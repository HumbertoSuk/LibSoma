from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Clave secreta para firmar los tokens (debería almacenarse en variables de entorno)
SECRET_KEY = os.getenv("SECRET_KEY", "secret_jwt_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hasher de contraseñas usando bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con una contraseña hash.

    Args:
        plain_password (str): La contraseña en texto plano proporcionada por el usuario.
        hashed_password (str): La contraseña hasheada almacenada en la base de datos.

    Returns:
        bool: True si la contraseña coincide, de lo contrario False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña utilizando bcrypt.

    Args:
        password (str): La contraseña en texto plano.

    Returns:
        str: La contraseña hasheada.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crea un token JWT para la autenticación.

    Args:
        data (dict): Los datos que se incluirán en el token (por ejemplo, el nombre de usuario).
        expires_delta (timedelta, optional): Tiempo adicional antes de que el token expire. 
            Si no se proporciona, el token expirará en 15 minutos.

    Returns:
        str: El token JWT firmado.
    """
    to_encode = data.copy()
    if expires_delta:
        # Utiliza timezone-aware datetime
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + \
            timedelta(minutes=15)  # Expiración por defecto
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """
    Verifica la validez de un token JWT. Decodifica el token y extrae el nombre de usuario.

    Args:
        token (str): El token JWT proporcionado por el cliente.
        credentials_exception: La excepción a levantar si la verificación falla.

    Returns:
        str: El nombre de usuario (sub) contenido en el token, si es válido.

    Raises:
        HTTPException: Si el token es inválido o ha expirado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
