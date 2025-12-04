from mysql.connector import pooling, Error
from typing import List, Dict, Optional, Tuple
import configparser
import os


class DatabaseManager:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._connection = None
        self._load_config()

    def _load_config(self):
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
        if self._pool is None:
            self.connect()
        return self._pool.get_connection()

    def disconnect(self):
        if self._pool:
            self._pool = None

    def insert_account(self, account_no: int, last_name: str, middle_name: str,
                      first_name: str, balance: float = 1000.0, date: str = None,
                      location: str = "", account_type: str = "normal",
                      credit_limit: float = 0.0) -> Tuple[bool, str]:
        connection = None
        cursor = None

        try:
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
        connection = None
        cursor = None

        try:
            if not self.account_exists(account_no):
                return False, f"La cuenta {account_no} no existe"
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
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
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
