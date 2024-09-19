import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Cargar la configuración de la base de datos desde variables de entorno
DB_USER = os.getenv("DATABASE_USER")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_NAME")

# Construir la URL de conexión a la base de datos
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_db_connection():
    """
    Crear y devolver una conexión a la base de datos PostgreSQL.

    Returns:
        psycopg2.extensions.connection: La conexión a la base de datos.
    Raises:
        HTTPException: Si ocurre un error al intentar conectarse a la base de datos.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        # Manejar errores de conexión a la base de datos y preservar la excepción original
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to the database: {str(e)}"
        ) from e
