"""Modelo de prestamos"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoanCreate(BaseModel):
    """
    Esquema Pydantic para la creación de un préstamo.

    Atributos:
        user_id (int): Identificador del usuario que realiza el préstamo.
        book_id (int): Identificador del libro que se presta.
    """
    user_id: int
    book_id: int


class LoanResponse(BaseModel):
    """
    Esquema Pydantic para la respuesta de un préstamo.

    Atributos:
        id (int): Identificador único del préstamo.
        user_id (int): Identificador del usuario que realiza el préstamo.
        book_id (int): Identificador del libro que se presta.
        loan_date (datetime): Fecha en la que se realizó el préstamo.
        return_date (Optional[datetime]): Fecha en la que se devuelve el libro. Puede ser nulo si no se ha devuelto.
        returned (bool): Indica si el libro ha sido devuelto.
    """
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    return_date: Optional[datetime]
    returned: bool

    class Config:
        # Esto permite trabajar con datos de la base de datos como objetos de Pydantic
        orm_mode = True
