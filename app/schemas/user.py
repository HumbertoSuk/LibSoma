"""Modelos para usuarios"""
from pydantic import BaseModel


class UserCreate(BaseModel):
    """
    Modelo que representa los datos requeridos para crear un nuevo usuario.

    Atributos:
        username (str): El nombre de usuario único.
        password (str): La contraseña en texto plano (que será hasheada).
        email (str): La dirección de correo electrónico única del usuario.
        role_id (int): El ID del rol asignado al usuario.
    """

    username: str
    password: str
    email: str
    role_id: int


class UserResponse(BaseModel):
    """
    Modelo de respuesta para devolver los datos de un usuario.

    Atributos:
        id (int): El ID único del usuario.
        username (str): El nombre de usuario.
        email (str): La dirección de correo electrónico del usuario.
        role_id (int): El ID del rol asignado al usuario.
    """
    id: int
    username: str
    email: str
    role_id: int
