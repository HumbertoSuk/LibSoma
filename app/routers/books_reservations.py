from fastapi import APIRouter, Depends, HTTPException
from app.schemas.book_reservations import BookReservationCreate, BookReservationResponse
from app.utils.database import get_db_connection
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/book-reservations/", response_model=BookReservationResponse)
async def create_book_reservation(reservation: BookReservationCreate, token: str = Depends(oauth2_scheme)):
    """
    Crea una nueva reserva de libro.

    Args:
        reservation (BookReservationCreate): Datos de la reserva a crear.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles de la reserva creada.

    Raises:
        HTTPException: Si la reserva no puede ser creada.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Crear la nueva reserva de libro
    query = """
        INSERT INTO book_reservations (user_id, book_id, reservation_date, active)
        VALUES (%s, %s, CURRENT_TIMESTAMP, TRUE)
        RETURNING id, user_id, book_id, reservation_date, active
    """
    cursor.execute(query, (reservation.user_id, reservation.book_id))
    conn.commit()

    new_reservation = cursor.fetchone()

    return {
        "id": new_reservation["id"],
        "user_id": new_reservation["user_id"],
        "book_id": new_reservation["book_id"],
        "reservation_date": new_reservation["reservation_date"],
        "active": new_reservation["active"],
        "message": "Book reservation created successfully"
    }


@router.get("/book-reservations/{reservation_id}/", response_model=BookReservationResponse)
async def get_book_reservation(reservation_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene una reserva de libro basada en su ID.

    Args:
        reservation_id (int): El ID de la reserva a obtener.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles de la reserva.

    Raises:
        HTTPException: Si la reserva no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener la reserva por su ID
    cursor.execute(
        "SELECT * FROM book_reservations WHERE id = %s", (reservation_id,))
    reservation = cursor.fetchone()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return {
        "id": reservation["id"],
        "user_id": reservation["user_id"],
        "book_id": reservation["book_id"],
        "reservation_date": reservation["reservation_date"],
        "active": reservation["active"],
        "message": "Book reservation retrieved successfully"
    }


@router.put("/book-reservations/{reservation_id}/", response_model=BookReservationResponse)
async def update_book_reservation(reservation_id: int, reservation: BookReservationCreate, token: str = Depends(oauth2_scheme)):
    """
    Actualiza una reserva de libro basada en su ID.

    Args:
        reservation_id (int): El ID de la reserva a editar.
        reservation (BookReservationCreate): Los nuevos datos de la reserva.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles actualizados de la reserva.

    Raises:
        HTTPException: Si la reserva no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si la reserva existe
    cursor.execute(
        "SELECT * FROM book_reservations WHERE id = %s", (reservation_id,))
    existing_reservation = cursor.fetchone()

    if not existing_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Actualizar la reserva de libro
    query = """
        UPDATE book_reservations 
        SET user_id = %s, book_id = %s, reservation_date = CURRENT_TIMESTAMP
        WHERE id = %s 
        RETURNING id, user_id, book_id, reservation_date, active
    """
    cursor.execute(query, (reservation.user_id,
                   reservation.book_id, reservation_id))
    conn.commit()

    updated_reservation = cursor.fetchone()

    return {
        "id": updated_reservation["id"],
        "user_id": updated_reservation["user_id"],
        "book_id": updated_reservation["book_id"],
        "reservation_date": updated_reservation["reservation_date"],
        "active": updated_reservation["active"],
        "message": "Book reservation updated successfully"
    }


@router.get("/book-reservations/", response_model=List[BookReservationResponse])
async def list_book_reservations(token: str = Depends(oauth2_scheme)):
    """
    Obtiene una lista de todas las reservas de libros en la base de datos.

    Args:
        token (str): El token JWT del usuario autenticado.

    Returns:
        list: Una lista de todas las reservas de libros.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener todas las reservas de libros
    cursor.execute("SELECT * FROM book_reservations")
    reservations = cursor.fetchall()

    return [{
        "id": reservation["id"],
        "user_id": reservation["user_id"],
        "book_id": reservation["book_id"],
        "reservation_date": reservation["reservation_date"],
        "active": reservation["active"]
    } for reservation in reservations]


@router.delete("/book-reservations/{reservation_id}/", status_code=204)
async def delete_book_reservation(reservation_id: int, token: str = Depends(oauth2_scheme)):
    """
    Elimina una reserva de libro basada en su ID.

    Args:
        reservation_id (int): El ID de la reserva a eliminar.
        token (str): El token JWT del usuario autenticado.

    Raises:
        HTTPException: Si la reserva no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si la reserva existe
    cursor.execute(
        "SELECT * FROM book_reservations WHERE id = %s", (reservation_id,))
    existing_reservation = cursor.fetchone()

    if not existing_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Eliminar la reserva de libro
    cursor.execute("DELETE FROM book_reservations WHERE id = %s",
                   (reservation_id,))
    conn.commit()

    return {"message": "Book reservation deleted successfully"}


@router.post("/reservations/")
async def reserve_book(user_id: int, book_id: int, token: str = Depends(oauth2_scheme)):
    """
    Realiza una reserva de un libro si hay copias disponibles.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT reserve_book(%s, %s)", (user_id, book_id))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Book reserved successfully."}


@router.get("/reservations/user/{user_id}")
async def get_user_reservations(user_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene todas las reservas activas de un usuario.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM book_reservations WHERE user_id = %s AND active = TRUE", (user_id,))
    reservations = cursor.fetchall()

    return [{"id": reservation["id"], "book_id": reservation["book_id"], "reservation_date": reservation["reservation_date"], "active": reservation["active"]} for reservation in reservations]
