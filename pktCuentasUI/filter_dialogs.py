"""
Filter Dialogs Module
Diálogos para filtrar datos con diferentes criterios
"""

from PyQt5.QtWidgets import (QDialog, QLabel, QDoubleSpinBox, QComboBox,
                             QDateEdit, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QMessageBox, QGroupBox)
from PyQt5.QtCore import QDate


class BalanceFilterDialog(QDialog):
    """
    Diálogo para filtrar cuentas por rango de balance
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Rango de Balance')
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()

        # Grupo de filtro
        group = QGroupBox("Rango de Balance")
        grid = QGridLayout()

        # Balance mínimo
        grid.addWidget(QLabel('Balance Mínimo:'), 0, 0)
        self.spin_min = QDoubleSpinBox()
        self.spin_min.setRange(0.0, 1e12)
        self.spin_min.setValue(0.0)
        self.spin_min.setPrefix('$ ')
        self.spin_min.setDecimals(2)
        self.spin_min.setGroupSeparatorShown(True)
        grid.addWidget(self.spin_min, 0, 1)

        # Balance máximo
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

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_apply = QPushButton('Aplicar Filtro')
        self.btn_cancel = QPushButton('Cancelar')

        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Conectar señales
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_cancel.clicked.connect(self.reject)

    def _on_apply(self):
        """Valida y acepta el diálogo"""
        min_val = self.spin_min.value()
        max_val = self.spin_max.value()

        if min_val > max_val:
            QMessageBox.warning(self, 'Validación',
                              'El balance mínimo no puede ser mayor que el máximo')
            return

        self.accept()

    def get_filter_params(self) -> dict:
        """
        Obtiene los parámetros del filtro

        Returns:
            dict: Diccionario con balance_min y balance_max
        """
        return {
            'balance_min': self.spin_min.value(),
            'balance_max': self.spin_max.value()
        }


class AccountTypeFilterDialog(QDialog):
    """
    Diálogo para filtrar cuentas por tipo
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Tipo de Cuenta')
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()

        # Grupo de filtro
        group = QGroupBox("Tipo de Cuenta")
        grid = QGridLayout()

        # Combo de tipo
        grid.addWidget(QLabel('Seleccionar Tipo:'), 0, 0)
        self.combo_type = QComboBox()
        self.combo_type.addItems(['Todas', 'Cuentas Normales', 'Cuentas de Crédito'])
        grid.addWidget(self.combo_type, 0, 1)

        # Información adicional
        info_label = QLabel(
            'Filtra las cuentas según su tipo:\n\n'
            '• Todas: Muestra todas las cuentas\n'
            '• Cuentas Normales: Solo cuentas sin crédito\n'
            '• Cuentas de Crédito: Solo cuentas con límite de crédito'
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet('QLabel { padding: 10px; background-color: #ffe082; color: #222; font-weight: bold; border-radius: 5px; }')
        grid.addWidget(info_label, 1, 0, 1, 2)

        group.setLayout(grid)
        layout.addWidget(group)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_apply = QPushButton('Aplicar Filtro')
        self.btn_cancel = QPushButton('Cancelar')

        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Conectar señales
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def get_filter_params(self) -> dict:
        """
        Obtiene los parámetros del filtro

        Returns:
            dict: Diccionario con tipo
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
    Diálogo para filtrar cuentas por fecha y/o lugar
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Fecha y Lugar')
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()

        # Grupo de fecha
        group_fecha = QGroupBox("Rango de Fechas")
        grid_fecha = QGridLayout()

        # Fecha inicio
        grid_fecha.addWidget(QLabel('Fecha Inicio:'), 0, 0)
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDisplayFormat('yyyy-MM-dd')
        self.date_inicio.setDate(QDate.currentDate().addYears(-1))
        grid_fecha.addWidget(self.date_inicio, 0, 1)

        # Fecha fin
        grid_fecha.addWidget(QLabel('Fecha Fin:'), 1, 0)
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDisplayFormat('yyyy-MM-dd')
        self.date_fin.setDate(QDate.currentDate())
        grid_fecha.addWidget(self.date_fin, 1, 1)

        # Checkbox para habilitar filtro de fecha
        from PyQt5.QtWidgets import QCheckBox
        self.chk_use_dates = QCheckBox('Aplicar filtro de fechas')
        self.chk_use_dates.setChecked(False)
        self.chk_use_dates.toggled.connect(self._toggle_dates)
        grid_fecha.addWidget(self.chk_use_dates, 2, 0, 1, 2)

        group_fecha.setLayout(grid_fecha)
        layout.addWidget(group_fecha)

        # Grupo de lugar
        group_lugar = QGroupBox("Lugar")
        grid_lugar = QGridLayout()

        # Campo de lugar
        grid_lugar.addWidget(QLabel('Buscar en Lugar:'), 0, 0)
        self.le_lugar = QLineEdit()
        self.le_lugar.setPlaceholderText('Ejemplo: Ciudad de México, Guadalajara...')
        grid_lugar.addWidget(self.le_lugar, 0, 1)

        # Información
        info_label = QLabel(
            'La búsqueda es sensible a mayúsculas/minúsculas.\n'
            'Se buscarán coincidencias parciales.'
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet('QLabel { padding: 5px; font-size: 9pt; color: #666; }')
        grid_lugar.addWidget(info_label, 1, 0, 1, 2)

        group_lugar.setLayout(grid_lugar)
        layout.addWidget(group_lugar)

        # Botones
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

        # Estado inicial
        self._toggle_dates(False)

        # Conectar señales
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_clear.clicked.connect(self._on_clear)

    def _toggle_dates(self, enabled):
        """Habilita/deshabilita controles de fecha"""
        self.date_inicio.setEnabled(enabled)
        self.date_fin.setEnabled(enabled)

    def _on_apply(self):
        """Valida y acepta el diálogo"""
        if self.chk_use_dates.isChecked():
            fecha_inicio = self.date_inicio.date()
            fecha_fin = self.date_fin.date()

            if fecha_inicio > fecha_fin:
                QMessageBox.warning(self, 'Validación',
                                  'La fecha de inicio no puede ser posterior a la fecha fin')
                return

        # Verificar que al menos un filtro esté activo
        if not self.chk_use_dates.isChecked() and not self.le_lugar.text().strip():
            QMessageBox.information(self, 'Información',
                                  'Debe activar al menos un filtro (fecha o lugar)')
            return

        self.accept()

    def _on_clear(self):
        """Limpia los controles"""
        self.chk_use_dates.setChecked(False)
        self.le_lugar.clear()
        self.date_inicio.setDate(QDate.currentDate().addYears(-1))
        self.date_fin.setDate(QDate.currentDate())

    def get_filter_params(self) -> dict:
        """
        Obtiene los parámetros del filtro

        Returns:
            dict: Diccionario con fecha_inicio, fecha_fin, lugar
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
