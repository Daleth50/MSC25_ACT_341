class Account(object):
    def __init__(self, account_number: int, last_name: str, maternal_last_name: str, first_name: str,
                 balance: float = 1000.0, date: str = None, place: str = ""):
        self.__account_number = account_number
        self.__last_name = last_name
        self.__maternal_last_name = maternal_last_name
        self.__first_name = first_name
        self.__balance = float(balance)
        self.__date = date
        self.__place = place

    def get_balance(self):
        return self.__balance

    def get_account_number(self):
        return self.__account_number

    def get_last_name(self):
        return self.__last_name

    def get_maternal_last_name(self):
        return self.__maternal_last_name

    def get_first_name(self):
        return self.__first_name

    def get_date(self):
        return self.__date

    def get_place(self):
        return self.__place

    def set_last_name(self, value: str):
        self.__last_name = value
        return self.__last_name

    def set_maternal_last_name(self, value: str):
        self.__maternal_last_name = value
        return self.__maternal_last_name

    def set_first_name(self, value: str):
        self.__first_name = value
        return self.__first_name

    def set_date(self, value: str):
        self.__date = value
        return self.__date

    def set_place(self, value: str):
        self.__place = value
        return self.__place

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
                raise ValueError('Invalid amount for deposit')
        except Exception as e:
            return e

    def withdraw(self, amount: float):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError('Invalid amount for withdrawal')
            if amount > self.__balance:
                raise Exception('Insufficient funds')
            self.__balance -= amount
            return self.get_balance()
        except Exception as e:
            return e

    def print_account(self):
        return f"Account No: {self.__account_number}, {self.__last_name} {self.__maternal_last_name} {self.__first_name}, Balance: {self.__balance}, Date: {self.__date}, Place: {self.__place}"

    def __str__(self):
        return self.print_account()
