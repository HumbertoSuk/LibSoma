"""endpoints de historiales de prestamos"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.loans_history import LoanHistoryCreate, LoanHistoryResponse
from app.utils.database import get_db_connection
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/loan-history/", response_model=LoanHistoryResponse)
async def create_loan_history(loan_history: LoanHistoryCreate, token: str = Depends(oauth2_scheme)):
    """
    Crea un nuevo historial de préstamo en la base de datos.

    Args:
        loan_history (LoanHistoryCreate): Datos del historial de préstamo a crear.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del historial de préstamo creado.

    Raises:
        HTTPException: Si hay algún error en la creación.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Crear el nuevo historial de préstamo
    query = """
        INSERT INTO loan_history (user_id, book_id, loan_date, return_date, returned)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, user_id, book_id, loan_date, return_date, returned
    """
    try:
        cursor.execute(query, (
            loan_history.user_id,
            loan_history.book_id,
            loan_history.loan_date,
            loan_history.return_date,
            loan_history.returned
        ))
        conn.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating loan history: {str(e)}")

    new_loan_history = cursor.fetchone()

    return {
        "id": new_loan_history["id"],
        "user_id": new_loan_history["user_id"],
        "book_id": new_loan_history["book_id"],
        "loan_date": new_loan_history["loan_date"],
        "return_date": new_loan_history["return_date"],
        "returned": new_loan_history["returned"],
        "message": "Loan history created successfully"
    }


@router.get("/loan-history/{loan_history_id}/", response_model=LoanHistoryResponse)
async def get_loan_history(loan_history_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene un historial de préstamo por su ID.

    Args:
        loan_history_id (int): El ID del historial de préstamo a obtener.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del historial de préstamo.

    Raises:
        HTTPException: Si el historial no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener el historial de préstamo por su ID
    cursor.execute("SELECT * FROM loan_history WHERE id = %s",
                   (loan_history_id,))
    loan_history = cursor.fetchone()

    if not loan_history:
        raise HTTPException(status_code=404, detail="Loan history not found")

    return {
        "id": loan_history["id"],
        "user_id": loan_history["user_id"],
        "book_id": loan_history["book_id"],
        "loan_date": loan_history["loan_date"],
        "return_date": loan_history["return_date"],
        "returned": loan_history["returned"],
        "message": "Loan history retrieved successfully"
    }


@router.get("/loan-history/", response_model=List[LoanHistoryResponse])
async def list_loan_histories(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    token: str = Depends(oauth2_scheme)
):
    """
    Obtiene una lista de todos los historiales de préstamos en la base de datos con paginación.

    Args:
        page (int): Número de página (por defecto 1).
        per_page (int): Cantidad de historiales por página (por defecto 10, máximo 100).
        token (str): El token JWT del usuario autenticado.

    Returns:
        list: Una lista de todos los historiales de préstamos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Calcular el desplazamiento para la paginación
    offset = (page - 1) * per_page

    # Obtener todos los historiales de préstamo con paginación
    cursor.execute(
        "SELECT * FROM loan_history LIMIT %s OFFSET %s", (per_page, offset))
    loan_histories = cursor.fetchall()

    if not loan_histories:
        raise HTTPException(status_code=404, detail="No loan histories found")

    return [{
        "id": loan_history["id"],
        "user_id": loan_history["user_id"],
        "book_id": loan_history["book_id"],
        "loan_date": loan_history["loan_date"],
        "return_date": loan_history["return_date"],
        "returned": loan_history["returned"]
    } for loan_history in loan_histories]
