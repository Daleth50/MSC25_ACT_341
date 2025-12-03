from pktCuentas.account import Account


class CreditAccount(Account):
    def __init__(self, no_account, apellido_paterno, apellido_materno, nombre, balance=1000.0, fecha=None, lugar=""):
        super().__init__(no_account, apellido_paterno, apellido_materno, nombre, balance, fecha, lugar)
        self.credit = 500.0

    def get_credit_limit(self):
        return self.credit

    def set_credit(self, balance):
        self.credit = float(balance)
        return self.credit

    def get_credit_limit_amount(self):
        return self.get_credit_limit()

    def set_credit_limit(self, amount):
        return self.set_credit(amount)

    def withdraw(self, amount):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError('Monto inválido para retiro')
            account_balance = super().get_balance()
            if amount <= account_balance:
                return super().withdraw(amount)
            elif amount <= (account_balance + self.get_credit_limit()):
                remaining = amount - account_balance
                super().set_balance(0)
                self.credit -= remaining
                return super().get_balance()
            else:
                return Exception('Saldo y crédito insuficiente')
        except Exception as e:
            return e

    def __str__(self):
        return f"{super().__str__()}, Límite de crédito: {self.get_credit_limit()}"
