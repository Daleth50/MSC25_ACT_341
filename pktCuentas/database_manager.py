"""
Database Manager Module
Handles all MySQL database operations
Implements Singleton pattern and connection pool
"""

import mysql.connector
from mysql.connector import pooling, Error
from typing import List, Dict, Optional, Tuple
import configparser
import os


class DatabaseManager:
    """
    MySQL database manager with Singleton pattern
    Handles connections, CRUD operations, and transactions
    """

    _instance = None
    _pool = None

    def __new__(cls):
        """Implementación de Singleton"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa el gestor de base de datos"""
        if self._initialized:
            return

        self._initialized = True
        self._connection = None
        self._load_config()

    def _load_config(self):
        """Carga configuración desde archivo INI"""
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'database_config.ini')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        config.read(config_path)

        self.config = {
            'host': config.get('mysql', 'host'),
            'port': config.getint('mysql', 'port'),
            'database': config.get('mysql', 'database'),
            'user': config.get('mysql', 'user'),
            'password': config.get('mysql', 'password'),
            'pool_size': config.getint('mysql', 'pool_size'),
            'pool_name': config.get('mysql', 'pool_name')
        }

    def connect(self) -> bool:
        """
        Establece pool de conexiones a la base de datos
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            if self._pool is None:
                self._pool = pooling.MySQLConnectionPool(
                    pool_name=self.config['pool_name'],
                    pool_size=self.config['pool_size'],
                    host=self.config['host'],
                    port=self.config['port'],
                    database=self.config['database'],
                    user=self.config['user'],
                    password=self.config['password'],
                    autocommit=False
                )
            return True
        except Error as e:
            print(f"Database connection error: {e}")
            return False

    def _get_connection(self):
        """Obtiene una conexión del pool"""
        if self._pool is None:
            self.connect()
        return self._pool.get_connection()

    def disconnect(self):
        """Cierra el pool de conexiones"""
        if self._pool:
            # El pool se cerrará automáticamente al finalizar el programa
            self._pool = None

    def insert_account(self, account_no: int, last_name: str, middle_name: str,
                      first_name: str, balance: float = 1000.0, date: str = None,
                      location: str = "", account_type: str = "normal",
                      credit_limit: float = 0.0) -> Tuple[bool, str]:
        """
        Inserta una nueva cuenta en la base de datos

        Args:
            account_no: Número único de cuenta
            last_name: Apellido paterno del cliente
            middle_name: Apellido materno del cliente
            first_name: Nombre del cliente
            balance: Saldo inicial
            date: Fecha de apertura (formato YYYY-MM-DD)
            location: Lugar de apertura
            account_type: 'normal' o 'credit'
            credit_limit: Límite de crédito (solo para cuentas de crédito)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        connection = None
        cursor = None

        try:
            # Validaciones
            if not last_name or not middle_name or not first_name:
                return False, "Los nombres no pueden estar vacíos"

            if balance < 0:
                return False, "El balance no puede ser negativo"

            if account_type not in ['normal', 'credit']:
                return False, "Tipo de cuenta inválido"

            if self.account_exists(account_no):
                return False, f"La cuenta {account_no} ya existe"

            connection = self._get_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO accounts 
                (account_no, last_name, middle_name, first_name, balance, 
                 date, location, account_type, credit_limit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (account_no, last_name, middle_name, first_name,
                     balance, date, location, account_type, credit_limit)

            cursor.execute(query, values)
            connection.commit()

            return True, f"Cuenta {account_no} insertada exitosamente"

        except Error as e:
            if connection:
                connection.rollback()
            return False, f"Error al insertar cuenta: {str(e)}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_account(self, account_no: int, last_name: str = None,
                      middle_name: str = None, first_name: str = None,
                      balance: float = None, date: str = None, location: str = None,
                      credit_limit: float = None) -> Tuple[bool, str]:
        """
        Actualiza los datos de una cuenta existente

        Args:
            account_no: Número de cuenta a actualizar
            last_name: Nuevo apellido paterno (opcional)
            middle_name: Nuevo apellido materno (opcional)
            first_name: Nuevo nombre (opcional)
            balance: Nuevo balance (opcional)
            date: Nueva fecha (opcional)
            location: Nuevo lugar (opcional)
            credit_limit: Nuevo límite de crédito (opcional)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        connection = None
        cursor = None

        try:
            if not self.account_exists(account_no):
                return False, f"La cuenta {account_no} no existe"

            # Construir query dinámica con los campos a actualizar
            updates = []
            values = []

            if last_name is not None:
                updates.append("last_name = %s")
                values.append(last_name)

            if middle_name is not None:
                updates.append("middle_name = %s")
                values.append(middle_name)

            if first_name is not None:
                updates.append("first_name = %s")
                values.append(first_name)

            if balance is not None:
                if balance < 0:
                    return False, "El balance no puede ser negativo"
                updates.append("balance = %s")
                values.append(balance)

            if date is not None:
                updates.append("date = %s")
                values.append(date)

            if location is not None:
                updates.append("location = %s")
                values.append(location)

            if credit_limit is not None:
                if credit_limit < 0:
                    return False, "El límite de crédito no puede ser negativo"
                updates.append("credit_limit = %s")
                values.append(credit_limit)

            if not updates:
                return False, "No hay campos para actualizar"

            connection = self._get_connection()
            cursor = connection.cursor()

            query = f"UPDATE accounts SET {', '.join(updates)} WHERE account_no = %s"
            values.append(account_no)

            cursor.execute(query, tuple(values))
            connection.commit()

            return True, f"Cuenta {account_no} actualizada exitosamente"

        except Error as e:
            if connection:
                connection.rollback()
            return False, f"Error al actualizar cuenta: {str(e)}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete_account(self, account_no: int) -> Tuple[bool, str]:
        """
        Elimina una cuenta de la base de datos

        Args:
            account_no: Número de cuenta a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        connection = None
        cursor = None

        try:
            if not self.account_exists(account_no):
                return False, f"La cuenta {account_no} no existe"

            connection = self._get_connection()
            cursor = connection.cursor()

            query = "DELETE FROM accounts WHERE account_no = %s"
            cursor.execute(query, (account_no,))
            connection.commit()

            return True, f"Cuenta {account_no} eliminada exitosamente"

        except Error as e:
            if connection:
                connection.rollback()
            return False, f"Error al eliminar cuenta: {str(e)}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_all_accounts(self) -> List[Dict]:
        """
        Consulta todas las cuentas de la base de datos

        Returns:
            List[Dict]: Lista de diccionarios con los datos de las cuentas
        """
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT account_no, last_name, middle_name, first_name, 
                       balance, date, location, account_type, credit_limit
                FROM accounts
                ORDER BY account_no
            """

            cursor.execute(query)
            results = cursor.fetchall()

            return results

        except Error as e:
            print(f"Error getting accounts: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_account(self, account_no: int) -> Optional[Dict]:
        """
        Consulta una cuenta específica

        Args:
            account_no: Número de cuenta a consultar

        Returns:
            Optional[Dict]: Diccionario con los datos de la cuenta o None
        """
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT account_no, last_name, middle_name, first_name, 
                       balance, date, location, account_type, credit_limit
                FROM accounts
                WHERE account_no = %s
            """

            cursor.execute(query, (account_no,))
            result = cursor.fetchone()

            return result

        except Error as e:
            print(f"Error getting account: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_accounts_by_filter(self, account_type: str = None,
                              balance_min: float = None, balance_max: float = None,
                              date_start: str = None, date_end: str = None,
                              location: str = None) -> List[Dict]:
        """
        Consulta cuentas aplicando filtros

        Args:
            account_type: Filtrar por tipo de cuenta ('normal' o 'credit')
            balance_min: Balance mínimo
            balance_max: Balance máximo
            date_start: Fecha inicial (YYYY-MM-DD)
            date_end: Fecha final (YYYY-MM-DD)
            location: Filtrar por lugar (búsqueda parcial)

        Returns:
            List[Dict]: Lista de cuentas que cumplen los filtros
        """
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)

            # Construir query dinámica
            conditions = []
            values = []

            if account_type:
                conditions.append("account_type = %s")
                values.append(account_type)

            if balance_min is not None:
                conditions.append("balance >= %s")
                values.append(balance_min)

            if balance_max is not None:
                conditions.append("balance <= %s")
                values.append(balance_max)

            if date_start:
                conditions.append("date >= %s")
                values.append(date_start)

            if date_end:
                conditions.append("date <= %s")
                values.append(date_end)

            if location:
                conditions.append("location LIKE %s")
                values.append(f"%{location}%")

            query = """
                SELECT account_no, last_name, middle_name, first_name, 
                       balance, date, location, account_type, credit_limit
                FROM accounts
            """

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY account_no"

            cursor.execute(query, tuple(values))
            results = cursor.fetchall()

            return results

        except Error as e:
            print(f"Error filtering accounts: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def account_exists(self, account_no: int) -> bool:
        """
        Verifica si una cuenta existe en la base de datos

        Args:
            account_no: Número de cuenta a verificar

        Returns:
            bool: True si existe, False en caso contrario
        """
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            query = "SELECT COUNT(*) FROM accounts WHERE account_no = %s"
            cursor.execute(query, (account_no,))

            count = cursor.fetchone()[0]
            return count > 0

        except Error as e:
            print(f"Error checking account existence: {e}")
            return False

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
