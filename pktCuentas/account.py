class Account(object):
    def __init__(self, no_account: int, apellido_paterno: str, apellido_materno: str, nombre: str,
                 balance: float = 1000.0, fecha: str = None, lugar: str = ""):
        self.__no_account = no_account
        self.__apellido_paterno = apellido_paterno
        self.__apellido_materno = apellido_materno
        self.__nombre = nombre
        self.__balance = float(balance)
        self.__fecha = fecha
        self.__lugar = lugar

    def get_balance(self):
        return self.__balance

    def get_no_account(self):
        return self.__no_account

    def get_apellido_paterno(self):
        return self.__apellido_paterno

    def get_apellido_materno(self):
        return self.__apellido_materno

    def get_nombre(self):
        return self.__nombre

    def get_fecha(self):
        return self.__fecha

    def get_lugar(self):
        return self.__lugar

    def get_last_name(self):
        return self.get_apellido_paterno()

    def get_maternal_last_name(self):
        return self.get_apellido_materno()

    def get_first_name(self):
        return self.get_nombre()

    def get_date(self):
        return self.get_fecha()

    def get_place(self):
        return self.get_lugar()

    def set_last_name(self, value: str):
        return self.set_apellido_paterno(value)

    def set_maternal_last_name(self, value: str):
        return self.set_apellido_materno(value)

    def set_first_name(self, value: str):
        return self.set_nombre(value)

    def set_date(self, value: str):
        return self.set_fecha(value)

    def set_place(self, value: str):
        return self.set_lugar(value)

    def set_apellido_paterno(self, valor: str):
        self.__apellido_paterno = valor
        return self.__apellido_paterno

    def set_apellido_materno(self, valor: str):
        self.__apellido_materno = valor
        return self.__apellido_materno

    def set_nombre(self, valor: str):
        self.__nombre = valor
        return self.__nombre

    def set_fecha(self, valor: str):
        self.__fecha = valor
        return self.__fecha

    def set_lugar(self, valor: str):
        self.__lugar = valor
        return self.__lugar

    def set_balance(self, balance: float):
        self.__balance = float(balance)
        return self.__balance

    def deposit(self, amount: float):
        try:
            amount = float(amount)
            if amount > 0:
                self.__balance += amount
                return self.get_balance()
            else:
                raise ValueError('Monto inválido para depósito')
        except Exception as e:
            return e

    def withdraw(self, amount: float):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError('Monto inválido para retiro')
            if amount > self.__balance:
                raise Exception('Saldo insuficiente')
            self.__balance -= amount
            return self.get_balance()
        except Exception as e:
            return e

    def print_account(self):
        return f"Cuenta No: {self.__no_account}, {self.__apellido_paterno} {self.__apellido_materno} {self.__nombre}, Balance: {self.__balance}, Fecha: {self.__fecha}, Lugar: {self.__lugar}"

    def __str__(self):
        return self.print_account()
