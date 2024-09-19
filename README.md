# Sistema de Gestión de Biblioteca

Este es un sistema de gestión de bibliotecas basado en FastAPI que incluye autenticación, gestión de roles, reservas de libros, préstamos, multas y otras funcionalidades.

## Características

- **Autenticación**: Registro, inicio de sesión con JWT.
- **Gestión de Usuarios y Roles**.
- **CRUD de Libros y Categorías**.
- **Reservas de Libros y Préstamos**.
- **Gestión de Multas por Retraso**.
- **Documentación interactiva de la API**: Swagger y ReDoc.

## Tecnologías Usadas

- **FastAPI**
- **PostgreSQL**
- **JWT para autenticación**
- **Docker y Docker Compose**
- **bcrypt** para hash de contraseñas.

## Instalación

### Requisitos Previos

- **Docker** y **Docker Compose**
- **Python 3.9+**

### Configuración

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/library-management-system.git
   cd library-management-system

   ```

2. Crea un archivo .env con las variables de entorno necesarias:

   ```bash
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=tucontraseña
   POSTGRES_DB=library_db
   SECRET_KEY=tu_clave_secreta
   ```

3. Crea un archivo .env con las variables de entorno necesarias:
   ```bash
   docker-compose up --build
   ```
4. Si prefieres correr localmente:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

### Accede a la documentación de la API interactiva:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Pgadmin** http://localhost:5050/

## Acceder y Configurar PgAdmin

**PgAdmin** es una herramienta gráfica para gestionar bases de datos PostgreSQL. Puedes acceder a PgAdmin en [http://localhost:5050](http://localhost:5050).

### Configuración de PgAdmin

Sigue los siguientes pasos para configurar y conectarte a la base de datos PostgreSQL:

### 1. Acceder a PgAdmin

- Abre tu navegador y ve a: [http://localhost:5050](http://localhost:5050).
- Introduce las credenciales para acceder (definidas en tu archivo `.env` o por defecto):

  - **Email**: `pgadmin4@pgadmin.org`
  - **Contraseña**: `admin`

### 2. Agregar un Servidor en PgAdmin

1. En el panel de PgAdmin, haz clic derecho en **Servers** y selecciona **Create > Server**.
2. Configura el servidor:

   - **Name**: Puedes usar cualquier nombre para identificar tu servidor (por ejemplo, `PostgresDB`).

3. Ve a la pestaña **Connection** y completa la información:

   - **Host**: `db` (nombre del servicio de la base de datos definido en `docker-compose.yml`).
   - **Port**: `5432` (puerto por defecto de PostgreSQL).
   - **Username**: `postgres` (o el valor que definiste en el archivo `.env`).
   - **Password**: `tucontraseña` (contraseña definida en el archivo `.env`).

4. Haz clic en **Save** para guardar la configuración y conectarte al servidor.

### 3. Gestionar la Base de Datos

Una vez conectado, podrás ver y gestionar tu base de datos en la sección **Databases** dentro del servidor que acabas de configurar:

- Explorar tablas, realizar consultas SQL, gestionar datos, etc.

### Credenciales por defecto

Si estás utilizando el archivo `.env` del proyecto, estas son las credenciales predeterminadas:

```env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=tucontraseña
    POSTGRES_DB=library_db
    PGADMIN_DEFAULT_EMAIL=pgadmin4@pgadmin.org
    PGADMIN_DEFAULT_PASSWORD=admin
```
