
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QInputDialog, QApplication
from PyQt5.uic import loadUi

from pktCuentas.bank_herencia import BankHerencia
from pktCuentas.credit_account import CreditAccount
from pktCuentasUI.add_account_dialog import AddAccountDialog


class Main(QMainWindow):
    def __init__(self,parent=None):
        try:
            super(Main,self).__init__(parent)
            loadUi('mwVentana.ui',self)
            self.bank = BankHerencia()
            self.setup_table()
            self.setup_events()
            try:
                self.clear_controls()
            except Exception:
                pass
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self,'Error',str(e))

    def setup_events(self):
        try:
            if hasattr(self, 'action_add'):
                self.action_add.triggered.connect(self.add_row)
            if hasattr(self, 'action_add_2'):
                self.action_add_2.triggered.connect(self.add_row)
            if hasattr(self, 'action_delete'):
                self.action_delete.triggered.connect(self.delete_selection)
            if hasattr(self, 'action_delete_2'):
                self.action_delete_2.triggered.connect(self.delete_selection)
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
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def setup_table(self):
        self.model = QStandardItemModel(0,6,self)
        self.model.setHorizontalHeaderLabels(['Cuenta','Cliente','Saldo','Tipo','Crédito','Lugar'])
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
            accounts = self.bank.handle_list_accounts() if hasattr(self.bank, 'handle_list_accounts') else list(self.bank.accounts)
            for acc in accounts:
                no = str(acc.get_no_account())
                client = f"{acc.get_apellido_paterno()} {acc.get_apellido_materno()} {acc.get_nombre()}"
                balance = f"{acc.get_balance():.2f}"
                if isinstance(acc, CreditAccount):
                    acct_type = "Cuenta de Crédito"
                    credit = f"{acc.get_credit_limit():.2f}" if hasattr(acc, 'get_credit_limit') else ""
                else:
                    acct_type = "Cuenta Normal"
                    credit = ""
                it_no = QStandardItem(no)
                it_client = QStandardItem(client)
                it_balance = QStandardItem(balance)
                it_type = QStandardItem(acct_type)
                it_credit = QStandardItem(credit)
                lugar_text = acc.get_lugar() if hasattr(acc, 'get_lugar') else ''
                it_place = QStandardItem(lugar_text)
                it_no.setTextAlignment(Qt.AlignCenter)
                it_client.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                it_balance.setTextAlignment(Qt.AlignCenter)
                it_type.setTextAlignment(Qt.AlignCenter)
                it_credit.setTextAlignment(Qt.AlignCenter)
                self.model.appendRow([it_no, it_client, it_balance, it_type, it_credit, it_place])
            try:
                if hasattr(self, 'tbl_accounts'):
                    self.tbl_accounts.resizeColumnsToContents()
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def add_row(self):
        try:
            dlg = AddAccountDialog(self)
            if dlg.exec_() == QDialog.Accepted:
                data = dlg.get_data()
                no_account = data['no_account']
                apep = data['apep']
                apem = data['apem']
                nombre = data['nombre']
                inicial_balance = data['balance']
                fecha = data['fecha']
                lugar = data['lugar']
                credit = data['credit']
                account_type = data['account_type']
                if self.bank.get_account(no_account):
                    QMessageBox.information(self,'Duplicado',f'La cuenta {no_account} ya existe')
                    return
                account = self.bank.handle_add_account(no_account, apep, apem, nombre, account_type, inicial_balance, fecha, lugar, credit)
                if isinstance(account, Exception):
                    QMessageBox.critical(self, 'Error', str(account))
                    return
                self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def find_row_by_account(self, account_no):
        for row in range(self.model.rowCount()):
            if self.model.item(row,0).text() == str(account_no):
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
                    f"Cuenta: {account.get_no_account()}",
                    f"Cliente: {account.get_apellido_paterno()} {account.get_apellido_materno()} {account.get_nombre()}",
                    f"Saldo: {account.get_balance():.2f}"
                ]
                if hasattr(account, 'get_fecha') and account.get_fecha():
                    info_lines.append(f"Fecha: {account.get_fecha()}")
                if hasattr(account, 'get_lugar') and account.get_lugar():
                    info_lines.append(f"Lugar: {account.get_lugar()}")
                if isinstance(account, CreditAccount):
                    info_lines.append("Tipo: Cuenta de Crédito")
                    info_lines.append(f"Límite de crédito: {account.get_credit_limit():.2f}")
                else:
                    info_lines.append("Tipo: Cuenta Normal")
                QMessageBox.information(self, 'Cuenta encontrada', '\n'.join(info_lines))
            else:
                QMessageBox.information(self,'No Encontrado',f'La cuenta {account_no} no se encuentra')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def handle_row_click(self, index):
        try:
            row = index.row()
            account_no = int(self.model.item(row,0).text())
            account = self.bank.get_account(account_no)
            if not account:
                QMessageBox.information(self, 'Error', 'Cuenta no encontrada')
                return
            info = f"Cuenta: {account.get_no_account()}\nCliente: {account.get_apellido_paterno()} {account.get_apellido_materno()} {account.get_nombre()}\nSaldo: {account.get_balance():.2f}"
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
                        'no_account': account.get_no_account(),
                        'apep': account.get_apellido_paterno(),
                        'apem': account.get_apellido_materno(),
                        'nombre': account.get_nombre(),
                        'balance': account.get_balance(),
                        'fecha': account.get_fecha() if hasattr(account, 'get_fecha') else None,
                        'lugar': account.get_lugar() if hasattr(account, 'get_lugar') else '',
                        'credit': account.get_credit_limit() if isinstance(account, CreditAccount) and hasattr(account, 'get_credit_limit') else 0.0,
                        'account_type': 'credit' if isinstance(account, CreditAccount) else 'normal'
                    }
                    edit_dlg = AddAccountDialog(self, data=dlg_data, edit_mode=True)
                    if edit_dlg.exec_() == QDialog.Accepted:
                        newdata = edit_dlg.get_data()
                        res = self.bank.modify_account_fields(account_no,
                                                             apellido_paterno=newdata['apep'],
                                                             apellido_materno=newdata['apem'],
                                                             nombre=newdata['nombre'],
                                                             fecha=newdata['fecha'],
                                                             lugar=newdata['lugar'])
                        if isinstance(res, Exception):
                            QMessageBox.critical(self, 'Error', str(res))
                        else:
                            if newdata.get('account_type') == 'credit':
                                try:
                                    credit_val = float(newdata.get('credit', 0.0))
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
                new_credit, ok = QInputDialog.getDouble(self, 'Modificar Crédito', 'Ingrese nuevo límite de crédito:', account.get_credit_limit(), 0.0, 1e12, 2)
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
                QMessageBox.information(self,'Eliminar','No hay cuentas seleccionadas')
                return
            resultado = QMessageBox.question(self, 'Eliminar','¿Está seguro de eliminar las cuentas seleccionadas?', QMessageBox.Yes|QMessageBox.No)
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

if __name__ == '__main__':
    app=QApplication(sys.argv)
    objVentana=Main()
    objVentana.show()
    app.exec()
