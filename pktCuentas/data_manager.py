"""
Data Manager Module
Manages import and export of CSV/XLSX data
"""

import pandas as pd
from typing import Dict, List, Tuple
import os


class DataManager:
    """
    Data import/export manager for CSV/XLSX files
    """

    @staticmethod
    def import_from_csv(file_path: str, db_manager, bank) -> Dict:
        """
        Import accounts from a CSV file
        Validates data and inserts into the database

        Args:
            file_path: Path to the CSV file
            db_manager: DatabaseManager instance
            bank: BankHerencia instance

        Returns:
            Dict: {
                'success': int,
                'errors': List[str],
                'duplicates': List[int]
            }
        """
        result = {
            'success': 0,
            'errors': [],
            'duplicates': []
        }

        try:
            # Read CSV file
            df = pd.read_csv(file_path)

            # Validate required columns
            required_columns = ['account_no', 'last_name', 'middle_name', 'first_name', 'balance']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                result['errors'].append(
                    f"Missing columns in CSV: {', '.join(missing_columns)}"
                )
                return result

            # Optional columns
            if 'date' not in df.columns:
                df['date'] = None
            if 'location' not in df.columns:
                df['location'] = ''
            if 'account_type' not in df.columns:
                df['account_type'] = 'normal'
            if 'credit_limit' not in df.columns:
                df['credit_limit'] = 0.0

            # Process each row
            for idx, row in df.iterrows():
                try:
                    # Validate account number
                    try:
                        account_no = int(row['account_no'])
                    except (ValueError, TypeError):
                        result['errors'].append(
                            f"Row {idx + 2}: Invalid account number '{row['account_no']}'"
                        )
                        continue

                    # Validate positive account number
                    if account_no <= 0:
                        result['errors'].append(
                            f"Row {idx + 2}: Account number must be positive"
                        )
                        continue

                    # Validate non-empty names
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

                    # Validate balance
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

                    # Validate date (can be None)
                    date = None
                    if pd.notna(row['date']):
                        try:
                            # Try to parse date
                            date_parsed = pd.to_datetime(row['date'])
                            date = date_parsed.strftime('%Y-%m-%d')
                        except:
                            result['errors'].append(
                                f"Row {idx + 2}: Invalid date format '{row['date']}'"
                            )
                            continue

                    # Validate location
                    location = str(row['location']).strip() if pd.notna(row['location']) else ''
                    if location == 'nan':
                        location = ''

                    # Validate account_type
                    account_type = str(row['account_type']).strip().lower()
                    if account_type not in ['normal', 'credit']:
                        account_type = 'normal'

                    # Validate credit limit
                    try:
                        credit_limit = float(row['credit_limit']) if pd.notna(row['credit_limit']) else 0.0
                        if credit_limit < 0:
                            credit_limit = 0.0
                    except:
                        credit_limit = 0.0

                    # If connected to DB, validate duplicates in DB
                    if db_manager:
                        if db_manager.account_exists(account_no):
                            result['duplicates'].append(account_no)
                            continue
                        # Insert into database
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
                        # Local mode: validate duplicates in self.accounts
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

            # Reload accounts in bank if DB is used
            if db_manager and result['success'] > 0:
                bank.load_from_database()

        except FileNotFoundError:
            result['errors'].append(f"File not found: {file_path}")
        except pd.errors.EmptyDataError:
            result['errors'].append("CSV file is empty")
        except Exception as e:
            result['errors'].append(f"Error reading CSV: {str(e)}")

        return result

    @staticmethod
    def export_to_csv(accounts: List, file_path: str) -> Tuple[bool, str]:
        """
        Exports accounts to a CSV file

        Args:
            accounts: List of Account objects
            file_path: Path to the CSV file to create

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Convert accounts to list of dictionaries
            data = []
            for acc in accounts:
                from pktCuentas.credit_account import CreditAccount

                account_type = 'credit' if isinstance(acc, CreditAccount) else 'normal'
                credit_limit = acc.get_credit_limit() if isinstance(acc, CreditAccount) else 0.0

                data.append({
                    'account_no': acc.get_no_account(),
                    'last_name': acc.get_apellido_paterno(),
                    'middle_name': acc.get_apellido_materno(),
                    'first_name': acc.get_nombre(),
                    'balance': acc.get_balance(),
                    'date': acc.get_fecha() if acc.get_fecha() else '',
                    'location': acc.get_lugar() if acc.get_lugar() else '',
                    'account_type': account_type,
                    'credit_limit': credit_limit
                })

            # Create DataFrame and export
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')

            return True, f"Data successfully exported to {file_path}"

        except Exception as e:
            return False, f"Error exporting to CSV: {str(e)}"

    @staticmethod
    def export_to_xlsx(accounts: List, file_path: str) -> Tuple[bool, str]:
        """
        Exports accounts to an Excel (XLSX) file

        Args:
            accounts: List of Account objects
            file_path: Path to the XLSX file to create

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Convert accounts to list of dictionaries
            data = []
            for acc in accounts:
                from pktCuentas.credit_account import CreditAccount

                account_type = 'Credit Account' if isinstance(acc, CreditAccount) else 'Normal Account'
                credit_limit = acc.get_credit_limit() if isinstance(acc, CreditAccount) else 0.0

                data.append({
                    'Account No.': acc.get_no_account(),
                    'Last Name': acc.get_apellido_paterno(),
                    'Middle Name': acc.get_apellido_materno(),
                    'First Name': acc.get_nombre(),
                    'Balance': acc.get_balance(),
                    'Date': acc.get_fecha() if acc.get_fecha() else '',
                    'Location': acc.get_lugar() if acc.get_lugar() else '',
                    'Account Type': account_type,
                    'Credit Limit': credit_limit
                })

            # Create DataFrame and export
            df = pd.DataFrame(data)

            # Export with formatting
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Accounts')

                # Get worksheet to apply formatting
                worksheet = writer.sheets['Accounts']

                # Adjust column widths
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
