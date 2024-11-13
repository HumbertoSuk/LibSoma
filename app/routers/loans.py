"""endpoints para los préstamos"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.loans import LoanCreate, LoanResponse
from app.utils.database import get_db_connection
from fastapi.security import OAuth2PasswordBearer
from typing import List
from datetime import datetime

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/loans/", response_model=LoanResponse)
async def create_loan(loan: LoanCreate, token: str = Depends(oauth2_scheme)):
    """
    Creates a new loan if copies are available and the user doesn't already have an active loan for the book.
    Updates the stock count of available copies for the book.

    Args:
        loan (LoanCreate): Loan data (user and book).
        token (str): The JWT token of the authenticated user.

    Returns:
        dict: A JSON object with details of the created loan.

    Raises:
        HTTPException: If the user already has an active loan for the book or if no copies are available.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if there are copies available
        cursor.execute(
            "SELECT copies_available FROM books WHERE id = %s", (loan.book_id,))
        book = cursor.fetchone()

        if not book or book["copies_available"] <= 0:
            raise HTTPException(
                status_code=400, detail="No copies available for this book.")

        # Check if the user already has an active loan for this book
        cursor.execute(
            "SELECT * FROM loans WHERE book_id = %s AND user_id = %s AND returned = FALSE",
            (loan.book_id, loan.user_id))
        user_existing_loan = cursor.fetchone()

        if user_existing_loan:
            raise HTTPException(
                status_code=400, detail="You already have an active loan for this book.")

        # Create the new loan and update the number of available copies
        cursor.execute("""
            INSERT INTO loans (user_id, book_id)
            VALUES (%s, %s)
            RETURNING id, user_id, book_id, loan_date, return_date, returned
        """, (loan.user_id, loan.book_id))
        new_loan = cursor.fetchone()

        cursor.execute(
            "UPDATE books SET copies_available = copies_available - 1 WHERE id = %s", (loan.book_id,))
        conn.commit()

        return {
            "id": new_loan["id"],
            "user_id": new_loan["user_id"],
            "book_id": new_loan["book_id"],
            "loan_date": new_loan["loan_date"],
            "return_date": new_loan["return_date"],
            "returned": new_loan["returned"],
            "message": "Loan created successfully, and the number of available copies updated."
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/loans/{loan_id}/return", response_model=LoanResponse)
async def return_book(loan_id: int, token: str = Depends(oauth2_scheme)):
    """
    Marca un préstamo como devuelto, actualiza la fecha de devolución y suma una copia disponible.

    Args:
        loan_id (int): El ID del préstamo a marcar como devuelto.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del préstamo actualizado.

    Raises:
        HTTPException: Si el préstamo no existe o ya ha sido devuelto.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el préstamo existe
        cursor.execute("SELECT * FROM loans WHERE id = %s", (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            raise HTTPException(
                status_code=404, detail="Préstamo no encontrado")

        if loan["returned"]:
            raise HTTPException(
                status_code=400, detail="Este préstamo ya ha sido devuelto.")

        # Marcar el préstamo como devuelto, actualizar la fecha de devolución y aumentar copias
        cursor.execute("""
            UPDATE loans
            SET returned = TRUE, return_date = %s
            WHERE id = %s
            RETURNING id, user_id, book_id, loan_date, return_date, returned
        """, (datetime.utcnow(), loan_id))
        updated_loan = cursor.fetchone()

        cursor.execute(
            "UPDATE books SET copies_available = copies_available + 1 WHERE id = %s", (loan["book_id"],))
        conn.commit()

        return {
            "id": updated_loan["id"],
            "user_id": updated_loan["user_id"],
            "book_id": updated_loan["book_id"],
            "loan_date": updated_loan["loan_date"],
            "return_date": updated_loan["return_date"],
            "returned": updated_loan["returned"],
            "message": "Libro devuelto y copias actualizadas correctamente"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/loans/", response_model=List[LoanResponse])
async def get_all_loans(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    token: str = Depends(oauth2_scheme)
):
    """
    Obtiene todos los préstamos con paginación opcional.

    Args:
        page (int): Número de página (por defecto 1).
        per_page (int): Número de préstamos por página (por defecto 10, máximo 100).

    Returns:
        list[LoanResponse]: Una lista de todos los préstamos con paginación.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Calcular el desplazamiento para la paginación
    offset = (page - 1) * per_page

    # Obtener préstamos con paginación
    cursor.execute("SELECT * FROM loans LIMIT %s OFFSET %s",
                   (per_page, offset))
    loans = cursor.fetchall()

    return [{
        "id": loan["id"],
        "user_id": loan["user_id"],
        "book_id": loan["book_id"],
        "loan_date": loan["loan_date"],
        "return_date": loan["return_date"],
        "returned": loan["returned"]
    } for loan in loans]


@router.get("/loans/{loan_id}/", response_model=LoanResponse)
async def get_loan(loan_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene un préstamo por su ID.

    Args:
        loan_id (int): El ID del préstamo a obtener.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del préstamo.

    Raises:
        HTTPException: Si el préstamo no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener el préstamo por su ID
    cursor.execute("SELECT * FROM loans WHERE id = %s", (loan_id,))
    loan = cursor.fetchone()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    return {
        "id": loan["id"],
        "user_id": loan["user_id"],
        "book_id": loan["book_id"],
        "loan_date": loan["loan_date"],
        "return_date": loan["return_date"],
        "returned": loan["returned"],
        "message": "Loan retrieved successfully"
    }


@router.delete("/loans/{loan_id}/", status_code=200)
async def delete_loan(loan_id: int, token: str = Depends(oauth2_scheme)):
    """
    Elimina un préstamo basado en su ID.

    Args:
        loan_id (int): El ID del préstamo a eliminar.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un mensaje de confirmación si el préstamo fue eliminado.

    Raises:
        HTTPException: Si el préstamo no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el préstamo existe
    cursor.execute("SELECT * FROM loans WHERE id = %s", (loan_id,))
    loan = cursor.fetchone()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    # Eliminar el préstamo
    cursor.execute("DELETE FROM loans WHERE id = %s", (loan_id,))
    conn.commit()

    return {"message": "Loan deleted successfully"}


@router.get("/loans/{loan_id}/late_fee")
async def calculate_late_fee(loan_id: int, token: str = Depends(oauth2_scheme)):
    """
    Calcula la multa por retraso en la devolución de un préstamo.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT calculate_late_fee(%s)", (loan_id,))
    fee = cursor.fetchone()

    if fee is None:
        raise HTTPException(
            status_code=404, detail="Loan not found or no late fee applicable"
        )

    return {"loan_id": loan_id, "late_fee": fee[0]}
