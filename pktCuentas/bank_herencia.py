from pktCuentas.credit_account import CreditAccount
from pktCuentas.account import Account


class BankManager:
    def __init__(self, db_manager=None):
        self.accounts = []
        self.db_manager = db_manager
        self.reload_from_database()

    def reload_from_database(self):
        if self.db_manager:
            try:
                db_accounts = self.db_manager.get_all_accounts()
                self.accounts = []

                for acc_data in db_accounts:
                    account_no = acc_data['account_no']
                    last_name = acc_data['last_name']
                    middle_name = acc_data['middle_name']
                    first_name = acc_data['first_name']
                    balance = acc_data['balance']
                    date = acc_data.get('date')
                    location = acc_data.get('location', '')
                    account_type = acc_data.get('account_type', 'normal')
                    credit_limit = acc_data.get('credit_limit', 0.0)

                    if account_type == 'credit':
                        account = CreditAccount(account_no, last_name, middle_name,
                                                first_name, balance, date, location)
                        if credit_limit > 0:
                            account.set_credit(credit_limit)
                    else:
                        account = Account(account_no, last_name, middle_name,
                                          first_name, balance, date, location)

                    self.accounts.append(account)
            except Exception as e:
                print(f"Error loading accounts from DB: {e}")
        else:
            self.accounts = []

    def get_account(self, account_no):
        return next((acc for acc in self.accounts if acc.get_account_number() == int(account_no)), None)

    def add_account(self, account_no, last_name, middle_name, first_name,
                    account_type, balance, date, location, credit=0.0):
        try:
            if self.get_account(account_no):
                return Exception(f'La cuenta {account_no} ya existe')
            if account_type == 'credit':
                new_account = CreditAccount(account_no, last_name, middle_name,
                                            first_name, balance, date, location)
                if credit > 0:
                    new_account.set_credit(credit)
            else:
                new_account = Account(account_no, last_name, middle_name,
                                      first_name, balance, date, location)

            self.accounts.append(new_account)

            if self.db_manager:
                db_account_type = 'credit' if isinstance(new_account, CreditAccount) else 'normal'
                db_credit_limit = new_account.get_credit_limit() if isinstance(new_account, CreditAccount) else 0.0

                success, message = self.db_manager.insert_account(
                    account_no=new_account.get_account_number(),
                    last_name=new_account.get_last_name(),
                    middle_name=new_account.get_maternal_last_name(),
                    first_name=new_account.get_first_name(),
                    balance=new_account.get_balance(),
                    date=new_account.get_date(),
                    location=new_account.get_place() if new_account.get_place() else '',
                    account_type=db_account_type,
                    credit_limit=db_credit_limit
                )

                if not success:
                    self.accounts.remove(new_account)
                    raise Exception(f'Error al insertar en BD: {message}')

            return new_account
        except Exception as e:
            return e

    def handle_add_account(self, account_no, last_name, middle_name, first_name,
                          account_type, balance, date, location, credit=0.0):
        return self.add_account(account_no, last_name, middle_name, first_name,
                               account_type, balance, date, location, credit)

    def remove_account(self, account):
        try:
            if account not in self.accounts:
                return Exception('Cuenta no encontrada')

            # Remove from the local list
            self.accounts.remove(account)

            # Sync with database
            if self.db_manager:
                success, message = self.db_manager.delete_account(account.get_account_number())
                if not success:
                    # Revert local change if DB fails
                    self.accounts.append(account)
                    raise Exception(f'Error al eliminar de BD: {message}')

            return True
        except Exception as e:
            return e

    def list_accounts(self):
        return self.accounts

    def handle_list_accounts(self):
        return self.accounts

    def deposit_to_account(self, account_no, amount):
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            result = acc.deposit(amount)
            if self.db_manager and not isinstance(result, Exception):
                self.db_manager.update_account(account_no, balance=acc.get_balance())

            return result
        except Exception as e:
            return e

    def withdraw_from_account(self, account_no, amount):
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            result = acc.withdraw(amount)
            if self.db_manager and not isinstance(result, Exception):
                self.db_manager.update_account(account_no, balance=acc.get_balance())

            return result
        except Exception as e:
            return e

    def modify_account_fields(self, account_no, last_name=None, middle_name=None,
                             first_name=None, date=None, location=None):
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            if last_name is not None:
                acc.set_last_name(last_name)
            if middle_name is not None:
                acc.set_maternal_last_name(middle_name)
            if first_name is not None:
                acc.set_first_name(first_name)
            if date is not None:
                acc.set_date(date)
            if location is not None:
                acc.set_place(location)
            if self.db_manager:
                self.db_manager.update_account(
                    account_no=account_no,
                    last_name=acc.get_last_name(),
                    middle_name=acc.get_maternal_last_name(),
                    first_name=acc.get_first_name(),
                    date=acc.get_date(),
                    location=acc.get_place()
                )

            return acc
        except Exception as e:
            return e

    def modify_credit(self, account_no, new_credit):
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')
            if not isinstance(acc, CreditAccount):
                return Exception('La cuenta no es de crédito')

            acc.set_credit(new_credit)
            if self.db_manager:
                self.db_manager.update_account(account_no, credit_limit=new_credit)

            return acc
        except Exception as e:
            return e
