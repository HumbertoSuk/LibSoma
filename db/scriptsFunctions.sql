-- ==========================
--  FUNCIONES ALMACENADAS (POSTGRESQL USA `CREATE FUNCTION`)
-- ==========================

-- Función para devolver un libro
CREATE OR REPLACE FUNCTION return_book(p_loan_id INTEGER) RETURNS VOID AS $$
BEGIN
    -- Marcar el préstamo como devuelto
    UPDATE loans
    SET returned = TRUE, return_date = CURRENT_TIMESTAMP
    WHERE id = p_loan_id;

    -- Mover los datos del préstamo a la tabla loan_history
    INSERT INTO loan_history (user_id, book_id, loan_date, return_date, returned)
    SELECT user_id, book_id, loan_date, CURRENT_TIMESTAMP, TRUE
    FROM loans
    WHERE id = p_loan_id;

    -- Incrementar el número de copias disponibles del libro
    UPDATE books
    SET copies_available = copies_available + 1
    WHERE id = (SELECT book_id FROM loans WHERE id = p_loan_id);

    -- Eliminar el préstamo de la tabla loans (opcional)
    DELETE FROM loans WHERE id = p_loan_id;
END;
$$ LANGUAGE plpgsql;

-- Función para calcular la multa por retraso
CREATE OR REPLACE FUNCTION calculate_late_fee(p_loan_id INTEGER) RETURNS DECIMAL(10, 2) AS $$
DECLARE
    overdue_days INT;
    daily_fee DECIMAL(10, 2) DEFAULT 1.00;  -- Monto de la multa por día de retraso
    p_fee DECIMAL(10, 2);
BEGIN
    -- Calcular los días de retraso
    SELECT EXTRACT(DAY FROM CURRENT_TIMESTAMP - return_date)
    INTO overdue_days
    FROM loans
    WHERE id = p_loan_id AND returned = FALSE;

    -- Calcular la multa
    IF overdue_days > 0 THEN
        p_fee := overdue_days * daily_fee;
    ELSE
        p_fee := 0;
    END IF;

    -- Retornar la multa calculada
    RETURN p_fee;
END;
$$ LANGUAGE plpgsql;

-- Función para generar una multa
CREATE OR REPLACE FUNCTION issue_fine(p_user_id INTEGER, p_loan_id INTEGER, p_amount DECIMAL(10, 2), p_description TEXT) RETURNS VOID AS $$
BEGIN
    -- Insertar una nueva multa en la tabla fines
    INSERT INTO fines (user_id, loan_id, amount, description)
    VALUES (p_user_id, p_loan_id, p_amount, p_description);
END;
$$ LANGUAGE plpgsql;

-- Función para registrar el pago de una multa
CREATE OR REPLACE FUNCTION pay_fine(p_fine_id INTEGER) RETURNS VOID AS $$
BEGIN
    -- Marcar la multa como pagada
    UPDATE fines
    SET paid = TRUE
    WHERE id = p_fine_id;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener el historial de préstamos de un usuario
CREATE OR REPLACE FUNCTION get_user_loan_history(p_user_id INTEGER) RETURNS SETOF loan_history AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM loan_history
    WHERE user_id = p_user_id
    ORDER BY loan_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Función para gestionar una reserva
CREATE OR REPLACE FUNCTION reserve_book(p_user_id INTEGER, p_book_id INTEGER) RETURNS VOID AS $$
BEGIN
    -- Verificar si el libro tiene copias disponibles
    IF (SELECT copies_available FROM books WHERE id = p_book_id) > 0 THEN
        -- Insertar en la tabla de reservas
        INSERT INTO book_reservations (user_id, book_id, reservation_date, active)
        VALUES (p_user_id, p_book_id, CURRENT_TIMESTAMP, TRUE);

        -- Disminuir el número de copias disponibles
        UPDATE books
        SET copies_available = copies_available - 1
        WHERE id = p_book_id;
    ELSE
        -- Devolver un error si no hay copias disponibles
        RAISE EXCEPTION 'No copies available for reservation';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener las multas de un usuario
CREATE OR REPLACE FUNCTION get_user_fines(p_user_id INTEGER) RETURNS SETOF fines AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM fines
    WHERE user_id = p_user_id
    ORDER BY fine_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener los préstamos atrasados de un usuario
CREATE OR REPLACE FUNCTION get_overdue_loans(p_user_id INTEGER) RETURNS SETOF loans AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM loans
    WHERE user_id = p_user_id AND return_date < CURRENT_TIMESTAMP AND returned = FALSE
    ORDER BY return_date ASC;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener la disponibilidad de un libro
CREATE OR REPLACE FUNCTION get_book_availability(p_book_id INTEGER) RETURNS INTEGER AS $$
DECLARE
    available_copies INT;
BEGIN
    -- Obtener el número de copias disponibles del libro
    SELECT copies_available INTO available_copies
    FROM books
    WHERE id = p_book_id;
    
    RETURN available_copies;
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar la información de un libro
CREATE OR REPLACE FUNCTION update_book_info(p_book_id INTEGER, p_title TEXT, p_author TEXT, p_category_id INTEGER, p_isbn TEXT) RETURNS VOID AS $$
BEGIN
    UPDATE books
    SET title = p_title,
        author = p_author,
        category_id = p_category_id,
        isbn = p_isbn,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_book_id;
END;
$$ LANGUAGE plpgsql;

-- Función para eliminar un libro
CREATE OR REPLACE FUNCTION delete_book(p_book_id INTEGER) RETURNS VOID AS $$
BEGIN
    -- Verificar que no hay préstamos activos para el libro
    IF (SELECT COUNT(*) FROM loans WHERE book_id = p_book_id AND returned = FALSE) = 0 THEN
        -- Verificar que no hay reservas activas
        IF (SELECT COUNT(*) FROM book_reservations WHERE book_id = p_book_id AND active = TRUE) = 0 THEN
            DELETE FROM books WHERE id = p_book_id;
        ELSE
            RAISE EXCEPTION 'Cannot delete book: Active reservations exist';
        END IF;
    ELSE
        RAISE EXCEPTION 'Cannot delete book: Active loans exist';
    END IF;
END;
$$ LANGUAGE plpgsql;
