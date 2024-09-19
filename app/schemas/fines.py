"""Modelo de multas"""
from pydantic import BaseModel, condecimal
from typing import Optional
from datetime import datetime


class FineCreate(BaseModel):
    """
    Esquema Pydantic para la creación de una multa.

    Atributos:
        user_id (int): Identificador del usuario al que se le asigna la multa.
        loan_id (int): Identificador del préstamo asociado a la multa.
        amount (Decimal): Monto de la multa.
        description (str): Descripción de la multa.
    """
    user_id: int
    loan_id: int
    amount: condecimal(max_digits=10, decimal_places=2)
    description: str


class FineResponse(BaseModel):
    """
    Esquema Pydantic para la respuesta de una multa.

    Atributos:
        id (int): Identificador único de la multa.
        user_id (int): Identificador del usuario al que se le asigna la multa.
        loan_id (int): Identificador del préstamo asociado a la multa.
        amount (Decimal): Monto de la multa.
        description (str): Descripción de la multa.
        paid (bool): Estado del pago de la multa.
        fine_date (datetime): Fecha en la que se registró la multa.
    """
    id: int
    user_id: int
    loan_id: int
    amount: condecimal(max_digits=10, decimal_places=2)
    description: str
    paid: bool
    fine_date: datetime

    class Config:
        orm_mode = True  # Permitir que funcione con datos provenientes de la base de datos
