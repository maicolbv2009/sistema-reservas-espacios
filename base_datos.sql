
USE maicol_barrueto_test;

-- 1. Tabla de tipos de espacios
CREATE TABLE IF NOT EXISTS tipos_espacios (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);

-- 2. Tabla de docentes
CREATE TABLE IF NOT EXISTS docentes (
    id_docente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE
);

-- 3. Tabla de espacios
CREATE TABLE IF NOT EXISTS espacios (
    id_espacio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(150),
    capacidad INT NOT NULL,
    id_tipo INT NOT NULL,
    CONSTRAINT chk_capacidad CHECK (capacidad > 0),
    FOREIGN KEY (id_tipo)
        REFERENCES tipos_espacios(id_tipo)
);

-- 4. Tabla de reservas
CREATE TABLE IF NOT EXISTS reservas (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_docente INT NOT NULL,
    id_espacio INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_termino TIME NOT NULL,
    estado ENUM('ACTIVA', 'CANCELADA')
        NOT NULL DEFAULT 'ACTIVA',
    FOREIGN KEY (id_docente)
        REFERENCES docentes(id_docente),
    FOREIGN KEY (id_espacio)
        REFERENCES espacios(id_espacio),
    CONSTRAINT chk_horario
        CHECK (hora_termino > hora_inicio)
);

-- ==========================================
-- PROCEDIMIENTOS ALMACENADOS
-- ==========================================

DELIMITER $$

-- 1. Registrar un docente
CREATE PROCEDURE registrar_docente(
    IN p_nombre VARCHAR(100),
    IN p_correo VARCHAR(150)
)
BEGIN
    INSERT INTO docentes (nombre, correo)
    VALUES (p_nombre, p_correo);
END $$

-- 2. Registrar un espacio
CREATE PROCEDURE registrar_espacio(
    IN p_nombre VARCHAR(100),
    IN p_ubicacion VARCHAR(150),
    IN p_capacidad INT,
    IN p_id_tipo INT
)
BEGIN
    INSERT INTO espacios (nombre, ubicacion, capacidad, id_tipo)
    VALUES (p_nombre, p_ubicacion, p_capacidad, p_id_tipo);
END $$

-- 3. Crear una reserva evitando horarios superpuestos
CREATE PROCEDURE crear_reserva(
    IN p_id_docente INT,
    IN p_id_espacio INT,
    IN p_fecha DATE,
    IN p_hora_inicio TIME,
    IN p_hora_termino TIME
)
BEGIN
    IF p_hora_termino <= p_hora_inicio THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La hora de termino debe ser posterior al inicio';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM reservas
        WHERE id_espacio = p_id_espacio
          AND fecha = p_fecha
          AND estado = 'ACTIVA'
          AND p_hora_inicio < hora_termino
          AND p_hora_termino > hora_inicio
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El espacio ya esta reservado en ese horario';
    ELSE
        INSERT INTO reservas (
            id_docente, id_espacio, fecha,
            hora_inicio, hora_termino, estado
        )
        VALUES (
            p_id_docente, p_id_espacio, p_fecha,
            p_hora_inicio, p_hora_termino, 'ACTIVA'
        );
    END IF;
END $$

-- 4. Consultar todas las reservas
CREATE PROCEDURE listar_reservas()
BEGIN
    SELECT *
    FROM reservas
    ORDER BY fecha, hora_inicio;
END $$

-- 5. Cancelar una reserva
CREATE PROCEDURE cancelar_reserva(
    IN p_id_reserva INT
)
BEGIN
    UPDATE reservas
    SET estado = 'CANCELADA'
    WHERE id_reserva = p_id_reserva
      AND estado = 'ACTIVA';

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La reserva no existe o ya fue cancelada';
    END IF;
END $$

-- 6. Modificar una reserva
CREATE PROCEDURE modificar_reserva(
    IN p_id_reserva INT,
    IN p_fecha DATE,
    IN p_hora_inicio TIME,
    IN p_hora_termino TIME
)
BEGIN
    IF p_hora_termino <= p_hora_inicio THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Horario no valido';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM reservas
        WHERE id_reserva = p_id_reserva
          AND estado = 'ACTIVA'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La reserva no existe o no esta activa';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM reservas r
        WHERE r.id_espacio = (
            SELECT id_espacio FROM reservas
            WHERE id_reserva = p_id_reserva
        )
          AND r.fecha = p_fecha
          AND r.estado = 'ACTIVA'
          AND r.id_reserva <> p_id_reserva
          AND p_hora_inicio < r.hora_termino
          AND p_hora_termino > r.hora_inicio
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El horario se cruza con otra reserva';
    END IF;

    UPDATE reservas
    SET fecha = p_fecha,
        hora_inicio = p_hora_inicio,
        hora_termino = p_hora_termino
    WHERE id_reserva = p_id_reserva;
END $$

-- 7. Comprobar disponibilidad de un espacio
CREATE PROCEDURE comprobar_disponibilidad(
    IN p_id_espacio INT,
    IN p_fecha DATE,
    IN p_hora_inicio TIME,
    IN p_hora_termino TIME
)
BEGIN
    SELECT CASE
        WHEN EXISTS (
            SELECT 1
            FROM reservas
            WHERE id_espacio = p_id_espacio
              AND fecha = p_fecha
              AND estado = 'ACTIVA'
              AND p_hora_inicio < hora_termino
              AND p_hora_termino > hora_inicio
        )
        THEN 'NO DISPONIBLE'
        ELSE 'DISPONIBLE'
    END AS disponibilidad;
END $$

DELIMITER ;
