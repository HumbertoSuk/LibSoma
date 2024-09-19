"""endpoints de roles"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.role import RoleCreate, RoleResponse
from app.utils.database import get_db_connection
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/roles/", response_model=RoleResponse)
async def create_role(role: RoleCreate, token: str = Depends(oauth2_scheme)):
    """
    Crea un nuevo rol en la base de datos.

    Args:
        role (RoleCreate): Datos del rol a crear.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del rol creado.

    Raises:
        HTTPException: Si ya existe un rol con el mismo nombre.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el rol ya existe
    cursor.execute("SELECT * FROM roles WHERE name = %s", (role.name,))
    existing_role = cursor.fetchone()

    if existing_role:
        raise HTTPException(
            status_code=400, detail="Role with this name already exists"
        )

    # Crear el nuevo rol
    query = """
        INSERT INTO roles (name)
        VALUES (%s)
        RETURNING id, name
    """
    cursor.execute(query, (role.name,))
    conn.commit()

    new_role = cursor.fetchone()

    return {
        "id": new_role["id"],
        "name": new_role["name"],
        "message": "Role created successfully"
    }


@router.get("/roles/{role_id}/", response_model=RoleResponse)
async def get_role(role_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene un rol basado en su ID.

    Args:
        role_id (int): El ID del rol a obtener.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del rol.

    Raises:
        HTTPException: Si el rol no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener el rol por su ID
    cursor.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
    role = cursor.fetchone()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return {
        "id": role["id"],
        "name": role["name"],
        "message": "Role retrieved successfully"
    }


@router.put("/roles/{role_id}/", response_model=RoleResponse)
async def update_role(role_id: int, role: RoleCreate, token: str = Depends(oauth2_scheme)):
    """
    Actualiza los detalles de un rol basado en su ID.

    Args:
        role_id (int): El ID del rol a editar.
        role (RoleCreate): Los nuevos datos del rol.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles actualizados del rol.

    Raises:
        HTTPException: Si el rol no existe o si el nombre ya está en uso.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el rol existe
    cursor.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
    existing_role = cursor.fetchone()

    if not existing_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Verificar si el nuevo nombre ya está en uso por otro rol
    cursor.execute(
        "SELECT * FROM roles WHERE name = %s AND id != %s", (role.name, role_id))
    duplicate_role = cursor.fetchone()

    if duplicate_role:
        raise HTTPException(
            status_code=400, detail="Role with this name already exists")

    # Actualizar el rol
    query = """
        UPDATE roles 
        SET name = %s 
        WHERE id = %s 
        RETURNING id, name
    """
    cursor.execute(query, (role.name, role_id))
    conn.commit()

    updated_role = cursor.fetchone()

    return {
        "id": updated_role["id"],
        "name": updated_role["name"],
        "message": "Role updated successfully"
    }


@router.delete("/roles/{role_id}/", status_code=200)
async def delete_role(role_id: int, token: str = Depends(oauth2_scheme)):
    """
    Elimina un rol basado en su ID.

    Args:
        role_id (int): El ID del rol a eliminar.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un mensaje de confirmación si el rol fue eliminado.

    Raises:
        HTTPException: Si el rol no existe o si está relacionado con algún usuario.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el rol existe
    cursor.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
    existing_role = cursor.fetchone()

    if not existing_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Verificar si el rol está relacionado con algún usuario
    cursor.execute("SELECT * FROM users WHERE role_id = %s", (role_id,))
    related_user = cursor.fetchone()

    if related_user:
        raise HTTPException(
            status_code=400, detail="Cannot delete role: role is assigned to a user"
        )

    # Eliminar el rol
    cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
    conn.commit()

    return {"message": "Role deleted successfully"}


@router.get("/roles/", response_model=List[RoleResponse])
async def get_all_roles(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    token: str = Depends(oauth2_scheme)
):
    """
    Obtiene todos los roles con paginación opcional.

    Args:
        page (int): Número de página (por defecto 1).
        per_page (int): Número de roles por página (por defecto 10, máximo 100).

    Returns:
        list[RoleResponse]: Una lista de todos los roles con paginación.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Calcular el desplazamiento para la paginación
    offset = (page - 1) * per_page

    # Obtener roles con paginación
    cursor.execute("SELECT * FROM roles LIMIT %s OFFSET %s",
                   (per_page, offset))
    roles = cursor.fetchall()

    return [{"id": role["id"], "name": role["name"]} for role in roles]
