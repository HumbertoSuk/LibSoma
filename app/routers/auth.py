"""Autenticación"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.auth import Token
from app.utils.database import get_db_connection
from app.utils.auth import create_access_token, verify_password
from datetime import timedelta

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica al usuario y genera un token de acceso JWT.

    Args:
        form_data (OAuth2PasswordRequestForm): Datos de entrada 'username' y 'password'.

    Returns:
        dict: Contiene el 'access_token' generado y el 'token_type'.

    Raises:
        HTTPException: Si el nombre de usuario o la contraseña son incorrectos.
    """
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required."
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    # Prevenir inyección de SQL con placeholders seguros
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (form_data.username,))
    user = cursor.fetchone()

    # Validación de existencia del usuario y la contraseña
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generar un token de acceso con un tiempo de expiración
    access_token_expires = timedelta(minutes=360)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
