"""Rutas de los usuarios"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.schemas.user import UserCreate, UserResponse
from app.utils.auth import get_password_hash, verify_token
from app.utils.database import get_db_connection
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter()

# Esquema para autenticar a los usuarios con token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register/", response_model=UserResponse)
async def register_user(user: UserCreate):
    """
    Registra un nuevo usuario en la base de datos.

    Args:
        user (UserCreate): Datos del usuario, incluyendo username, password, email y role_id.

    Returns:
        dict: Un objeto JSON con los detalles del nuevo usuario (username, email, role_id).

    Raises:
        HTTPException: Si el nombre de usuario o correo electrónico ya están registrados,
                       o si el role_id proporcionado es inválido.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el usuario o email ya existen
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s",
                   (user.username, user.email))
    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Verificar si el role_id es válido
    cursor.execute("SELECT * FROM roles WHERE id = %s", (user.role_id,))
    role = cursor.fetchone()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id provided"
        )

    # Hashear la contraseña del usuario
    hashed_password = get_password_hash(user.password)

    # Insertar el nuevo usuario en la base de datos
    query = """
        INSERT INTO users (username, password, email, role_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id, username, email, role_id
    """
    cursor.execute(query, (user.username, hashed_password,
                   user.email, user.role_id))
    conn.commit()

    # Obtener los datos del nuevo usuario registrado
    new_user = cursor.fetchone()

    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "role_id": new_user["role_id"]
    }


@router.get("/users/me/")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    Obtiene los detalles del usuario autenticado basándose en el token JWT proporcionado.

    Args:
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles del usuario autenticado (username, email, role_id).

    Raises:
        HTTPException: Si el token no es válido o si el usuario no existe en la base de datos.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # Verificar el token JWT y obtener el nombre de usuario
    username = verify_token(token, credentials_exception)

    # Obtener los detalles del usuario desde la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "username": user["username"],
        "email": user["email"],
        "role_id": user["role_id"]
    }


@router.delete("/users/{user_id}/", status_code=200)
async def delete_user(user_id: int, token: str = Depends(oauth2_scheme)):
    """
    Elimina un usuario de la base de datos basado en su ID.

    Args:
        user_id (int): El ID del usuario a eliminar.
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un mensaje de confirmación si el usuario fue eliminado exitosamente.

    Raises:
        HTTPException: Si el usuario no existe o no está autorizado para eliminarlo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # Verificar el token JWT
    username = verify_token(token, credentials_exception)

    # Verificar si el usuario existe
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Eliminar el usuario
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()

    return {"message": f"User with ID {user_id} successfully deleted."}


@router.put("/users/{user_id}/", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate, token: str = Depends(oauth2_scheme)):
    """
    Edita los detalles de un usuario basado en su ID.

    Args:
        user_id (int): El ID del usuario a editar.
        user (UserCreate): Los nuevos datos del usuario (username, password, email, role_id).
        token (str): El token JWT del usuario autenticado.

    Returns:
        dict: Un objeto JSON con los detalles actualizados del usuario.

    Raises:
        HTTPException: Si el usuario no existe o los datos son inválidos.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # Verificar el token JWT
    username = verify_token(token, credentials_exception)

    # Verificar si el usuario existe
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verificar si el nuevo username o email ya están en uso por otro usuario
    cursor.execute("""
        SELECT * FROM users 
        WHERE (username = %s OR email = %s) AND id != %s
    """, (user.username, user.email, user_id))
    duplicate_user = cursor.fetchone()

    if duplicate_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already in use"
        )

    # Hashear la nueva contraseña
    hashed_password = get_password_hash(user.password)

    # Actualizar los datos del usuario
    query = """
        UPDATE users 
        SET username = %s, password = %s, email = %s, role_id = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s 
        RETURNING id, username, email, role_id
    """
    cursor.execute(query, (user.username, hashed_password,
                   user.email, user.role_id, user_id))
    conn.commit()

    updated_user = cursor.fetchone()

    return {
        "id": updated_user["id"],
        "username": updated_user["username"],
        "email": updated_user["email"],
        "role_id": updated_user["role_id"]
    }


@router.get("/users/", response_model=List[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    username: str = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtiene la lista de todos los usuarios con paginación y filtros.

    Args:
        page (int): Número de página.
        per_page (int): Cantidad de resultados por página (máximo 100).
        username (str, opcional): Filtro por nombre de usuario.

    Returns:
        list[UserResponse]: Una lista de usuarios con sus detalles, incluyendo el ID.

    Raises:
        HTTPException: Si no se puede validar el token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # Verificar el token JWT
    verify_token(token, credentials_exception)

    # Obtener la conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Filtro opcional por username
    query = "SELECT id, username, email, role_id FROM users WHERE TRUE"
    params = []

    if username:
        query += " AND username ILIKE %s"
        params.append(f"%{username}%")

    # Paginación
    offset = (page - 1) * per_page
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, tuple(params))
    users = cursor.fetchall()

    return [{"id": user["id"], "username": user["username"], "email": user["email"], "role_id": user["role_id"]} for user in users]
