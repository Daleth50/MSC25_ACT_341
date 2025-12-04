import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QInputDialog, QApplication
from PyQt5.uic import loadUi

from pktCuentas.bank_herencia import BankManager
from pktCuentas.credit_account import CreditAccount
from pktCuentas.database_manager import DatabaseManager
from pktCuentas.data_manager import DataManager
from pktCuentas.analytics import Analytics
from pktCuentas.charts import ChartGenerator
from pktCuentasUI.add_account_dialog import AddAccountDialog
from pktCuentasUI.filter_dialogs import BalanceFilterDialog, AccountTypeFilterDialog, PlaceFilterDialog
from pktCuentasUI.results_dialogs import ChartDialog, FilterResultDialog, ImportResultDialog
from pktCuentasUI.report_dialog import ReportDialog


class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        try:
            # Load UI file from the same directory as this script
            ui_path = os.path.join(os.path.dirname(__file__), 'mwVentana.ui')
            loadUi(ui_path, self)
            self.db_manager = DatabaseManager()
            connected = self.db_manager.connect()
            if not connected:
                QMessageBox.warning(self, 'Advertencia Base de Datos',
                                    'No se pudo conectar a la base de datos MySQL.\n'
                                    'El sistema funcionará en modo local sin persistencia.\n\n'
                                    'Verifique:\n'
                                    '1. MySQL está instalado y corriendo\n'
                                    '2. La base de datos "banco_db" existe (ejecute banco_schema.sql)\n'
                                    '3. Las credenciales en config/database_config.ini son correctas')
                self.db_manager = None
            self.bank = BankManager(self.db_manager)
            self.setup_table()
            self.setup_events()
            try:
                self.clear_controls()
            except Exception:
                pass
            # Ensure table is refreshed with data from DB
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def setup_events(self):
        # Acciones básicas
        if hasattr(self, 'action_add'):
            self.action_add.triggered.connect(self.add_row)
        if hasattr(self, 'action_delete'):
            self.action_delete.triggered.connect(self.delete_selection)
        if hasattr(self, 'action_search'):
            self.action_search.triggered.connect(self.search_account)
        if hasattr(self, 'action_search_2'):
            self.action_search_2.triggered.connect(self.search_account)
        if hasattr(self, 'action_exit'):
            self.action_exit.triggered.connect(self.exit_app)
        if hasattr(self, 'action_exit_2'):
            self.action_exit_2.triggered.connect(self.exit_app)
        if hasattr(self, 'tbl_accounts'):
            self.tbl_accounts.doubleClicked.connect(self.handle_row_click)

        # Acciones para importar/exportar
        if hasattr(self, 'action_import_csv'):
            self.action_import_csv.triggered.connect(self.import_csv)
        if hasattr(self, 'action_import_xlsx'):
            self.action_import_xlsx.triggered.connect(self.import_xlsx)
        if hasattr(self, 'action_export_csv'):
            self.action_export_csv.triggered.connect(self.export_csv)
        if hasattr(self, 'action_export_xlsx'):
            self.action_export_xlsx.triggered.connect(self.export_xlsx)

        # Acciones para filtros
        if hasattr(self, 'action_filter_balance'):
            self.action_filter_balance.triggered.connect(self.show_balance_filter)
        if hasattr(self, 'action_filter_type'):
            self.action_filter_type.triggered.connect(self.show_type_filter)
        if hasattr(self, 'action_filter_date_place'):
            self.action_filter_date_place.triggered.connect(self.show_date_place_filter)

        # Acciones para gráficas
        if hasattr(self, 'action_chart_balance'):
            self.action_chart_balance.triggered.connect(self.show_chart_balance)
        if hasattr(self, 'action_chart_types'):
            self.action_chart_types.triggered.connect(self.show_chart_types)
        if hasattr(self, 'action_chart_temporal'):
            self.action_chart_temporal.triggered.connect(self.show_chart_temporal)
        if hasattr(self, 'action_chart_credit'):
            self.action_chart_credit.triggered.connect(self.show_chart_credit)
        if hasattr(self, 'btnFiltroBalance'):
            self.btnFiltroBalance.clicked.connect(self.show_balance_filter)
        if hasattr(self, 'btnFiltroTipo'):
            self.btnFiltroTipo.clicked.connect(self.show_type_filter)
        if hasattr(self, 'btnFiltroFechaLugar'):
            self.btnFiltroFechaLugar.clicked.connect(self.show_date_place_filter)
        if hasattr(self, 'btnReportes'):
            self.btnReportes.clicked.connect(self.show_report_dialog)

    def setup_table(self):
        self.model = QStandardItemModel(0, 7, self)
        self.model.setHorizontalHeaderLabels(['No. Cuenta', 'Cliente', 'Saldo', 'Tipo', 'Crédito', 'Fecha'
        , 'Lugar'])
        if hasattr(self, 'tbl_accounts'):
            self.tbl_accounts.setModel(self.model)
            self.tbl_accounts.setSelectionBehavior(self.tbl_accounts.SelectRows)
            self.tbl_accounts.setSelectionMode(self.tbl_accounts.MultiSelection)
            self.tbl_accounts.setEditTriggers(self.tbl_accounts.NoEditTriggers)

    def clear_controls(self):
        return

    def refresh_table(self):
        try:
            self.model.removeRows(0, self.model.rowCount())
            accounts = self.bank.handle_list_accounts() if hasattr(self.bank, 'handle_list_accounts') else list(
                self.bank.accounts)
            for acc in accounts:
                no = str(acc.get_account_number())
                client = f"{acc.get_last_name()} {acc.get_maternal_last_name()} {acc.get_first_name()}"
                balance = f"{acc.get_balance():.2f}"
                account_type = "Crédito" if isinstance(acc, CreditAccount) else "Normal"
                credit_limit = f"{acc.get_credit_limit():.2f}" if isinstance(acc, CreditAccount) else "N/A"
                place = acc.get_place() if hasattr(acc, 'get_place') else ""

                # Handle date - could be string or datetime object
                date_value = "N/A"
                if hasattr(acc, 'get_date') and acc.get_date():
                    date = acc.get_date()
                    if hasattr(date, 'strftime'):
                        date_value = date.strftime('%Y-%m-%d')
                    else:
                        date_value = str(date)
                
                row_data = [
                    QStandardItem(no),
                    QStandardItem(client),
                    QStandardItem(balance),
                    QStandardItem(account_type),
                    QStandardItem(credit_limit),
                    QStandardItem(date_value),
                    QStandardItem(place)
                ]
                self.model.appendRow(row_data)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def add_row(self):
        try:
            dlg = AddAccountDialog(self)
            if dlg.exec_() == QDialog.Accepted:
                data = dlg.get_data()
                account_no = data['account_no']
                last_name = data['last_name']
                middle_name = data['middle_name']
                first_name = data['first_name']
                inicial_balance = data['balance']
                date = data['date']
                location = data['location']
                credit = data['credit_limit']
                account_type = data['account_type']
                if self.bank.get_account(account_no):
                    QMessageBox.information(self, 'Duplicado', f'La cuenta {account_no} ya existe')
                    return
                account = self.bank.handle_add_account(account_no, last_name, middle_name, first_name, account_type,
                                                       inicial_balance, date, location, credit)
                if isinstance(account, Exception):
                    QMessageBox.critical(self, 'Error', str(account))
                    return
                self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def find_row_by_account(self, account_no):
        for row in range(self.model.rowCount()):
            if self.model.item(row, 0).text() == str(account_no):
                return row
        return -1

    def search_account(self):
        try:
            clave, ok = QInputDialog.getText(self, 'Buscar', 'Ingrese el número de cuenta:')
            if not ok:
                return
            clave = clave.strip()
            if not clave:
                QMessageBox.information(self, 'Buscar', 'Ingrese el número de cuenta')
                return
            try:
                account_no = int(clave)
            except ValueError:
                QMessageBox.information(self, 'Buscar', 'La clave debe ser numérica')
                return
            account = self.bank.get_account(account_no)
            if account:
                row = self.find_row_by_account(account_no)
                if row < 0:
                    self.refresh_table()
                    row = self.find_row_by_account(account_no)
                if row >= 0 and hasattr(self, 'tbl_accounts'):
                    self.tbl_accounts.selectRow(row)
                info_lines = [
                    f"Cuenta: {account.get_account_number()}",
                    f"Cliente: {account.get_last_name()} {account.get_maternal_last_name()} {account.get_first_name()}",
                    f"Saldo: {account.get_balance():.2f}"
                ]
                if hasattr(account, 'get_date') and account.get_date():
                    info_lines.append(f"Fecha: {account.get_date()}")
                if hasattr(account, 'get_place') and account.get_place():
                    info_lines.append(f"Lugar: {account.get_place()}")
                if isinstance(account, CreditAccount):
                    info_lines.append("Tipo: Cuenta de Crédito")
                    info_lines.append(f"Límite de crédito: {account.get_credit_limit():.2f}")
                else:
                    info_lines.append("Tipo: Cuenta Normal")
                QMessageBox.information(self, 'Cuenta encontrada', '\n'.join(info_lines))
            else:
                QMessageBox.information(self, 'No Encontrado', f'La cuenta {account_no} no se encuentra')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def handle_row_click(self, index):
        try:
            row = index.row()
            account_no = int(self.model.item(row, 0).text())
            account = self.bank.get_account(account_no)
            if not account:
                QMessageBox.information(self, 'Error', 'Cuenta no encontrada')
                return
            info = f"Cuenta: {account.get_account_number()}\nCliente: {account.get_last_name()} {account.get_maternal_last_name()} {account.get_first_name()}\nSaldo: {account.get_balance():.2f}"
            if isinstance(account, CreditAccount):
                info += f"\nCrédito: {account.get_credit_limit():.2f}"
            msg = QMessageBox(self)
            msg.setWindowTitle('Registro seleccionado')
            msg.setText(info)
            btn_deposit = msg.addButton('Depositar', QMessageBox.ActionRole)
            btn_withdraw = msg.addButton('Retirar', QMessageBox.ActionRole)
            btn_edit = msg.addButton('Editar', QMessageBox.ActionRole)
            btn_close = msg.addButton(QMessageBox.Close)
            btn_credit = None
            if isinstance(account, CreditAccount):
                btn_credit = msg.addButton('Modificar Crédito', QMessageBox.ActionRole)
            msg.exec_()
            clicked = msg.clickedButton()
            if clicked == btn_deposit:
                amount, ok = QInputDialog.getDouble(self, 'Depositar', 'Ingrese monto a depositar:', 0.0, 0.0, 1e12, 2)
                if ok:
                    res = self.bank.deposit_to_account(account_no, amount)
                    if isinstance(res, Exception):
                        QMessageBox.critical(self, 'Error', str(res))
                    else:
                        QMessageBox.information(self, 'Depósito', f'Depósito exitoso. Nuevo saldo: {res:.2f}')
                        self.refresh_table()
            elif clicked == btn_withdraw:
                amount, ok = QInputDialog.getDouble(self, 'Retirar', 'Ingrese monto a retirar:', 0.0, 0.0, 1e12, 2)
                if ok:
                    res = self.bank.withdraw_from_account(account_no, amount)
                    if isinstance(res, Exception):
                        QMessageBox.critical(self, 'Error', str(res))
                    else:
                        QMessageBox.information(self, 'Retiro', f'Retiro procesado. Saldo: {res:.2f}')
                        self.refresh_table()
            elif clicked == btn_edit:
                try:
                    dlg_data = {
                        'account_no': account.get_account_number(),
                        'last_name': account.get_last_name(),
                        'middle_name': account.get_maternal_last_name(),
                        'first_name': account.get_first_name(),
                        'balance': account.get_balance(),
                        'date': account.get_date() if hasattr(account, 'get_date') else None,
                        'location': account.get_place() if hasattr(account, 'get_place') else '',
                        'credit_limit': account.get_credit_limit() if isinstance(account, CreditAccount) and hasattr(
                            account, 'get_credit_limit') else 0.0,
                        'account_type': 'credit' if isinstance(account, CreditAccount) else 'normal'
                    }
                    edit_dlg = AddAccountDialog(self, data=dlg_data, edit_mode=True)
                    if edit_dlg.exec_() == QDialog.Accepted:
                        newdata = edit_dlg.get_data()
                        # pass English-named fields to BankManager.modify_account_fields
                        res = self.bank.modify_account_fields(account_no,
                                                              last_name=newdata.get('last_name'),
                                                              middle_name=newdata.get('middle_name'),
                                                              first_name=newdata.get('first_name'),
                                                              date=newdata.get('date'),
                                                              location=newdata.get('location'))
                        if isinstance(res, Exception):
                            QMessageBox.critical(self, 'Error', str(res))
                        else:
                            if newdata.get('account_type') == 'credit':
                                try:
                                    credit_val = float(newdata.get('credit_limit', 0.0))
                                    c_res = self.bank.modify_credit(account_no, credit_val)
                                    if isinstance(c_res, Exception):
                                        QMessageBox.critical(self, 'Error', str(c_res))
                                except Exception:
                                    pass
                            QMessageBox.information(self, 'Editar', 'Campos modificados exitosamente')
                            self.refresh_table()
                except Exception as e:
                    QMessageBox.critical(self, 'Error', str(e))
            elif btn_credit is not None and clicked == btn_credit:
                new_credit, ok = QInputDialog.getDouble(self, 'Modificar Crédito', 'Ingrese nuevo límite de crédito:',
                                                        account.get_credit_limit(), 0.0, 1e12, 2)
                if ok:
                    res = self.bank.modify_credit(account_no, new_credit)
                    if isinstance(res, Exception):
                        QMessageBox.critical(self, 'Error', str(res))
                    else:
                        QMessageBox.information(self, 'Crédito', f'Límite modificado: {new_credit:.2f}')
                        self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def delete_selection(self):
        try:
            if hasattr(self, 'tbl_accounts'):
                selection = self.tbl_accounts.selectionModel().selectedRows()
            else:
                selection = []
            if not selection:
                QMessageBox.information(self, 'Eliminar', 'No hay cuentas seleccionadas')
                return
            resultado = QMessageBox.question(self, 'Eliminar', '¿Está seguro de eliminar las cuentas seleccionadas?',
                                             QMessageBox.Yes | QMessageBox.No)
            if resultado == QMessageBox.Yes:
                nums = [int(self.model.item(idx.row(), 0).text()) for idx in selection]
                for account_no in nums:
                    acc = self.bank.get_account(account_no)
                    if acc:
                        res = self.bank.remove_account(acc)
                        if isinstance(res, Exception):
                            QMessageBox.critical(self, 'Error', f'Error al eliminar la cuenta {account_no}: {res}')
                self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def exit_app(self):
        try:
            result = QMessageBox.question(self, 'Salir', '¿Está seguro de salir?', QMessageBox.Yes | QMessageBox.No)
            if result == QMessageBox.Yes:
                QApplication.quit()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def import_csv(self):
        try:
            from PyQt5.QtWidgets import QFileDialog
            # Ensure CSV filter is selected by default. Use a non-native dialog
            # when needed so selectedFilter is respected on macOS.
            opts = QFileDialog.Options()
            opts |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getOpenFileName(self, 'Importar CSV', '',
                                                      'CSV Files (*.csv);;Excel Files (*.xlsx)',
                                                      'CSV Files (*.csv)', options=opts)
            if filename:
                # Dispatch to the correct importer based on file extension
                if filename.lower().endswith('.xlsx'):
                    result = DataManager.import_from_xlsx(filename, self.db_manager, self.bank)
                else:
                    result = DataManager.import_from_csv(filename, self.db_manager, self.bank)
                # Update dialog to use new keys: 'success', 'errors', 'duplicates'
                dlg = ImportResultDialog(result, self)
                dlg.exec_()
                self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def import_xlsx(self):
        try:
            from PyQt5.QtWidgets import QFileDialog
            # Force Excel filter as selectedFilter to ensure default on all platforms.
            opts = QFileDialog.Options()
            opts |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getOpenFileName(self, 'Importar Excel', '',
                                                      'Excel Files (*.xlsx);;CSV Files (*.csv)',
                                                      'Excel Files (*.xlsx)', options=opts)
            if filename:
                if filename.lower().endswith('.xlsx'):
                    result = DataManager.import_from_xlsx(filename, self.db_manager, self.bank)
                else:
                    result = DataManager.import_from_csv(filename, self.db_manager, self.bank)
                dlg = ImportResultDialog(result, self)
                dlg.exec_()
                self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def export_csv(self):
        try:
            from PyQt5.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(self, 'Exportar CSV', '', 'CSV Files (*.csv)')
            if filename:
                accounts = self.bank.handle_list_accounts()
                exito, mensaje = DataManager.export_to_csv(accounts, filename)
                if not exito:
                    QMessageBox.critical(self, 'Error', f'Error al exportar: {mensaje}')
                else:
                    QMessageBox.information(self, 'Exportar', mensaje)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def export_xlsx(self):
        try:
            from PyQt5.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(self, 'Exportar Excel', '', 'Excel Files (*.xlsx)')
            if filename:
                accounts = self.bank.handle_list_accounts()
                exito, mensaje = DataManager.export_to_xlsx(accounts, filename)
                if not exito:
                    QMessageBox.critical(self, 'Error', f'Error al exportar: {mensaje}')
                else:
                    QMessageBox.information(self, 'Exportar', mensaje)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    # Métodos de filtros
    def show_balance_filter(self):
        try:
            dlg = BalanceFilterDialog(self)
            if dlg.exec_() == QDialog.Accepted:
                params = dlg.get_filter_params()
                accounts = self.bank.handle_list_accounts()
                df = Analytics.accounts_to_dataframe(accounts)
                filtered_df = Analytics.filter_by_balance_range(df, params['balance_min'], params['balance_max'])
                result_dlg = FilterResultDialog(filtered_df, 'Filtro por Saldo', self)
                result_dlg.exec_()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_type_filter(self):
        try:
            dlg = AccountTypeFilterDialog(self)
            if dlg.exec_() == QDialog.Accepted:
                params = dlg.get_filter_params()
                accounts = self.bank.handle_list_accounts()
                df = Analytics.accounts_to_dataframe(accounts)
                filtered_df = Analytics.filter_by_account_type(df, params['tipo'])
                result_dlg = FilterResultDialog(filtered_df, f'Filtro por Tipo: {params["tipo"]}', self)
                result_dlg.exec_()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_date_place_filter(self):
        try:
            accounts = self.bank.handle_list_accounts()
            df = Analytics.accounts_to_dataframe(accounts)
            loc_options = Analytics.get_location_options(df)
            dlg = PlaceFilterDialog(self, locations=loc_options)
            if dlg.exec_() == QDialog.Accepted:
                params = dlg.get_filter_params()
                accounts = self.bank.handle_list_accounts()
                df = Analytics.accounts_to_dataframe(accounts)
                filtered_df = Analytics.filter_by_location(df, location=params['lugar'])
                result_dlg = FilterResultDialog(filtered_df, 'Filtro por Lugar', self)
                result_dlg.exec_()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_chart_balance(self):
        try:
            accounts = self.bank.handle_list_accounts()
            chart_gen = ChartGenerator()
            fig = chart_gen.generate_balance_histogram(accounts)
            if fig is not None:
                dlg = ChartDialog(fig, 'Distribución de Saldos', self)
                dlg.exec_()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_chart_types(self):
        try:
            accounts = self.bank.handle_list_accounts()
            chart_gen = ChartGenerator()
            fig = chart_gen.generate_account_type_pie(accounts)
            if fig is not None:
                dlg = ChartDialog(fig, 'Tipos de Cuenta', self)
                dlg.exec_()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_chart_temporal(self):
        try:
            accounts = self.bank.handle_list_accounts()
            chart_gen = ChartGenerator()
            fig = chart_gen.generate_temporal_trend(accounts)
            if fig is not None:
                dlg = ChartDialog(fig, 'Análisis Temporal', self)
                dlg.exec_()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_chart_credit(self):
        try:
            accounts = self.bank.handle_list_accounts()
            chart_gen = ChartGenerator()
            fig = chart_gen.generate_credit_comparison(accounts)
            if fig is not None:
                dlg = ChartDialog(fig, 'Uso de Crédito', self)
                dlg.exec_()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_report_dialog(self):
        try:
            dlg = ReportDialog(self)
            if dlg.exec_() == QDialog.Accepted:
                selected = dlg.get_selected_report()
                accounts = self.bank.handle_list_accounts()
                if selected == 'hist':
                    fig = ChartGenerator().generate_balance_histogram(accounts)
                    if fig is not None:
                        ChartDialog(fig, 'Distribución de Saldos', self).exec_()
                elif selected == 'pie':
                    fig = ChartGenerator().generate_account_type_pie(accounts)
                    if fig is not None:
                        ChartDialog(fig, 'Distribución por Tipo', self).exec_()
                elif selected == 'time':
                    fig = ChartGenerator().generate_temporal_trend(accounts)
                    if fig is not None:
                        ChartDialog(fig, 'Tendencia Temporal', self).exec_()
                elif selected == 'credit':
                    fig = ChartGenerator().generate_credit_comparison(accounts)
                    if fig is not None:
                        ChartDialog(fig, 'Comparación Crédito', self).exec_()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    objVentana = Main()
    objVentana.show()
    app.exec()
