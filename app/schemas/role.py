"""Modelo de rol"""
from pydantic import BaseModel


class RoleBase(BaseModel):
    """
    Esquema base para representar un rol en el sistema.

    Atributos:
        name (str): El nombre único del rol.
    """
    name: str


class RoleCreate(RoleBase):
    """
    Esquema para crear un nuevo rol.

    Hereda el atributo name de RoleBase.
    """
    pass


class RoleResponse(BaseModel):
    """
    Esquema de respuesta para un rol.

    Atributos:
        id (int): El identificador único del rol.
        name (str): El nombre único del rol.
    """
    id: int
    name: str
