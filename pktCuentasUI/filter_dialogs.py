"""
Filter Dialogs Module
Dialogs for filtering data by different criteria
"""

from PyQt5.QtWidgets import (QDialog, QLabel, QDoubleSpinBox, QComboBox,
                             QDateEdit, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QMessageBox, QGroupBox, QCheckBox)
from PyQt5.QtCore import QDate


class BalanceFilterDialog(QDialog):
    """
    Dialog to filter accounts by balance range
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Rango de Balance')
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Balance range group
        group = QGroupBox("Rango de Balance")
        grid = QGridLayout()

        # Minimum balance
        grid.addWidget(QLabel('Balance Mínimo:'), 0, 0)
        self.spin_min = QDoubleSpinBox()
        self.spin_min.setRange(0.0, 1e12)
        self.spin_min.setValue(0.0)
        self.spin_min.setPrefix('$ ')
        self.spin_min.setDecimals(2)
        self.spin_min.setGroupSeparatorShown(True)
        grid.addWidget(self.spin_min, 0, 1)

        # Maximum balance
        grid.addWidget(QLabel('Balance Máximo:'), 1, 0)
        self.spin_max = QDoubleSpinBox()
        self.spin_max.setRange(0.0, 1e12)
        self.spin_max.setValue(1000000.0)
        self.spin_max.setPrefix('$ ')
        self.spin_max.setDecimals(2)
        self.spin_max.setGroupSeparatorShown(True)
        grid.addWidget(self.spin_max, 1, 1)

        group.setLayout(grid)
        layout.addWidget(group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_apply = QPushButton('Aplicar Filtro')
        self.btn_cancel = QPushButton('Cancelar')

        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Connect signals
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_cancel.clicked.connect(self.reject)

    def _on_apply(self):
        """Validate and accept the dialog"""
        min_val = self.spin_min.value()
        max_val = self.spin_max.value()

        if min_val > max_val:
            QMessageBox.warning(self, 'Validación', 'El balance mínimo no puede ser mayor que el máximo')
            return

        self.accept()

    def get_filter_params(self) -> dict:
        """
        Get filter parameters

        Returns:
            dict: Dictionary with balance_min and balance_max
        """
        return {
            'balance_min': self.spin_min.value(),
            'balance_max': self.spin_max.value()
        }


class AccountTypeFilterDialog(QDialog):
    """
    Dialog to filter accounts by type
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Tipo de Cuenta')
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Account type group
        group = QGroupBox("Tipo de Cuenta")
        grid = QGridLayout()

        # Type combo box
        grid.addWidget(QLabel('Seleccionar Tipo:'), 0, 0)
        self.combo_type = QComboBox()
        self.combo_type.addItems(['Todas', 'Cuentas Normales', 'Cuentas de Crédito'])
        grid.addWidget(self.combo_type, 0, 1)

        # Additional information
        info_label = QLabel(
            'Filter accounts by type:\n\n'
            '• Todas: Show all accounts\n'
            '• Cuentas Normales: Only accounts without credit\n'
            '• Cuentas de Crédito: Only accounts with credit limit'
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet('QLabel { padding: 10px; background-color: #fff; color: #222; font-weight: bold; border-radius: 5px; }')
        grid.addWidget(info_label, 1, 0, 1, 2)

        group.setLayout(grid)
        layout.addWidget(group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_apply = QPushButton('Aplicar Filtro')
        self.btn_cancel = QPushButton('Cancelar')

        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Connect signals
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def get_filter_params(self) -> dict:
        """
        Get filter parameters

        Returns:
            dict: Dictionary with account type
        """
        tipo_map = {
            0: 'todas',
            1: 'normal',
            2: 'credit'
        }

        return {
            'tipo': tipo_map[self.combo_type.currentIndex()]
        }


class DatePlaceFilterDialog(QDialog):
    """
    Dialog to filter accounts by date and/or place
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Fecha y Lugar')
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Date range group
        group_fecha = QGroupBox("Rango de Fechas")
        grid_fecha = QGridLayout()

        # Start date
        grid_fecha.addWidget(QLabel('Fecha Inicio:'), 0, 0)
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDisplayFormat('yyyy-MM-dd')
        self.date_inicio.setDate(QDate.currentDate().addYears(-1))
        grid_fecha.addWidget(self.date_inicio, 0, 1)

        # End date
        grid_fecha.addWidget(QLabel('Fecha Fin:'), 1, 0)
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDisplayFormat('yyyy-MM-dd')
        self.date_fin.setDate(QDate.currentDate())
        grid_fecha.addWidget(self.date_fin, 1, 1)

        # Date filter checkbox
        self.chk_use_dates = QCheckBox('Aplicar filtro de fechas')
        self.chk_use_dates.setChecked(False)
        self.chk_use_dates.toggled.connect(self._toggle_dates)
        grid_fecha.addWidget(self.chk_use_dates, 2, 0, 1, 2)

        group_fecha.setLayout(grid_fecha)
        layout.addWidget(group_fecha)

        # Place group
        group_lugar = QGroupBox("Lugar")
        grid_lugar = QGridLayout()

        # Place search field
        grid_lugar.addWidget(QLabel('Buscar en Lugar:'), 0, 0)
        self.le_lugar = QLineEdit()
        self.le_lugar.setPlaceholderText('Ejemplo: Ciudad de México, Guadalajara...')
        grid_lugar.addWidget(self.le_lugar, 0, 1)

        # Information label
        info_label = QLabel(
            'Search is case sensitive.\nPartial matches will be found.'
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet('QLabel { padding: 5px; font-size: 9pt; color: #666; }')
        grid_lugar.addWidget(info_label, 1, 0, 1, 2)

        group_lugar.setLayout(grid_lugar)
        layout.addWidget(group_lugar)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_apply = QPushButton('Aplicar Filtro')
        self.btn_cancel = QPushButton('Cancelar')
        self.btn_clear = QPushButton('Limpiar')

        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Initial state
        self._toggle_dates(False)

        # Connect signals
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_clear.clicked.connect(self._on_clear)

    def _toggle_dates(self, enabled):
        """Enable/disable date controls"""
        self.date_inicio.setEnabled(enabled)
        self.date_fin.setEnabled(enabled)

    def _on_apply(self):
        """Validate and accept the dialog"""
        if self.chk_use_dates.isChecked():
            fecha_inicio = self.date_inicio.date()
            fecha_fin = self.date_fin.date()

            if fecha_inicio > fecha_fin:
                QMessageBox.warning(self, 'Validación', 'La fecha de inicio no puede ser posterior a la fecha fin')
                return

        # At least one filter must be active
        if not self.chk_use_dates.isChecked() and not self.le_lugar.text().strip():
            QMessageBox.information(self, 'Información', 'Debe activar al menos un filtro (fecha o lugar)')
            return

        self.accept()

    def _on_clear(self):
        """Clear controls"""
        self.chk_use_dates.setChecked(False)
        self.le_lugar.clear()
        self.date_inicio.setDate(QDate.currentDate().addYears(-1))
        self.date_fin.setDate(QDate.currentDate())

    def get_filter_params(self) -> dict:
        """
        Get filter parameters

        Returns:
            dict: Dictionary with start_date, end_date, place
        """
        params = {
            'fecha_inicio': None,
            'fecha_fin': None,
            'lugar': None
        }

        if self.chk_use_dates.isChecked():
            params['fecha_inicio'] = self.date_inicio.date().toString('yyyy-MM-dd')
            params['fecha_fin'] = self.date_fin.date().toString('yyyy-MM-dd')

        if self.le_lugar.text().strip():
            params['lugar'] = self.le_lugar.text().strip()

        return params
