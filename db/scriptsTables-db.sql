-- ==========================
--  CREACIÓN DE TABLAS
-- ==========================

-- Tabla de Roles
CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

-- Tabla de Usuarios
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  role_id INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (role_id) REFERENCES roles(id)
);
-- Índice para mejorar las consultas basadas en role_id
CREATE INDEX idx_users_role_id ON users(role_id);

-- Tabla de Categorías (Normalizada)
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

-- Tabla de Libros
CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  category_id INTEGER,
  isbn TEXT UNIQUE NOT NULL,
  copies_available INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);
-- Índice para mejorar las consultas basadas en category_id
CREATE INDEX idx_books_category_id ON books(category_id);
-- Índices para facilitar la búsqueda de libros por título y autor
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);

-- Tabla de Préstamos (Relación Activa)
CREATE TABLE loans (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  book_id INTEGER,
  loan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  return_date TIMESTAMP,
  returned BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (book_id) REFERENCES books(id)
);
-- Índices para mejorar las consultas por usuario y libro
CREATE INDEX idx_loans_user_id ON loans(user_id);
CREATE INDEX idx_loans_book_id ON loans(book_id);

-- Tabla de Historial de Préstamos
CREATE TABLE loan_history (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  book_id INTEGER,
  loan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  return_date TIMESTAMP,
  returned BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (book_id) REFERENCES books(id)
);
-- Índices para mejorar las consultas por usuario y libro en el historial
CREATE INDEX idx_loan_history_user_id ON loan_history(user_id);
CREATE INDEX idx_loan_history_book_id ON loan_history(book_id);

-- Tabla de Reservas de Libros
CREATE TABLE book_reservations (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  book_id INTEGER,
  reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  active BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (book_id) REFERENCES books(id)
);
-- Índices para optimizar las consultas por usuario y libro en reservas
CREATE INDEX idx_reservations_user_id ON book_reservations(user_id);
CREATE INDEX idx_reservations_book_id ON book_reservations(book_id);

-- ==========================
--  ÍNDICES COMPUESTOS
-- ==========================

-- Índice compuesto para mejorar las consultas por usuario y libro en préstamos
CREATE INDEX idx_loans_user_book ON loans(user_id, book_id);

-- Índice compuesto para mejorar las consultas por usuario y estado en reservas
CREATE INDEX idx_reservations_user_active ON book_reservations(user_id, active);

-- ==========================
--  TABLA DE MULTAS
-- ==========================

-- Tabla de Multas (para registrar penalizaciones por retraso u otros motivos)
CREATE TABLE fines (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  loan_id INTEGER,
  amount DECIMAL(10, 2) NOT NULL,
  description TEXT NOT NULL,
  paid BOOLEAN DEFAULT FALSE,
  fine_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (loan_id) REFERENCES loans(id)
);
-- Índices para optimizar las consultas por usuario y estado de pago
CREATE INDEX idx_fines_user_id ON fines(user_id);
CREATE INDEX idx_fines_paid ON fines(paid);

CREATE TABLE invalidated_tokens (
    id SERIAL PRIMARY KEY,
    token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
