import pandas as pd
from typing import Dict, List, Tuple
import os

class DataManager:

    @staticmethod
    def import_from_csv(file_path: str, db_manager, bank) -> Dict:
        result = {
            'success': 0,
            'errors': [],
            'duplicates': []
        }

        try:
            df = pd.read_csv(file_path)
            required_columns = ['account_no', 'last_name', 'middle_name', 'first_name', 'balance']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                result['errors'].append(
                    f"Missing columns in CSV: {', '.join(missing_columns)}"
                )
                return result
            if 'date' not in df.columns:
                df['date'] = None
            if 'location' not in df.columns:
                df['location'] = ''
            if 'account_type' not in df.columns:
                df['account_type'] = 'normal'
            if 'credit_limit' not in df.columns:
                df['credit_limit'] = 0.0
            for idx, row in df.iterrows():
                try:
                    try:
                        account_no = int(row['account_no'])
                    except (ValueError, TypeError):
                        result['errors'].append(
                            f"Row {idx + 2}: Invalid account number '{row['account_no']}'"
                        )
                        continue
                    if account_no <= 0:
                        result['errors'].append(
                            f"Row {idx + 2}: Account number must be positive"
                        )
                        continue
                    last_name = str(row['last_name']).strip()
                    middle_name = str(row['middle_name']).strip()
                    first_name = str(row['first_name']).strip()

                    if not last_name or last_name == 'nan':
                        result['errors'].append(
                            f"Row {idx + 2}: Last name is empty"
                        )
                        continue

                    if not middle_name or middle_name == 'nan':
                        result['errors'].append(
                            f"Row {idx + 2}: Middle name is empty"
                        )
                        continue

                    if not first_name or first_name == 'nan':
                        result['errors'].append(
                            f"Row {idx + 2}: First name is empty"
                        )
                        continue
                    try:
                        balance = float(row['balance'])
                        if balance < 0:
                            result['errors'].append(
                                f"Row {idx + 2}: Balance cannot be negative"
                            )
                            continue
                    except (ValueError, TypeError):
                        result['errors'].append(
                            f"Row {idx + 2}: Invalid balance '{row['balance']}'"
                        )
                        continue
                    date = None
                    if pd.notna(row['date']):
                        try:
                            date_parsed = pd.to_datetime(row['date'])
                            date = date_parsed.strftime('%Y-%m-%d')
                        except:
                            result['errors'].append(
                                f"Row {idx + 2}: Invalid date format '{row['date']}'"
                            )
                            continue
                    location = str(row['location']).strip() if pd.notna(row['location']) else ''
                    if location == 'nan':
                        location = ''
                    account_type = str(row['account_type']).strip().lower()
                    if account_type not in ['normal', 'credit']:
                        account_type = 'normal'
                    try:
                        credit_limit = float(row['credit_limit']) if pd.notna(row['credit_limit']) else 0.0
                        if credit_limit < 0:
                            credit_limit = 0.0
                    except:
                        credit_limit = 0.0
                    if db_manager:
                        if db_manager.account_exists(account_no):
                            result['duplicates'].append(account_no)
                            continue
                        success, message = db_manager.insert_account(
                            account_no=account_no,
                            last_name=last_name,
                            middle_name=middle_name,
                            first_name=first_name,
                            balance=balance,
                            date=date,
                            location=location,
                            account_type=account_type,
                            credit_limit=credit_limit
                        )

                        if success:
                            result['success'] += 1
                        else:
                            result['errors'].append(
                                f"Row {idx + 2}, Account {account_no}: {message}"
                            )
                    else:
                        if bank.get_account(account_no):
                            result['duplicates'].append(account_no)
                            continue
                        if account_type == 'credit':
                            from pktCuentas.credit_account import CreditAccount
                            account = CreditAccount(account_no, last_name, middle_name, first_name, balance, date, location)
                            if credit_limit > 0:
                                account.set_credit(credit_limit)
                        else:
                            from pktCuentas.account import Account
                            account = Account(account_no, last_name, middle_name, first_name, balance, date, location)
                        bank.accounts.append(account)
                        result['success'] += 1
                except Exception as e:
                    result['errors'].append(
                        f"Row {idx + 2}: Unexpected error - {str(e)}"
                    )
            if db_manager and result['success'] > 0:
                bank.reload_from_database()

        except FileNotFoundError:
            result['errors'].append(f"File not found: {file_path}")
        except pd.errors.EmptyDataError:
            result['errors'].append("CSV file is empty")
        except Exception as e:
            result['errors'].append(f"Error reading CSV: {str(e)}")

        return result

    @staticmethod
    def export_to_csv(accounts: List, file_path: str) -> Tuple[bool, str]:
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            data = []
            for acc in accounts:
                from pktCuentas.credit_account import CreditAccount

                account_type = 'credit' if isinstance(acc, CreditAccount) else 'normal'
                credit_limit = acc.get_credit_limit() if isinstance(acc, CreditAccount) else 0.0

                data.append({
                    'account_no': acc.get_account_number(),
                    'last_name': acc.get_last_name(),
                    'middle_name': acc.get_maternal_last_name(),
                    'first_name': acc.get_first_name(),
                    'balance': acc.get_balance(),
                    'date': acc.get_date() if acc.get_date() else '',
                    'location': acc.get_place() if acc.get_place() else '',
                    'account_type': account_type,
                    'credit_limit': credit_limit
                })
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')

            return True, f"Data successfully exported to {file_path}"

        except Exception as e:
            return False, f"Error exporting to CSV: {str(e)}"

    @staticmethod
    def export_to_xlsx(accounts: List, file_path: str) -> Tuple[bool, str]:
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            data = []
            for acc in accounts:
                from pktCuentas.credit_account import CreditAccount

                account_type = 'Credit Account' if isinstance(acc, CreditAccount) else 'Normal Account'
                credit_limit = acc.get_credit_limit() if isinstance(acc, CreditAccount) else 0.0

                data.append({
                    'Account No.': acc.get_account_number(),
                    'Last Name': acc.get_last_name(),
                    'Middle Name': acc.get_maternal_last_name(),
                    'First Name': acc.get_first_name(),
                    'Balance': acc.get_balance(),
                    'Date': acc.get_date() if acc.get_date() else '',
                    'Location': acc.get_place() if acc.get_place() else '',
                    'Account Type': account_type,
                    'Credit Limit': credit_limit
                })
            df = pd.DataFrame(data)
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Accounts')
                worksheet = writer.sheets['Accounts']
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

            return True, f"Data successfully exported to {file_path}"

        except Exception as e:
            return False, f"Error exporting to Excel: {str(e)}"

    @staticmethod
    def import_from_xlsx(file_path: str, db_manager, bank) -> Dict:
        """
        Import accounts from an Excel (.xlsx) file. This method normalizes common
        header names (e.g. 'Account No.' / 'account_no', 'Last Name' / 'last_name')
        so sheets produced by export_to_xlsx or user-created files are accepted.
        """
        result = {
            'success': 0,
            'errors': [],
            'duplicates': []
        }

        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            col_map = {}
            for col in df.columns:
                low = str(col).strip().lower()
                if low in ['account no', 'account no.', 'account_no', 'account number', 'accountnumber']:
                    col_map[col] = 'account_no'
                elif low in ['last name', 'last_name', 'lastname']:
                    col_map[col] = 'last_name'
                elif low in ['middle name', 'middle_name', 'middlename']:
                    col_map[col] = 'middle_name'
                elif low in ['first name', 'first_name', 'firstname']:
                    col_map[col] = 'first_name'
                elif low in ['balance', 'saldo']:
                    col_map[col] = 'balance'
                elif low in ['date']:
                    col_map[col] = 'date'
                elif low in ['location', 'lugar']:
                    col_map[col] = 'location'
                elif low in ['account type', 'account_type', 'tipo']:
                    col_map[col] = 'account_type'
                elif low in ['credit limit', 'credit_limit', 'limite credito', 'creditlimit']:
                    col_map[col] = 'credit_limit'
                else:
                    col_map[col] = col

            df = df.rename(columns=col_map)
            required_columns = ['account_no', 'last_name', 'middle_name', 'first_name', 'balance']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                result['errors'].append(f"Missing columns in Excel: {', '.join(missing_columns)}")
                return result

            if 'date' not in df.columns:
                df['date'] = None
            if 'location' not in df.columns:
                df['location'] = ''
            if 'account_type' not in df.columns:
                df['account_type'] = 'normal'
            if 'credit_limit' not in df.columns:
                df['credit_limit'] = 0.0
            for idx, row in df.iterrows():
                try:
                    try:
                        account_no = int(row['account_no'])
                    except (ValueError, TypeError):
                        result['errors'].append(
                            f"Row {idx + 2}: Invalid account number '{row['account_no']}'"
                        )
                        continue

                    if account_no <= 0:
                        result['errors'].append(f"Row {idx + 2}: Account number must be positive")
                        continue

                    last_name = str(row['last_name']).strip()
                    middle_name = str(row['middle_name']).strip()
                    first_name = str(row['first_name']).strip()

                    if not last_name or last_name == 'nan':
                        result['errors'].append(f"Row {idx + 2}: Last name is empty")
                        continue
                    if not middle_name or middle_name == 'nan':
                        result['errors'].append(f"Row {idx + 2}: Middle name is empty")
                        continue
                    if not first_name or first_name == 'nan':
                        result['errors'].append(f"Row {idx + 2}: First name is empty")
                        continue

                    try:
                        balance = float(row['balance'])
                        if balance < 0:
                            result['errors'].append(f"Row {idx + 2}: Balance cannot be negative")
                            continue
                    except (ValueError, TypeError):
                        result['errors'].append(f"Row {idx + 2}: Invalid balance '{row['balance']}'")
                        continue

                    date = None
                    if pd.notna(row['date']):
                        try:
                            date_parsed = pd.to_datetime(row['date'])
                            date = date_parsed.strftime('%Y-%m-%d')
                        except:
                            result['errors'].append(f"Row {idx + 2}: Invalid date format '{row['date']}'")
                            continue

                    location = str(row['location']).strip() if pd.notna(row['location']) else ''
                    if location == 'nan':
                        location = ''

                    account_type = str(row['account_type']).strip().lower()
                    if account_type not in ['normal', 'credit']:
                        account_type = 'normal'

                    try:
                        credit_limit = float(row['credit_limit']) if pd.notna(row['credit_limit']) else 0.0
                        if credit_limit < 0:
                            credit_limit = 0.0
                    except:
                        credit_limit = 0.0

                    if db_manager:
                        if db_manager.account_exists(account_no):
                            result['duplicates'].append(account_no)
                            continue
                        success, message = db_manager.insert_account(
                            account_no=account_no,
                            last_name=last_name,
                            middle_name=middle_name,
                            first_name=first_name,
                            balance=balance,
                            date=date,
                            location=location,
                            account_type=account_type,
                            credit_limit=credit_limit
                        )
                        if success:
                            result['success'] += 1
                        else:
                            result['errors'].append(f"Row {idx + 2}, Account {account_no}: {message}")
                    else:
                        if bank.get_account(account_no):
                            result['duplicates'].append(account_no)
                            continue
                        if account_type == 'credit':
                            from pktCuentas.credit_account import CreditAccount
                            account = CreditAccount(account_no, last_name, middle_name, first_name, balance, date, location)
                            if credit_limit > 0:
                                account.set_credit(credit_limit)
                        else:
                            from pktCuentas.account import Account
                            account = Account(account_no, last_name, middle_name, first_name, balance, date, location)
                        bank.accounts.append(account)
                        result['success'] += 1
                except Exception as e:
                    result['errors'].append(f"Row {idx + 2}: Unexpected error - {str(e)}")
            if db_manager and result['success'] > 0:
                bank.reload_from_database()

        except FileNotFoundError:
            result['errors'].append(f"File not found: {file_path}")
        except ValueError:
            result['errors'].append("Excel file is empty or invalid")
        except Exception as e:
            result['errors'].append(f"Error reading Excel: {str(e)}")

        return result
