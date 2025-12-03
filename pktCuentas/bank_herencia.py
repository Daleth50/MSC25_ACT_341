from pktCuentas.credit_account import CreditAccount
from pktCuentas.account import Account


class BankHerencia:
    def __init__(self):
        self.accounts = []

    def add_account(self, account):
        try:
            if self.get_account(account.get_no_account()):
                raise AttributeError("La cuenta ya existe.")
            self.accounts.append(account)
            return account
        except Exception as e:
            return e

    def get_account(self, account_no):
        try:
            return next((acc for acc in self.accounts if acc.get_no_account() == int(account_no)), None)
        except Exception:
            return None

    def remove_account(self, account):
        try:
            self.accounts.remove(account)
            return True
        except ValueError as e:
            return e

    def __list_accounts(self):
        return list(self.accounts)

    def handle_list_accounts(self):
        return self.__list_accounts()

    def handle_add_acount(self, no_account: int, apellido_paterno: str, apellido_materno: str, nombre: str,
                           account_type='normal', balance: float = 1000.0, fecha: str = None, lugar: str = "", credit: float = 0.0):
        try:
            if self.get_account(no_account):
                raise AttributeError('La cuenta ya existe')
            if account_type == 'normal':
                new_account = Account(no_account, apellido_paterno, apellido_materno, nombre, balance, fecha, lugar)
            else:
                new_account = CreditAccount(no_account, apellido_paterno, apellido_materno, nombre, balance, fecha, lugar)
                if credit:
                    new_account.set_credit(credit)
            self.accounts.append(new_account)
            return new_account
        except Exception as e:
            return e

    def handle_add_account(self, *args, **kwargs):
        return self.handle_add_acount(*args, **kwargs)

    def get_account_by_no(self, account_no):
        return self.get_account(account_no)

    def remove_account_by_no(self, account_no):
        acc = self.get_account(account_no)
        if acc:
            return self.remove_account(acc)
        return Exception('Cuenta no encontrada')

    def modify_credit_limit(self, account_no, new_credit):
        return self.modify_credit(account_no, new_credit)

    def list_accounts(self):
        return self.__list_accounts()

    def deposit_to_account(self, account_no, amount):
        acc = self.get_account(account_no)
        if not acc:
            return Exception('Cuenta no encontrada')
        return acc.deposit(amount)

    def withdraw_from_account(self, account_no, amount):
        acc = self.get_account(account_no)
        if not acc:
            return Exception('Cuenta no encontrada')
        return acc.withdraw(amount)

    def modify_account_fields(self, account_no, apellido_paterno=None, apellido_materno=None, nombre=None, fecha=None, lugar=None):
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
        return acc

    def modify_credit(self, account_no, new_credit):
        acc = self.get_account(account_no)
        if not acc:
            return Exception('Cuenta no encontrada')
        if not isinstance(acc, CreditAccount):
            return Exception('La cuenta no es de crédito')
        acc.set_credit(new_credit)
        return acc
