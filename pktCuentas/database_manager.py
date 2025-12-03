"""
Database Manager Module
Gestiona todas las operaciones de base de datos MySQL
Implementa patrón Singleton y pool de conexiones
"""

import mysql.connector
from mysql.connector import pooling, Error
from typing import List, Dict, Optional, Tuple
import configparser
import os


class DatabaseManager:
    """
    Gestor de base de datos MySQL con patrón Singleton
    Maneja conexiones, operaciones CRUD y transacciones
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
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")

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
            print(f"Error al conectar a la base de datos: {e}")
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

    def insertar_cuenta(self, no_cuenta: int, apellido_paterno: str, apellido_materno: str,
                       nombre: str, balance: float = 1000.0, fecha: str = None,
                       lugar: str = "", tipo_cuenta: str = "normal",
                       limite_credito: float = 0.0) -> Tuple[bool, str]:
        """
        Inserta una nueva cuenta en la base de datos

        Args:
            no_cuenta: Número único de cuenta
            apellido_paterno: Apellido paterno del cliente
            apellido_materno: Apellido materno del cliente
            nombre: Nombre del cliente
            balance: Saldo inicial
            fecha: Fecha de apertura (formato YYYY-MM-DD)
            lugar: Lugar de apertura
            tipo_cuenta: 'normal' o 'credit'
            limite_credito: Límite de crédito (solo para cuentas de crédito)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        connection = None
        cursor = None

        try:
            # Validaciones
            if not apellido_paterno or not apellido_materno or not nombre:
                return False, "Los nombres no pueden estar vacíos"

            if balance < 0:
                return False, "El balance no puede ser negativo"

            if tipo_cuenta not in ['normal', 'credit']:
                return False, "Tipo de cuenta inválido"

            if self.validar_cuenta_existe(no_cuenta):
                return False, f"La cuenta {no_cuenta} ya existe"

            connection = self._get_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO cuentas 
                (no_cuenta, apellido_paterno, apellido_materno, nombre, balance, 
                 fecha, lugar, tipo_cuenta, limite_credito)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (no_cuenta, apellido_paterno, apellido_materno, nombre,
                     balance, fecha, lugar, tipo_cuenta, limite_credito)

            cursor.execute(query, values)
            connection.commit()

            return True, f"Cuenta {no_cuenta} insertada exitosamente"

        except Error as e:
            if connection:
                connection.rollback()
            return False, f"Error al insertar cuenta: {str(e)}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def actualizar_cuenta(self, no_cuenta: int, apellido_paterno: str = None,
                         apellido_materno: str = None, nombre: str = None,
                         balance: float = None, fecha: str = None, lugar: str = None,
                         limite_credito: float = None) -> Tuple[bool, str]:
        """
        Actualiza los datos de una cuenta existente

        Args:
            no_cuenta: Número de cuenta a actualizar
            apellido_paterno: Nuevo apellido paterno (opcional)
            apellido_materno: Nuevo apellido materno (opcional)
            nombre: Nuevo nombre (opcional)
            balance: Nuevo balance (opcional)
            fecha: Nueva fecha (opcional)
            lugar: Nuevo lugar (opcional)
            limite_credito: Nuevo límite de crédito (opcional)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        connection = None
        cursor = None

        try:
            if not self.validar_cuenta_existe(no_cuenta):
                return False, f"La cuenta {no_cuenta} no existe"

            # Construir query dinámica con los campos a actualizar
            updates = []
            values = []

            if apellido_paterno is not None:
                updates.append("apellido_paterno = %s")
                values.append(apellido_paterno)

            if apellido_materno is not None:
                updates.append("apellido_materno = %s")
                values.append(apellido_materno)

            if nombre is not None:
                updates.append("nombre = %s")
                values.append(nombre)

            if balance is not None:
                if balance < 0:
                    return False, "El balance no puede ser negativo"
                updates.append("balance = %s")
                values.append(balance)

            if fecha is not None:
                updates.append("fecha = %s")
                values.append(fecha)

            if lugar is not None:
                updates.append("lugar = %s")
                values.append(lugar)

            if limite_credito is not None:
                if limite_credito < 0:
                    return False, "El límite de crédito no puede ser negativo"
                updates.append("limite_credito = %s")
                values.append(limite_credito)

            if not updates:
                return False, "No hay campos para actualizar"

            connection = self._get_connection()
            cursor = connection.cursor()

            query = f"UPDATE cuentas SET {', '.join(updates)} WHERE no_cuenta = %s"
            values.append(no_cuenta)

            cursor.execute(query, tuple(values))
            connection.commit()

            return True, f"Cuenta {no_cuenta} actualizada exitosamente"

        except Error as e:
            if connection:
                connection.rollback()
            return False, f"Error al actualizar cuenta: {str(e)}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def eliminar_cuenta(self, no_cuenta: int) -> Tuple[bool, str]:
        """
        Elimina una cuenta de la base de datos

        Args:
            no_cuenta: Número de cuenta a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        connection = None
        cursor = None

        try:
            if not self.validar_cuenta_existe(no_cuenta):
                return False, f"La cuenta {no_cuenta} no existe"

            connection = self._get_connection()
            cursor = connection.cursor()

            query = "DELETE FROM cuentas WHERE no_cuenta = %s"
            cursor.execute(query, (no_cuenta,))
            connection.commit()

            return True, f"Cuenta {no_cuenta} eliminada exitosamente"

        except Error as e:
            if connection:
                connection.rollback()
            return False, f"Error al eliminar cuenta: {str(e)}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def consultar_todas(self) -> List[Dict]:
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
                SELECT no_cuenta, apellido_paterno, apellido_materno, nombre, 
                       balance, fecha, lugar, tipo_cuenta, limite_credito
                FROM cuentas
                ORDER BY no_cuenta
            """

            cursor.execute(query)
            results = cursor.fetchall()

            return results

        except Error as e:
            print(f"Error al consultar cuentas: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def consultar_una(self, no_cuenta: int) -> Optional[Dict]:
        """
        Consulta una cuenta específica

        Args:
            no_cuenta: Número de cuenta a consultar

        Returns:
            Optional[Dict]: Diccionario con los datos de la cuenta o None
        """
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT no_cuenta, apellido_paterno, apellido_materno, nombre, 
                       balance, fecha, lugar, tipo_cuenta, limite_credito
                FROM cuentas
                WHERE no_cuenta = %s
            """

            cursor.execute(query, (no_cuenta,))
            result = cursor.fetchone()

            return result

        except Error as e:
            print(f"Error al consultar cuenta: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def consultar_por_filtro(self, tipo_cuenta: str = None,
                            balance_min: float = None, balance_max: float = None,
                            fecha_inicio: str = None, fecha_fin: str = None,
                            lugar: str = None) -> List[Dict]:
        """
        Consulta cuentas aplicando filtros

        Args:
            tipo_cuenta: Filtrar por tipo de cuenta ('normal' o 'credit')
            balance_min: Balance mínimo
            balance_max: Balance máximo
            fecha_inicio: Fecha inicial (YYYY-MM-DD)
            fecha_fin: Fecha final (YYYY-MM-DD)
            lugar: Filtrar por lugar (búsqueda parcial)

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

            if tipo_cuenta:
                conditions.append("tipo_cuenta = %s")
                values.append(tipo_cuenta)

            if balance_min is not None:
                conditions.append("balance >= %s")
                values.append(balance_min)

            if balance_max is not None:
                conditions.append("balance <= %s")
                values.append(balance_max)

            if fecha_inicio:
                conditions.append("fecha >= %s")
                values.append(fecha_inicio)

            if fecha_fin:
                conditions.append("fecha <= %s")
                values.append(fecha_fin)

            if lugar:
                conditions.append("lugar LIKE %s")
                values.append(f"%{lugar}%")

            query = """
                SELECT no_cuenta, apellido_paterno, apellido_materno, nombre, 
                       balance, fecha, lugar, tipo_cuenta, limite_credito
                FROM cuentas
            """

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY no_cuenta"

            cursor.execute(query, tuple(values))
            results = cursor.fetchall()

            return results

        except Error as e:
            print(f"Error al consultar con filtros: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def validar_cuenta_existe(self, no_cuenta: int) -> bool:
        """
        Verifica si una cuenta existe en la base de datos

        Args:
            no_cuenta: Número de cuenta a verificar

        Returns:
            bool: True si existe, False en caso contrario
        """
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            query = "SELECT COUNT(*) FROM cuentas WHERE no_cuenta = %s"
            cursor.execute(query, (no_cuenta,))

            count = cursor.fetchone()[0]
            return count > 0

        except Error as e:
            print(f"Error al validar cuenta: {e}")
            return False

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

