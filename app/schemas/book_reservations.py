"""Modelo de reservaciones de libros"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BookReservationCreate(BaseModel):
    """
    Esquema Pydantic para la creación de una reserva de libro.

    Atributos:
        user_id (int): Identificador del usuario que realiza la reserva.
        book_id (int): Identificador del libro reservado.
    """
    user_id: int
    book_id: int


class BookReservationResponse(BaseModel):
    """
    Esquema Pydantic para la respuesta de una reserva de libro.

    Atributos:
        id (int): Identificador único de la reserva.
        user_id (int): Identificador del usuario que realizó la reserva.
        book_id (int): Identificador del libro reservado.
        reservation_date (datetime): Fecha en la que se realizó la reserva.
        active (bool): Estado de la reserva (activa o inactiva).
    """
    id: int
    user_id: int
    book_id: int
    reservation_date: datetime
    active: bool

    class Config:
        orm_mode = True  # Permitir que funcione con datos provenientes de la base de datos
