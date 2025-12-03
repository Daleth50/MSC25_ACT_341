-- Bank Database Schema

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS banco_db
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE banco_db;

-- Remove table if exists (for clean recreation)
DROP TABLE IF EXISTS accounts;

-- Create accounts table
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_no INT NOT NULL UNIQUE,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    date DATE,
    location VARCHAR(200),
    account_type ENUM('normal', 'credit') NOT NULL DEFAULT 'normal',
    credit_limit DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_account_no (account_no),
    INDEX idx_account_type (account_type),
    INDEX idx_date (date),
    INDEX idx_last_name (last_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data (optional)
INSERT INTO accounts (account_no, last_name, middle_name, first_name, balance, date, location, account_type, credit_limit) VALUES
(1010, 'Garcia', 'Lopez', 'Juan', 5000.00, '2025-01-15', 'Mexico City', 'normal', 0.00),
(1011, 'Martinez', 'Perez', 'Maria', 3000.00, '2025-02-20', 'Guadalajara', 'credit', 2000.00),
(1012, 'Hernandez', 'Sanchez', 'Luis', 8000.00, '2025-03-10', 'Monterrey', 'normal', 0.00),
(1013, 'Ramirez', 'Gomez', 'Ana', 12000.00, '2025-04-05', 'Puebla', 'credit', 5000.00),
(1014, 'Torres', 'Diaz', 'Carlos', 7000.00, '2025-05-12', 'Tijuana', 'normal', 0.00);

-- Verify inserted data
SELECT COUNT(*) as total_accounts FROM accounts;
SELECT account_type, COUNT(*) as quantity FROM accounts GROUP BY account_type;
