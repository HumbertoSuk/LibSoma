"""Modelos para token de autenticación"""
from pydantic import BaseModel


class Token(BaseModel):
    """
    Modelo que representa un token de acceso.

    Atributos:
        access_token (str): El token de acceso JWT.
        token_type (str): El tipo de token, normalmente 'bearer'.
    """

    access_token: str
    token_type: str
