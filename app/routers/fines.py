from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.fines import FineCreate, FineResponse
from app.utils.database import get_db_connection
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/fines/", response_model=FineResponse)
async def create_fine(fine: FineCreate, token: str = Depends(oauth2_scheme)):
    """
    Crea una nueva multa.

    Args:
        fine (FineCreate): Datos de la multa a crear.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles de la multa creada.

    Raises:
        HTTPException: Si ocurre algún error al crear la multa.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Crear la nueva multa
        query = """
            INSERT INTO fines (user_id, loan_id, amount, description, fine_date, paid)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, FALSE)
            RETURNING id, user_id, loan_id, amount, description, paid, fine_date
        """
        cursor.execute(query, (fine.user_id, fine.loan_id,
                       fine.amount, fine.description))
        conn.commit()

        new_fine = cursor.fetchone()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating fine: {str(e)}")

    return {
        "id": new_fine["id"],
        "user_id": new_fine["user_id"],
        "loan_id": new_fine["loan_id"],
        "amount": new_fine["amount"],
        "description": new_fine["description"],
        "paid": new_fine["paid"],
        "fine_date": new_fine["fine_date"],
        "message": "Fine created successfully"
    }


@router.get("/fines/{fine_id}/", response_model=FineResponse)
async def get_fine(fine_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene una multa basada en su ID.

    Args:
        fine_id (int): El ID de la multa a obtener.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles de la multa.

    Raises:
        HTTPException: Si la multa no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener la multa por su ID
    cursor.execute("SELECT * FROM fines WHERE id = %s", (fine_id,))
    fine = cursor.fetchone()

    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")

    return {
        "id": fine["id"],
        "user_id": fine["user_id"],
        "loan_id": fine["loan_id"],
        "amount": fine["amount"],
        "description": fine["description"],
        "paid": fine["paid"],
        "fine_date": fine["fine_date"],
        "message": "Fine retrieved successfully"
    }


@router.put("/fines/{fine_id}/pay", response_model=FineResponse)
async def pay_fine(fine_id: int, token: str = Depends(oauth2_scheme)):
    """
    Actualiza el estado de pago de una multa.

    Args:
        fine_id (int): El ID de la multa a actualizar.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles de la multa actualizada.

    Raises:
        HTTPException: Si la multa no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si la multa existe
    cursor.execute("SELECT * FROM fines WHERE id = %s", (fine_id,))
    existing_fine = cursor.fetchone()

    if not existing_fine:
        raise HTTPException(status_code=404, detail="Fine not found")

    # Actualizar el estado de pago de la multa
    query = """
        UPDATE fines 
        SET paid = TRUE 
        WHERE id = %s 
        RETURNING id, user_id, loan_id, amount, description, paid, fine_date
    """
    cursor.execute(query, (fine_id,))
    conn.commit()

    updated_fine = cursor.fetchone()

    return {
        "id": updated_fine["id"],
        "user_id": updated_fine["user_id"],
        "loan_id": updated_fine["loan_id"],
        "amount": updated_fine["amount"],
        "description": updated_fine["description"],
        "paid": updated_fine["paid"],
        "fine_date": updated_fine["fine_date"],
        "message": "Fine paid successfully"
    }

# Parámetros de la multa
INITIAL_FINE = 100  # Multa inicial después del período de gracia
DAILY_FINE = 10  # Multa diaria adicional por cada día después del período de gracia
GRACE_PERIOD_DAYS = 7  # Días de gracia sin multa


@router.get("/fines/", response_model=List[FineResponse])
async def list_fines(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), token: str = Depends(oauth2_scheme)):
    """
    Obtiene una lista de todas las multas con paginación y genera o recalcula automáticamente multas para préstamos vencidos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    current_date = datetime.utcnow()

    # Step 1: Find overdue loans that have not been returned
    cursor.execute("SELECT * FROM loans WHERE returned = FALSE")
    overdue_loans = cursor.fetchall()

    for loan in overdue_loans:
        loan_id = loan["id"]
        user_id = loan["user_id"]
        loan_date = loan["loan_date"]

        # Calculate total overdue days after the grace period
        overdue_days = (current_date - loan_date).days - GRACE_PERIOD_DAYS
        if overdue_days > 0:
            # Check if there's an existing unpaid fine for this loan
            cursor.execute(
                "SELECT * FROM fines WHERE loan_id = %s AND paid = FALSE ORDER BY fine_date DESC LIMIT 1",
                (loan_id,)
            )
            existing_fine = cursor.fetchone()

            total_fine_amount = INITIAL_FINE + (overdue_days * DAILY_FINE)
            description = f"Multa por exceso de días ({overdue_days} días excedidos)"

            if existing_fine:
                # Fine already exists, update it with the recalculated fine amount
                cursor.execute("""
                    UPDATE fines
                    SET amount = %s, description = %s, fine_date = %s
                    WHERE id = %s
                """, (total_fine_amount, description, current_date, existing_fine["id"]))
            else:
                # No previous fine, create an initial fine for the overdue period
                cursor.execute("""
                    INSERT INTO fines (user_id, loan_id, amount, description, paid, fine_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, loan_id, total_fine_amount, description, False, current_date))

    conn.commit()

    # Step 2: Retrieve all fines with pagination
    cursor.execute("SELECT * FROM fines LIMIT %s OFFSET %s",
                   (per_page, offset))
    fines = cursor.fetchall()

    if not fines:
        raise HTTPException(status_code=404, detail="No fines found")

    return [{
        "id": fine["id"],
        "user_id": fine["user_id"],
        "loan_id": fine["loan_id"],
        "amount": fine["amount"],
        "description": fine["description"],
        "paid": fine["paid"],
        "fine_date": fine["fine_date"]
    } for fine in fines]


@router.delete("/fines/{fine_id}/", status_code=200)
async def delete_fine(fine_id: int, token: str = Depends(oauth2_scheme)):
    """
    Elimina una multa basada en su ID.

    Args:
        fine_id (int): El ID de la multa a eliminar.
        token (str): El token JWT del usuario autenticado.

    Raises:
        HTTPException: Si la multa no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si la multa existe
    cursor.execute("SELECT * FROM fines WHERE id = %s", (fine_id,))
    existing_fine = cursor.fetchone()

    if not existing_fine:
        raise HTTPException(status_code=404, detail="Fine not found")

    # Eliminar la multa
    cursor.execute("DELETE FROM fines WHERE id = %s", (fine_id,))
    conn.commit()

    return {"message": "Fine deleted successfully"}


@router.get("/fines/user/{user_id}/", response_model=List[FineResponse])
async def get_user_fines(user_id: int, token: str = Depends(oauth2_scheme)):
    """
    Obtiene todas las multas de un usuario.

    Args:
        user_id (int): El ID del usuario.
        token (str): El token JWT del usuario autenticado.

    Returns:
        list: Una lista de todas las multas del usuario.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener todas las multas del usuario
    cursor.execute("SELECT * FROM get_user_fines(%s)", (user_id,))
    fines = cursor.fetchall()

    if not fines:
        raise HTTPException(
            status_code=404, detail="No fines found for the user")

    return [{
        "id": fine["id"],
        "user_id": fine["user_id"],
        "loan_id": fine["loan_id"],
        "amount": fine["amount"],
        "description": fine["description"],
        "paid": fine["paid"],
        "fine_date": fine["fine_date"]
    } for fine in fines]
