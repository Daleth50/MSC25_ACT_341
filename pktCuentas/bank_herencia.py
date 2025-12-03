from pktCuentas.credit_account import CreditAccount
from pktCuentas.account import Account


class BankHerencia:
    def __init__(self, db_manager=None):
        self.accounts = []
        self.db_manager = db_manager

        # Cargar cuentas desde la base de datos si está disponible
        if self.db_manager:
            self.load_from_database()

    def load_from_database(self):
        """Cargar todas las cuentas desde la base de datos"""
        try:
            if not self.db_manager:
                return

            cuentas_db = self.db_manager.obtener_todas_cuentas()
            self.accounts = []

            for cuenta_data in cuentas_db:
                no_cuenta = cuenta_data['no_cuenta']
                apellido_paterno = cuenta_data['apellido_paterno']
                apellido_materno = cuenta_data['apellido_materno']
                nombre = cuenta_data['nombre']
                balance = cuenta_data['balance']
                fecha = cuenta_data.get('fecha')
                lugar = cuenta_data.get('lugar', '')
                tipo_cuenta = cuenta_data.get('tipo_cuenta', 'normal')
                limite_credito = cuenta_data.get('limite_credito', 0.0)

                if tipo_cuenta == 'credit':
                    account = CreditAccount(no_cuenta, apellido_paterno, apellido_materno,
                                          nombre, balance, fecha, lugar)
                    if limite_credito > 0:
                        account.set_credit(limite_credito)
                else:
                    account = Account(no_cuenta, apellido_paterno, apellido_materno,
                                    nombre, balance, fecha, lugar)

                self.accounts.append(account)
        except Exception as e:
            print(f"Error al cargar cuentas desde BD: {e}")

    def get_account(self, account_no):
        """Obtener una cuenta por su número"""
        return next((acc for acc in self.accounts if acc.get_no_account() == int(account_no)), None)

    def handle_add_acount(self, no_account, apellido_paterno, apellido_materno, nombre,
                         account_type, balance, fecha, lugar, credit=0.0):
        """Agregar una nueva cuenta"""
        try:
            # Verificar si ya existe
            if self.get_account(no_account):
                return Exception(f'La cuenta {no_account} ya existe')

            # Crear la cuenta según el tipo
            if account_type == 'credit':
                new_account = CreditAccount(no_account, apellido_paterno, apellido_materno,
                                          nombre, balance, fecha, lugar)
                if credit > 0:
                    new_account.set_credit(credit)
            else:
                new_account = Account(no_account, apellido_paterno, apellido_materno,
                                    nombre, balance, fecha, lugar)

            # Agregar a la lista local
            self.accounts.append(new_account)

            # Sincronizar con base de datos
            if self.db_manager:
                tipo_cuenta = 'credit' if isinstance(new_account, CreditAccount) else 'normal'
                limite_credito = new_account.get_credit_limit() if isinstance(new_account, CreditAccount) else 0.0

                exito, mensaje = self.db_manager.insertar_cuenta(
                    no_cuenta=new_account.get_no_account(),
                    apellido_paterno=new_account.get_apellido_paterno(),
                    apellido_materno=new_account.get_apellido_materno(),
                    nombre=new_account.get_nombre(),
                    balance=new_account.get_balance(),
                    fecha=new_account.get_fecha(),
                    lugar=new_account.get_lugar() if new_account.get_lugar() else '',
                    tipo_cuenta=tipo_cuenta,
                    limite_credito=limite_credito
                )

                if not exito:
                    # Revertir cambio local si falla BD
                    self.accounts.remove(new_account)
                    raise Exception(f'Error al insertar en BD: {mensaje}')

            return new_account
        except Exception as e:
            return e

    def handle_add_account(self, *args, **kwargs):
        """Alias para handle_add_acount (corregir typo)"""
        return self.handle_add_acount(*args, **kwargs)

    def remove_account(self, account):
        """Eliminar una cuenta"""
        try:
            if account not in self.accounts:
                return Exception('Cuenta no encontrada')

            # Eliminar de la lista local
            self.accounts.remove(account)

            # Sincronizar con base de datos
            if self.db_manager:
                exito, mensaje = self.db_manager.eliminar_cuenta(account.get_no_account())
                if not exito:
                    # Revertir cambio local si falla BD
                    self.accounts.append(account)
                    raise Exception(f'Error al eliminar de BD: {mensaje}')

            return True
        except Exception as e:
            return e

    def handle_list_accounts(self):
        """Listar todas las cuentas"""
        return self.accounts

    def list_accounts(self):
        """Alias para handle_list_accounts"""
        return self.handle_list_accounts()

    def deposit_to_account(self, account_no, amount):
        """Depositar a una cuenta"""
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            result = acc.deposit(amount)

            # Sincronizar con base de datos
            if self.db_manager and not isinstance(result, Exception):
                self.db_manager.actualizar_balance(account_no, acc.get_balance())

            return result
        except Exception as e:
            return e

    def withdraw_from_account(self, account_no, amount):
        """Retirar de una cuenta"""
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            result = acc.withdraw(amount)

            # Sincronizar con base de datos
            if self.db_manager and not isinstance(result, Exception):
                self.db_manager.actualizar_balance(account_no, acc.get_balance())

            return result
        except Exception as e:
            return e

    def modify_account_fields(self, account_no, apellido_paterno=None, apellido_materno=None,
                             nombre=None, fecha=None, lugar=None):
        """Modificar campos de una cuenta"""
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            if apellido_paterno is not None:
                acc.set_apellido_paterno(apellido_paterno)
            if apellido_materno is not None:
                acc.set_apellido_materno(apellido_materno)
            if nombre is not None:
                acc.set_nombre(nombre)
            if fecha is not None:
                acc.set_fecha(fecha)
            if lugar is not None:
                acc.set_lugar(lugar)

            # Sincronizar con base de datos
            if self.db_manager:
                self.db_manager.actualizar_cuenta(
                    no_cuenta=account_no,
                    apellido_paterno=acc.get_apellido_paterno(),
                    apellido_materno=acc.get_apellido_materno(),
                    nombre=acc.get_nombre(),
                    fecha=acc.get_fecha(),
                    lugar=acc.get_lugar()
                )

            return acc
        except Exception as e:
            return e

    def modify_credit(self, account_no, new_credit):
        """Modificar límite de crédito de una cuenta"""
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')
            if not isinstance(acc, CreditAccount):
                return Exception('La cuenta no es de crédito')

            acc.set_credit(new_credit)

            # Sincronizar con base de datos
            if self.db_manager:
                self.db_manager.actualizar_limite_credito(account_no, new_credit)

            return acc
        except Exception as e:
            return e

