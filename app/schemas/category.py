"""Categorias de libros."""
from pydantic import BaseModel


class CategoryBase(BaseModel):
    """
    Esquema base para representar una categoría de libros.

    Atributos:
        name (str): El nombre único de la categoría.
    """
    name: str


class CategoryCreate(CategoryBase):
    """
    Esquema para crear una nueva categoría.

    Hereda el atributo name de CategoryBase.
    """
    pass


class CategoryResponse(BaseModel):
    """
    Esquema de respuesta para una categoría.

    Atributos:
        id (int): El identificador único de la categoría.
        name (str): El nombre único de la categoría.
    """
    id: int
    name: str
