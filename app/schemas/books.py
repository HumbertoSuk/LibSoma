"""Modelo de libros."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BookBase(BaseModel):
    """
    Esquema base para representar un libro.

    Atributos:
        title (str): El título del libro.
        author (str): El autor del libro.
        category_id (Optional[int]): El ID de la categoría a la que pertenece el libro.
        isbn (str): El ISBN único del libro.
        copies_available (int): Número de copias disponibles.
    """
    title: str
    author: str
    category_id: Optional[int] = None
    isbn: str
    copies_available: int = 1


class BookCreate(BookBase):
    """
    Esquema para crear un nuevo libro.

    Hereda todos los atributos de BookBase.
    """
    pass


class BookUpdate(BaseModel):
    """
    Esquema para actualizar la información de un libro.

    Atributos:
        title (Optional[str]): El nuevo título del libro (opcional).
        author (Optional[str]): El nuevo autor del libro (opcional).
        category_id (Optional[int]): El nuevo ID de la categoría del libro (opcional).
        isbn (Optional[str]): El nuevo ISBN del libro (opcional).
        copies_available (Optional[int]): El nuevo número de copias disponibles (opcional).
    """
    title: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[int] = None
    isbn: Optional[str] = None
    copies_available: Optional[int] = None


class BookResponse(BaseModel):
    """
    Esquema de respuesta para un libro.

    Atributos:
        id (int): El ID del libro.
        title (str): El título del libro.
        author (str): El autor del libro.
        category_id (int): El ID de la categoría a la que pertenece el libro.
        isbn (str): El ISBN único del libro.
        copies_available (int): El número de copias disponibles.
        created_at (datetime): La fecha de creación del libro.
        updated_at (datetime): La fecha de la última actualización del libro.
    """
    id: int
    title: str
    author: str
    category_id: int
    isbn: str
    copies_available: int
    created_at: datetime
    updated_at: datetime
