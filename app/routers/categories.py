from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.category import CategoryCreate, CategoryResponse
from app.utils.database import get_db_connection
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/categories/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, token: str = Depends(oauth2_scheme)):
    """
    Crea una nueva categoría en la base de datos.

    Args:
        category (CategoryCreate): Datos de la categoría a crear.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles de la categoría creada.

    Raises:
        HTTPException: Si ya existe una categoría con el mismo nombre.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si la categoría ya existe
    cursor.execute("SELECT * FROM categories WHERE name = %s",
                   (category.name,))
    existing_category = cursor.fetchone()

    if existing_category:
        raise HTTPException(
            status_code=400, detail="Category with this name already exists"
        )

    try:
        # Crear la nueva categoría
        query = """
            INSERT INTO categories (name)
            VALUES (%s)
            RETURNING id, name
        """
        cursor.execute(query, (category.name,))
        conn.commit()

        new_category = cursor.fetchone()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating category: {str(e)}")

    return {"id": new_category["id"], "name": new_category["name"], "message": "Category created successfully"}


@router.get("/categories/{category_id}/", response_model=CategoryResponse)
async def get_category(category_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene una categoría basada en su ID.

    Args:
        category_id (int): El ID de la categoría a obtener.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles de la categoría.

    Raises:
        HTTPException: Si la categoría no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener la categoría por su ID
    cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
    category = cursor.fetchone()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"id": category["id"], "name": category["name"], "message": "Category retrieved successfully"}


@router.get("/categories/", response_model=List[CategoryResponse])
async def get_all_categories(page: int = Query(1, ge=1), per_page: int = Query(40, ge=1, le=100), token: str = Depends(oauth2_scheme)):
    """
    Obtiene todas las categorías en la base de datos con paginación.

    Args:
        page (int): Número de página (por defecto 1).
        per_page (int): Número de categorías por página (por defecto 10, máximo 100).
        token (str): El token JWT del usuario autenticado.

    Returns:
        list[CategoryResponse]: Una lista de todas las categorías.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    offset = (page - 1) * per_page

    # Obtener todas las categorías con paginación
    cursor.execute("SELECT * FROM categories LIMIT %s OFFSET %s",
                   (per_page, offset))
    categories = cursor.fetchall()

    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")

    return [{"id": category["id"], "name": category["name"]} for category in categories]


@router.put("/categories/{category_id}/", response_model=CategoryResponse)
async def update_category(category_id: int, category: CategoryCreate, token: str = Depends(oauth2_scheme)):
    """
    Actualiza los detalles de una categoría basada en su ID.

    Args:
        category_id (int): El ID de la categoría a editar.
        category (CategoryCreate): Los nuevos datos de la categoría.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles actualizados de la categoría.

    Raises:
        HTTPException: Si la categoría no existe o si el nombre ya está en uso.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si la categoría existe
    cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
    existing_category = cursor.fetchone()

    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Verificar si el nuevo nombre ya está en uso por otra categoría
    cursor.execute("SELECT * FROM categories WHERE name = %s AND id != %s",
                   (category.name, category_id))
    duplicate_category = cursor.fetchone()

    if duplicate_category:
        raise HTTPException(
            status_code=400, detail="Category with this name already exists")

    try:
        # Actualizar la categoría
        query = """
            UPDATE categories 
            SET name = %s 
            WHERE id = %s 
            RETURNING id, name
        """
        cursor.execute(query, (category.name, category_id))
        conn.commit()

        updated_category = cursor.fetchone()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating category: {str(e)}")

    return {"id": updated_category["id"], "name": updated_category["name"], "message": "Category updated successfully"}


@router.delete("/categories/{category_id}/", status_code=200)
async def delete_category(category_id: int, token: str = Depends(oauth2_scheme)):
    """
    Elimina una categoría basada en su ID.

    Args:
        category_id (int): El ID de la categoría a eliminar.
        token (str): El token JWT del usuario autenticado.

    Raises:
        HTTPException: Si la categoría no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si la categoría existe
    cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
    existing_category = cursor.fetchone()

    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        # Eliminar la categoría
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        conn.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting category: {str(e)}")

    return {"message": "Category deleted successfully"}
