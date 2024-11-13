from pydantic import BaseModel


class Token(BaseModel):
    """
    Modelo que representa un token de acceso.

    Atributos:
        access_token (str): El token de acceso JWT.
        token_type (str): El tipo de token, normalmente 'bearer'.
        user_id (int): El ID del usuario autenticado.
    """
    access_token: str
    token_type: str
    user_id: int  # Agregar el campo user_id
    role_id: int  # Agregar role_id
