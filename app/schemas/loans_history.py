"""Modelo Historial de prestamos"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoanHistoryCreate(BaseModel):
    """
    Esquema Pydantic para la creación de un historial de préstamo.

    Atributos:
        user_id (int): Identificador del usuario que realiza el préstamo.
        book_id (int): Identificador del libro prestado.
        loan_date (Optional[datetime]): Fecha en la que se realizó el préstamo.
        return_date (Optional[datetime]): Fecha en la que se devolvió el libro.
        returned (bool): Indica si el libro fue devuelto.
    """
    user_id: int
    book_id: int
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    returned: bool = False


class LoanHistoryResponse(BaseModel):
    """
    Esquema Pydantic para la respuesta del historial de un préstamo.

    Atributos:
        id (int): Identificador único del historial.
        user_id (int): Identificador del usuario que realizó el préstamo.
        book_id (int): Identificador del libro prestado.
        loan_date (datetime): Fecha en la que se realizó el préstamo.
        return_date (Optional[datetime]): Fecha en la que se devolvió el libro.
        returned (bool): Indica si el libro fue devuelto.
    """
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    return_date: Optional[datetime]
    returned: bool

    class Config:
        orm_mode = True  # Permitir que funcione con datos provenientes de la base de datos
