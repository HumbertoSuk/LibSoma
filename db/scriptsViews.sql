
-- ==========================
--  VISTAS NECESARIAS
-- ==========================

-- Vista para ver los préstamos activos
CREATE VIEW active_loans AS
SELECT l.id AS loan_id, u.username, b.title, l.loan_date, l.return_date
FROM loans l
JOIN users u ON l.user_id = u.id
JOIN books b ON l.book_id = b.id
WHERE l.returned = FALSE;

-- Vista para ver los préstamos atrasados
CREATE VIEW overdue_loans AS
SELECT l.id AS loan_id, u.username, b.title, l.loan_date, l.return_date
FROM loans l
JOIN users u ON l.user_id = u.id
JOIN books b ON l.book_id = b.id
WHERE l.return_date < CURRENT_TIMESTAMP AND l.returned = FALSE;

-- Vista para obtener libros más populares (basado en número de préstamos)
CREATE VIEW most_borrowed_books AS
SELECT b.id, b.title, COUNT(l.book_id) AS borrow_count
FROM loans l
JOIN books b ON l.book_id = b.id
GROUP BY b.id, b.title
ORDER BY borrow_count DESC;

-- Vista para ver las reservas activas por libro
CREATE VIEW active_reservations AS
SELECT r.id AS reservation_id, u.username, b.title, r.reservation_date
FROM book_reservations r
JOIN users u ON r.user_id = u.id
JOIN books b ON r.book_id = b.id
WHERE r.active = TRUE;

-- Vista para ver el historial de multas pagadas
CREATE VIEW paid_fines AS
SELECT f.id AS fine_id, u.username, f.amount, f.fine_date
FROM fines f
JOIN users u ON f.user_id = u.id
WHERE f.paid = TRUE
ORDER BY f.fine_date DESC;
