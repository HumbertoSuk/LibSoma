"""Autenticación"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.auth import Token
from app.schemas.invalidated_token import InvalidatedToken
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
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Buscar el usuario en la base de datos, incluyendo el id de rol
        query = "SELECT id, username, password, role_id FROM users WHERE username = %s"
        cursor.execute(query, (form_data.username,))
        user = cursor.fetchone()

        # Validar existencia y contraseña
        if not user or not verify_password(form_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generar el token JWT
        access_token_expires = timedelta(minutes=360)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )

        # Incluir el user_id y role_id en la respuesta
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["id"],      # ID del usuario
            "role_id": user["role_id"]  # ID del rol del usuario
        }

    finally:
        cursor.close()
        conn.close()


@router.post("/logout/")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Invalida el token actual y lo almacena en la tabla de tokens invalidos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO invalidated_tokens (token) VALUES (%s)"
        cursor.execute(query, (token,))
        conn.commit()

        return {"message": "Logout successful, token invalidated"}
    finally:
        cursor.close()
        conn.close()


def is_token_invalidated(token: str) -> bool:
    """
    Verifica si el token está en la lista negra (invalidado).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT * FROM invalidated_tokens WHERE token = %s"
        cursor.execute(query, (token,))
        result = cursor.fetchone()
        return result is not None
    finally:
        cursor.close()
        conn.close()


@router.get("/some_protected_route/")
async def protected_route(token: str = Depends(oauth2_scheme)):
    """
    Ruta protegida que verifica si el token ha sido invalidado.
    """
    if is_token_invalidated(token):
        raise HTTPException(
            status_code=401, detail="Token has been invalidated")

    return {"message": "Access granted"}
