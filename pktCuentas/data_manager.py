"""
Data Manager Module
Gestiona importación y exportación de datos CSV/XLSX
"""

import pandas as pd
from typing import Dict, List, Tuple
import os


class DataManager:
    """
    Gestor de importación y exportación de datos
    Maneja archivos CSV y XLSX
    """

    @staticmethod
    def import_from_csv(file_path: str, db_manager, bank) -> Dict:
        """
        Importa cuentas desde un archivo CSV
        Valida datos e inserta en la base de datos

        Args:
            file_path: Ruta del archivo CSV
            db_manager: Instancia de DatabaseManager
            bank: Instancia de BankHerencia

        Returns:
            Dict: {
                'exitosos': int,
                'errores': List[str],
                'duplicados': List[int]
            }
        """
        resultado = {
            'exitosos': 0,
            'errores': [],
            'duplicados': []
        }

        try:
            # Leer archivo CSV
            df = pd.read_csv(file_path)

            # Validar columnas requeridas
            columnas_requeridas = ['no_cuenta', 'apellido_paterno', 'apellido_materno',
                                  'nombre', 'balance']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]

            if columnas_faltantes:
                resultado['errores'].append(
                    f"Columnas faltantes en CSV: {', '.join(columnas_faltantes)}"
                )
                return resultado

            # Columnas opcionales
            if 'fecha' not in df.columns:
                df['fecha'] = None
            if 'lugar' not in df.columns:
                df['lugar'] = ''
            if 'tipo_cuenta' not in df.columns:
                df['tipo_cuenta'] = 'normal'
            if 'limite_credito' not in df.columns:
                df['limite_credito'] = 0.0

            # Procesar cada fila
            for idx, row in df.iterrows():
                try:
                    # Validar número de cuenta
                    try:
                        no_cuenta = int(row['no_cuenta'])
                    except (ValueError, TypeError):
                        resultado['errores'].append(
                            f"Fila {idx + 2}: Número de cuenta inválido '{row['no_cuenta']}'"
                        )
                        continue

                    # Validar que no_cuenta sea positivo
                    if no_cuenta <= 0:
                        resultado['errores'].append(
                            f"Fila {idx + 2}: Número de cuenta debe ser positivo"
                        )
                        continue

                    # Validar nombres no vacíos
                    apellido_paterno = str(row['apellido_paterno']).strip()
                    apellido_materno = str(row['apellido_materno']).strip()
                    nombre = str(row['nombre']).strip()

                    if not apellido_paterno or apellido_paterno == 'nan':
                        resultado['errores'].append(
                            f"Fila {idx + 2}: Apellido paterno vacío"
                        )
                        continue

                    if not apellido_materno or apellido_materno == 'nan':
                        resultado['errores'].append(
                            f"Fila {idx + 2}: Apellido materno vacío"
                        )
                        continue

                    if not nombre or nombre == 'nan':
                        resultado['errores'].append(
                            f"Fila {idx + 2}: Nombre vacío"
                        )
                        continue

                    # Validar balance
                    try:
                        balance = float(row['balance'])
                        if balance < 0:
                            resultado['errores'].append(
                                f"Fila {idx + 2}: Balance no puede ser negativo"
                            )
                            continue
                    except (ValueError, TypeError):
                        resultado['errores'].append(
                            f"Fila {idx + 2}: Balance inválido '{row['balance']}'"
                        )
                        continue

                    # Validar fecha (puede ser None)
                    fecha = None
                    if pd.notna(row['fecha']):
                        try:
                            # Intentar parsear fecha
                            fecha_parsed = pd.to_datetime(row['fecha'])
                            fecha = fecha_parsed.strftime('%Y-%m-%d')
                        except:
                            resultado['errores'].append(
                                f"Fila {idx + 2}: Formato de fecha inválido '{row['fecha']}'"
                            )
                            continue

                    # Validar lugar
                    lugar = str(row['lugar']).strip() if pd.notna(row['lugar']) else ''
                    if lugar == 'nan':
                        lugar = ''

                    # Validar tipo_cuenta
                    tipo_cuenta = str(row['tipo_cuenta']).strip().lower()
                    if tipo_cuenta not in ['normal', 'credit']:
                        tipo_cuenta = 'normal'

                    # Validar límite de crédito
                    try:
                        limite_credito = float(row['limite_credito']) if pd.notna(row['limite_credito']) else 0.0
                        if limite_credito < 0:
                            limite_credito = 0.0
                    except:
                        limite_credito = 0.0

                    # Si hay conexión a BD, validar duplicados en BD
                    if db_manager:
                        if db_manager.validar_cuenta_existe(no_cuenta):
                            resultado['duplicados'].append(no_cuenta)
                            continue
                        # Insertar en base de datos
                        exito, mensaje = db_manager.insertar_cuenta(
                            no_cuenta=no_cuenta,
                            apellido_paterno=apellido_paterno,
                            apellido_materno=apellido_materno,
                            nombre=nombre,
                            balance=balance,
                            fecha=fecha,
                            lugar=lugar,
                            tipo_cuenta=tipo_cuenta,
                            limite_credito=limite_credito
                        )

                        if exito:
                            resultado['exitosos'] += 1
                        else:
                            resultado['errores'].append(
                                f"Fila {idx + 2}, Cuenta {no_cuenta}: {mensaje}"
                            )
                    else:
                        # Modo local: validar duplicados en self.accounts
                        if bank.get_account(no_cuenta):
                            resultado['duplicados'].append(no_cuenta)
                            continue
                        if tipo_cuenta == 'credit':
                            from pktCuentas.credit_account import CreditAccount
                            account = CreditAccount(no_cuenta, apellido_paterno, apellido_materno, nombre, balance, fecha, lugar)
                            if limite_credito > 0:
                                account.set_credit(limite_credito)
                        else:
                            from pktCuentas.account import Account
                            account = Account(no_cuenta, apellido_paterno, apellido_materno, nombre, balance, fecha, lugar)
                        bank.accounts.append(account)
                        resultado['exitosos'] += 1
                except Exception as e:
                    resultado['errores'].append(
                        f"Fila {idx + 2}: Error inesperado - {str(e)}"
                    )

            # Recargar cuentas en bank si hay BD
            if db_manager and resultado['exitosos'] > 0:
                bank.load_from_database()

        except FileNotFoundError:
            resultado['errores'].append(f"Archivo no encontrado: {file_path}")
        except pd.errors.EmptyDataError:
            resultado['errores'].append("El archivo CSV está vacío")
        except Exception as e:
            resultado['errores'].append(f"Error al leer CSV: {str(e)}")

        return resultado

    @staticmethod
    def export_to_csv(accounts: List, file_path: str) -> Tuple[bool, str]:
        """
        Exporta cuentas a un archivo CSV

        Args:
            accounts: Lista de objetos Account
            file_path: Ruta del archivo CSV a crear

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Crear directorio si no existe
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Convertir cuentas a lista de diccionarios
            data = []
            for acc in accounts:
                from pktCuentas.credit_account import CreditAccount

                tipo_cuenta = 'credit' if isinstance(acc, CreditAccount) else 'normal'
                limite_credito = acc.get_credit_limit() if isinstance(acc, CreditAccount) else 0.0

                data.append({
                    'no_cuenta': acc.get_no_account(),
                    'apellido_paterno': acc.get_apellido_paterno(),
                    'apellido_materno': acc.get_apellido_materno(),
                    'nombre': acc.get_nombre(),
                    'balance': acc.get_balance(),
                    'fecha': acc.get_fecha() if acc.get_fecha() else '',
                    'lugar': acc.get_lugar() if acc.get_lugar() else '',
                    'tipo_cuenta': tipo_cuenta,
                    'limite_credito': limite_credito
                })

            # Crear DataFrame y exportar
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')

            return True, f"Datos exportados exitosamente a {file_path}"

        except Exception as e:
            return False, f"Error al exportar a CSV: {str(e)}"

    @staticmethod
    def export_to_xlsx(accounts: List, file_path: str) -> Tuple[bool, str]:
        """
        Exporta cuentas a un archivo Excel (XLSX)

        Args:
            accounts: Lista de objetos Account
            file_path: Ruta del archivo XLSX a crear

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Crear directorio si no existe
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Convertir cuentas a lista de diccionarios
            data = []
            for acc in accounts:
                from pktCuentas.credit_account import CreditAccount

                tipo_cuenta = 'Cuenta de Crédito' if isinstance(acc, CreditAccount) else 'Cuenta Normal'
                limite_credito = acc.get_credit_limit() if isinstance(acc, CreditAccount) else 0.0

                data.append({
                    'No. Cuenta': acc.get_no_account(),
                    'Apellido Paterno': acc.get_apellido_paterno(),
                    'Apellido Materno': acc.get_apellido_materno(),
                    'Nombre': acc.get_nombre(),
                    'Balance': acc.get_balance(),
                    'Fecha': acc.get_fecha() if acc.get_fecha() else '',
                    'Lugar': acc.get_lugar() if acc.get_lugar() else '',
                    'Tipo de Cuenta': tipo_cuenta,
                    'Límite de Crédito': limite_credito
                })

            # Crear DataFrame y exportar
            df = pd.DataFrame(data)

            # Exportar con formato
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Cuentas')

                # Obtener worksheet para aplicar formato
                worksheet = writer.sheets['Cuentas']

                # Ajustar ancho de columnas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            return True, f"Datos exportados exitosamente a {file_path}"

        except Exception as e:
            return False, f"Error al exportar a Excel: {str(e)}"
