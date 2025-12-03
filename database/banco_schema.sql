-- Banco Database Schema

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS banco_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE banco_db;

-- Eliminar tabla si existe (para recreación limpia)
DROP TABLE IF EXISTS cuentas;

-- Crear tabla de cuentas
CREATE TABLE cuentas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    no_cuenta INT NOT NULL UNIQUE,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 1000.00,
    fecha DATE NULL,
    lugar VARCHAR(200) DEFAULT '',
    tipo_cuenta ENUM('normal', 'credit') NOT NULL DEFAULT 'normal',
    limite_credito DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_balance CHECK (balance >= 0),
    CONSTRAINT chk_limite_credito CHECK (limite_credito >= 0),
    CONSTRAINT chk_no_cuenta_positive CHECK (no_cuenta > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índices para mejorar rendimiento
CREATE INDEX idx_no_cuenta ON cuentas(no_cuenta);
CREATE INDEX idx_tipo_cuenta ON cuentas(tipo_cuenta);
CREATE INDEX idx_fecha ON cuentas(fecha);
CREATE INDEX idx_apellido_paterno ON cuentas(apellido_paterno);

-- Insertar datos de ejemplo (opcional)
INSERT INTO cuentas (no_cuenta, apellido_paterno, apellido_materno, nombre, balance, fecha, lugar, tipo_cuenta, limite_credito) VALUES
(1001, 'García', 'López', 'Juan', 5000.00, '2025-01-15', 'Ciudad de México', 'normal', 0.00),
(1002, 'Martínez', 'Rodríguez', 'María', 7500.50, '2025-02-20', 'Guadalajara', 'credit', 2000.00),
(1003, 'Hernández', 'Pérez', 'Carlos', 3200.00, '2025-03-10', 'Monterrey', 'normal', 0.00),
(1004, 'González', 'Sánchez', 'Ana', 12000.00, '2025-04-05', 'Puebla', 'credit', 5000.00),
(1005, 'Ramírez', 'Torres', 'Luis', 1500.00, '2025-05-12', 'Tijuana', 'normal', 0.00);

-- Verificar datos insertados
SELECT COUNT(*) as total_cuentas FROM cuentas;
SELECT tipo_cuenta, COUNT(*) as cantidad FROM cuentas GROUP BY tipo_cuenta;

