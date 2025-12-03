from pktCuentas.credit_account import CreditAccount
from pktCuentas.account import Account


class BankManager:
    def __init__(self, db_manager=None):
        self.accounts = []
        self.db_manager = db_manager

        # Load accounts from the database if available
        if self.db_manager:
            self.load_from_database()

    def load_from_database(self):
        """Load all accounts from the database"""
        try:
            if not self.db_manager:
                return

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

    def get_account(self, account_no):
        """Get an account by its number"""
        return next((acc for acc in self.accounts if acc.get_no_account() == int(account_no)), None)

    def add_account(self, account_no, last_name, middle_name, first_name,
                    account_type, balance, date, location, credit=0.0):
        """Add a new account"""
        try:
            # Check if it already exists
            if self.get_account(account_no):
                return Exception(f'La cuenta {account_no} ya existe')

            # Create the account according to the type
            if account_type == 'credit':
                new_account = CreditAccount(account_no, last_name, middle_name,
                                            first_name, balance, date, location)
                if credit > 0:
                    new_account.set_credit(credit)
            else:
                new_account = Account(account_no, last_name, middle_name,
                                      first_name, balance, date, location)

            # Add to the local list
            self.accounts.append(new_account)

            # Sync with database
            if self.db_manager:
                db_account_type = 'credit' if isinstance(new_account, CreditAccount) else 'normal'
                db_credit_limit = new_account.get_credit_limit() if isinstance(new_account, CreditAccount) else 0.0

                success, message = self.db_manager.insert_account(
                    account_no=new_account.get_no_account(),
                    last_name=new_account.get_apellido_paterno(),
                    middle_name=new_account.get_apellido_materno(),
                    first_name=new_account.get_nombre(),
                    balance=new_account.get_balance(),
                    date=new_account.get_fecha(),
                    location=new_account.get_lugar() if new_account.get_lugar() else '',
                    account_type=db_account_type,
                    credit_limit=db_credit_limit
                )

                if not success:
                    # Revert local change if DB fails
                    self.accounts.remove(new_account)
                    raise Exception(f'Error al insertar en BD: {message}')

            return new_account
        except Exception as e:
            return e

    def remove_account(self, account):
        """Remove an account"""
        try:
            if account not in self.accounts:
                return Exception('Cuenta no encontrada')

            # Remove from the local list
            self.accounts.remove(account)

            # Sync with database
            if self.db_manager:
                success, message = self.db_manager.delete_account(account.get_no_account())
                if not success:
                    # Revert local change if DB fails
                    self.accounts.append(account)
                    raise Exception(f'Error al eliminar de BD: {message}')

            return True
        except Exception as e:
            return e

    def list_accounts(self):
        """List all accounts"""
        return self.accounts

    def deposit_to_account(self, account_no, amount):
        """Deposit to an account"""
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            result = acc.deposit(amount)

            # Sync with database
            if self.db_manager and not isinstance(result, Exception):
                self.db_manager.update_account(account_no, balance=acc.get_balance())

            return result
        except Exception as e:
            return e

    def withdraw_from_account(self, account_no, amount):
        """Withdraw from an account"""
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            result = acc.withdraw(amount)

            # Sync with database
            if self.db_manager and not isinstance(result, Exception):
                self.db_manager.update_account(account_no, balance=acc.get_balance())

            return result
        except Exception as e:
            return e

    def modify_account_fields(self, account_no, last_name=None, middle_name=None,
                             first_name=None, date=None, location=None):
        """Modify account fields"""
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')

            if last_name is not None:
                acc.set_apellido_paterno(last_name)
            if middle_name is not None:
                acc.set_apellido_materno(middle_name)
            if first_name is not None:
                acc.set_nombre(first_name)
            if date is not None:
                acc.set_fecha(date)
            if location is not None:
                acc.set_lugar(location)

            # Sync with database
            if self.db_manager:
                self.db_manager.update_account(
                    account_no=account_no,
                    last_name=acc.get_apellido_paterno(),
                    middle_name=acc.get_apellido_materno(),
                    first_name=acc.get_nombre(),
                    date=acc.get_fecha(),
                    location=acc.get_lugar()
                )

            return acc
        except Exception as e:
            return e

    def modify_credit(self, account_no, new_credit):
        """Modify credit limit of an account"""
        try:
            acc = self.get_account(account_no)
            if not acc:
                return Exception('Cuenta no encontrada')
            if not isinstance(acc, CreditAccount):
                return Exception('La cuenta no es de crédito')

            acc.set_credit(new_credit)

            # Sync with database
            if self.db_manager:
                self.db_manager.update_account(account_no, credit_limit=new_credit)

            return acc
        except Exception as e:
            return e
