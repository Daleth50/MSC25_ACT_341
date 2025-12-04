from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QDateEdit, QComboBox,
                             QDoubleSpinBox, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QMessageBox)
from PyQt5.QtCore import QDate


class AddAccountDialog(QDialog):
    def __init__(self, parent=None, data=None, edit_mode=False):
        super().__init__(parent)
        self.setWindowTitle('Agregar cuenta' if not edit_mode else 'Editar cuenta')
        self.edit_mode = edit_mode
        self.setup_ui()
        if self.edit_mode:
            try:
                self.le_account.setReadOnly(True)
                self.spin_balance.setEnabled(False)
                self.combo_type.setEnabled(False)
                self.spin_credit.setEnabled(False)
            except Exception:
                pass
        if data:
            self.set_data(data)

    def setup_ui(self):
        grid = QGridLayout()

        grid.addWidget(QLabel('No. Cuenta:'), 0, 0)
        self.le_account = QLineEdit()
        grid.addWidget(self.le_account, 0, 1)

        grid.addWidget(QLabel('Apellido Paterno:'), 0, 2)
        self.le_last_name = QLineEdit()
        grid.addWidget(self.le_last_name, 0, 3)

        grid.addWidget(QLabel('Apellido Materno:'), 0, 4)
        self.le_maternal_last_name = QLineEdit()
        grid.addWidget(self.le_maternal_last_name, 0, 5)

        grid.addWidget(QLabel('Nombre:'), 1, 0)
        self.le_first_name = QLineEdit()
        grid.addWidget(self.le_first_name, 1, 1)

        grid.addWidget(QLabel('Fecha:'), 1, 2)
        self.date_date = QDateEdit()
        self.date_date.setCalendarPopup(True)
        self.date_date.setDisplayFormat('yyyy-MM-dd')
        self.date_date.setDate(QDate.currentDate())
        grid.addWidget(self.date_date, 1, 3)

        grid.addWidget(QLabel('Lugar:'), 1, 4)
        self.le_place = QLineEdit()
        grid.addWidget(self.le_place, 1, 5)

        grid.addWidget(QLabel('Balance inicial:'), 2, 0)
        self.spin_balance = QDoubleSpinBox()
        self.spin_balance.setRange(0.0, 1e12)
        self.spin_balance.setValue(1000.0)
        grid.addWidget(self.spin_balance, 2, 1)

        grid.addWidget(QLabel('Tipo:'), 2, 2)
        self.combo_type = QComboBox()
        self.combo_type.addItems(['Cuenta Normal', 'Cuenta de Crédito'])
        grid.addWidget(self.combo_type, 2, 3)

        grid.addWidget(QLabel('Límite Crédito:'), 2, 4)
        self.spin_credit = QDoubleSpinBox()
        self.spin_credit.setRange(0.0, 1e12)
        self.spin_credit.setValue(500.0)
        grid.addWidget(self.spin_credit, 2, 5)

        self.btn_add = QPushButton('Agregar' if not getattr(self, 'edit_mode', False) else 'Guardar')
        self.btn_cancel = QPushButton('Cancelar')
        btn_h = QHBoxLayout()
        btn_h.addStretch()
        btn_h.addWidget(self.btn_add)
        btn_h.addWidget(self.btn_cancel)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addLayout(btn_h)
        self.setLayout(layout)

        self._on_type_changed(self.combo_type.currentIndex())
        self.combo_type.currentIndexChanged.connect(self._on_type_changed)  # type: ignore[attr-defined]

        self.btn_add.clicked.connect(self._on_add_clicked)  # type: ignore[attr-defined]
        self.btn_cancel.clicked.connect(self.reject)  # type: ignore[attr-defined]

    def _on_type_changed(self, idx):
        if idx == 1:
            self.spin_credit.setVisible(True)
        else:
            self.spin_credit.setVisible(False)

    def _on_add_clicked(self):
        account_no_text = self.le_account.text().strip()
        last = self.le_last_name.text().strip()
        maternal = self.le_maternal_last_name.text().strip()
        first = self.le_first_name.text().strip()
        try:
            if not account_no_text:
                raise ValueError('La clave no puede estar vacía')
            account_no = int(account_no_text)
        except ValueError:
            QMessageBox.information(self, 'Validación', 'La clave debe ser numérica y no puede estar vacía')
            return
        if not last:
            QMessageBox.information(self, 'Validación', 'Apellido paterno no puede estar vacío')
            return
        if not maternal:
            QMessageBox.information(self, 'Validación', 'Apellido materno no puede estar vacío')
            return
        if not first:
            QMessageBox.information(self, 'Validación', 'El nombre no puede estar vacío')
            return
        self.accept()

    def set_data(self, data: dict):
        try:
            self.le_account.setText(str(data.get('account_no', '')))
            self.le_account.setReadOnly(True)
            self.le_last_name.setText(data.get('last_name', ''))
            self.le_maternal_last_name.setText(data.get('middle_name', ''))
            self.le_first_name.setText(data.get('first_name', ''))
            try:
                self.spin_balance.setValue(float(data.get('balance', 0.0)))
            except Exception:
                pass
            if data.get('date'):
                try:
                    self.date_date.setDate(QDate.fromString(data.get('date'), 'yyyy-MM-dd'))
                except Exception:
                    pass
            self.le_place.setText(data.get('location', ''))
            if data.get('account_type') == 'credit':
                self.combo_type.setCurrentIndex(1)
                try:
                    self.spin_credit.setValue(float(data.get('credit_limit', 0.0)))
                except Exception:
                    pass
            else:
                self.combo_type.setCurrentIndex(0)
        except Exception:
            pass

    def get_data(self):
        account_no = int(self.le_account.text().strip()) if self.le_account.text().strip() else 0
        last_name = self.le_last_name.text().strip()
        middle_name = self.le_maternal_last_name.text().strip()
        first_name = self.le_first_name.text().strip()
        inicial_balance = float(self.spin_balance.value())
        date = self.date_date.date().toString('yyyy-MM-dd')
        location = self.le_place.text().strip()
        credit_limit = float(self.spin_credit.value()) if self.spin_credit.isVisible() else 0.0
        selected_index = self.combo_type.currentIndex()
        account_type = 'credit' if selected_index == 1 else 'normal'
        return {
            'account_no': account_no,
            'last_name': last_name,
            'middle_name': middle_name,
            'first_name': first_name,
            'balance': inicial_balance,
            'date': date,
            'location': location,
            'credit_limit': credit_limit,
            'account_type': account_type
        }
