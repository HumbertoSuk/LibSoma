from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.books import BookCreate, BookUpdate, BookResponse
from app.utils.database import get_db_connection
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/books/", response_model=BookResponse)
async def create_book(book: BookCreate, token: str = Depends(oauth2_scheme)):
    """
    Crea un nuevo libro en la base de datos.

    Args:
        book (BookCreate): Datos del libro a crear.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del libro creado.

    Raises:
        HTTPException: Si ya existe un libro con el mismo ISBN.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el libro con el mismo ISBN ya existe
    cursor.execute("SELECT * FROM books WHERE isbn = %s", (book.isbn,))
    existing_book = cursor.fetchone()

    if existing_book:
        raise HTTPException(
            status_code=400, detail="Book with this ISBN already exists"
        )

    try:
        # Crear el nuevo libro
        query = """
            INSERT INTO books (title, author, category_id, isbn, copies_available)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, title, author, category_id, isbn, copies_available, created_at, updated_at
        """
        cursor.execute(query, (book.title, book.author,
                               book.category_id, book.isbn, book.copies_available))
        conn.commit()

        new_book = cursor.fetchone()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating book: {str(e)}")

    return {
        "id": new_book["id"],
        "title": new_book["title"],
        "author": new_book["author"],
        "category_id": new_book["category_id"],
        "isbn": new_book["isbn"],
        "copies_available": new_book["copies_available"],
        "created_at": new_book["created_at"],
        "updated_at": new_book["updated_at"],
        "message": "Book created successfully"
    }


@router.get("/books/{book_id}/", response_model=BookResponse)
async def get_book(book_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene los detalles de un libro basado en su ID.

    Args:
        book_id (int): El ID del libro a obtener.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del libro.

    Raises:
        HTTPException: Si el libro no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener el libro por su ID
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return {
        "id": book["id"],
        "title": book["title"],
        "author": book["author"],
        "category_id": book["category_id"],
        "isbn": book["isbn"],
        "copies_available": book["copies_available"],
        "created_at": book["created_at"],
        "updated_at": book["updated_at"],
        "message": "Book retrieved successfully"
    }


@router.get("/books/", response_model=List[BookResponse])
async def get_all_books(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), token: str = Depends(oauth2_scheme)):
    """
    Obtiene todos los libros de la base de datos con paginación.

    Args:
        page (int): Número de página (por defecto 1).
        per_page (int): Número de libros por página (por defecto 10, máximo 100).
        token (str): El token JWT del usuario autenticado.

    Returns:
        list: Una lista de libros.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    offset = (page - 1) * per_page

    # Obtener todos los libros con paginación
    cursor.execute("SELECT * FROM books LIMIT %s OFFSET %s",
                   (per_page, offset))
    books = cursor.fetchall()

    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    return [{
        "id": book["id"],
        "title": book["title"],
        "author": book["author"],
        "category_id": book["category_id"],
        "isbn": book["isbn"],
        "copies_available": book["copies_available"],
        "created_at": book["created_at"],
        "updated_at": book["updated_at"]
    } for book in books]


@router.put("/books/{book_id}/", response_model=BookResponse)
async def update_book(book_id: int, book: BookUpdate, token: str = Depends(oauth2_scheme)):
    """
    Actualiza los detalles de un libro basado en su ID.

    Args:
        book_id (int): El ID del libro a editar.
        book (BookUpdate): Los nuevos datos del libro (opcional).
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles actualizados del libro.

    Raises:
        HTTPException: Si el libro no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el libro existe
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    existing_book = cursor.fetchone()

    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
        # Actualizar los datos del libro
        query = """
            UPDATE books 
            SET title = COALESCE(%s, title), 
                author = COALESCE(%s, author), 
                category_id = COALESCE(%s, category_id), 
                isbn = COALESCE(%s, isbn), 
                copies_available = COALESCE(%s, copies_available), 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s 
            RETURNING id, title, author, category_id, isbn, copies_available, created_at, updated_at
        """
        cursor.execute(query, (book.title, book.author, book.category_id,
                               book.isbn, book.copies_available, book_id))
        conn.commit()

        updated_book = cursor.fetchone()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating book: {str(e)}")

    return {
        "id": updated_book["id"],
        "title": updated_book["title"],
        "author": updated_book["author"],
        "category_id": updated_book["category_id"],
        "isbn": updated_book["isbn"],
        "copies_available": updated_book["copies_available"],
        "created_at": updated_book["created_at"],
        "updated_at": updated_book["updated_at"],
        "message": "Book updated successfully"
    }


@router.delete("/books/{book_id}/", status_code=200)
async def delete_book(book_id: int, token: str = Depends(oauth2_scheme)):
    """
    Elimina un libro basado en su ID.

    Args:
        book_id (int): El ID del libro a eliminar.
        token (str): El token JWT del usuario autenticado.

    Raises:
        HTTPException: Si el libro no existe o si tiene préstamos o reservas activas.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el libro existe
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    existing_book = cursor.fetchone()

    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
        # Eliminar el libro
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting book: {str(e)}")

    return {"message": "Book deleted successfully"}


@router.get("/books/{book_id}/availability")
async def get_book_availability(book_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene la cantidad de copias disponibles de un libro.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT get_book_availability(%s)", (book_id,))
    available_copies = cursor.fetchone()

    if available_copies is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return {"book_id": book_id, "available_copies": available_copies[0]}


@router.put("/books/{book_id}/update")
async def update_book_info(book_id: int, title: str, author: str, category_id: int, isbn: str, token: str = Depends(oauth2_scheme)):
    """
    Actualiza la información de un libro.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT update_book_info(%s, %s, %s, %s, %s)",
                       (book_id, title, author, category_id, isbn))
        conn.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating book: {str(e)}")

    return {"message": "Book updated successfully"}
