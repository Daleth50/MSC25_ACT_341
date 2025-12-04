from PyQt5.QtWidgets import (QDialog, QLabel, QDoubleSpinBox, QComboBox,
                             QPushButton, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QMessageBox, QGroupBox)


class BalanceFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Rango de Balance')
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        group = QGroupBox("Rango de Balance")
        grid = QGridLayout()
        grid.addWidget(QLabel('Balance Mínimo:'), 0, 0)
        self.spin_min = QDoubleSpinBox()
        self.spin_min.setRange(0.0, 1e12)
        self.spin_min.setValue(0.0)
        self.spin_min.setPrefix('$ ')
        self.spin_min.setDecimals(2)
        self.spin_min.setGroupSeparatorShown(True)
        grid.addWidget(self.spin_min, 0, 1)
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
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_apply = QPushButton('Aplicar Filtro')
        self.btn_cancel = QPushButton('Cancelar')
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_cancel.clicked.connect(self.reject)

    def _on_apply(self):
        min_val = self.spin_min.value()
        max_val = self.spin_max.value()

        if min_val > max_val:
            QMessageBox.warning(self, 'Validación', 'El balance mínimo no puede ser mayor que el máximo')
            return

        self.accept()

    def get_filter_params(self) -> dict:
        return {
            'balance_min': self.spin_min.value(),
            'balance_max': self.spin_max.value()
        }


class AccountTypeFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Tipo de Cuenta')
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        group = QGroupBox("Tipo de Cuenta")
        grid = QGridLayout()
        grid.addWidget(QLabel('Seleccionar Tipo:'), 0, 0)
        self.combo_type = QComboBox()
        self.combo_type.addItems(['Todas', 'Cuentas Normales', 'Cuentas de Crédito'])
        grid.addWidget(self.combo_type, 0, 1)
        info_label = QLabel(
            'Filter accounts by type:\n\n'
            '• Todas: Show all accounts\n'
            '• Cuentas Normales: Only accounts without credit\n'
            '• Cuentas de Crédito: Only accounts with credit limit'
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            'QLabel { padding: 10px; background-color: #fff; color: #222; font-weight: bold; border-radius: 5px; }')
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
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def get_filter_params(self) -> dict:
        tipo_map = {
            0: 'todas',
            1: 'normal',
            2: 'credit'
        }

        return {
            'tipo': tipo_map[self.combo_type.currentIndex()]
        }


class PlaceFilterDialog(QDialog):
    def __init__(self, parent=None, locations: list | None = None):
        super().__init__(parent)
        self.setWindowTitle('Filtrar por Lugar')
        self.setMinimumWidth(380)
        self._locations = locations or []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        group_lugar = QGroupBox("Lugar")
        grid_lugar = QGridLayout()
        grid_lugar.addWidget(QLabel('Seleccionar Lugar:'), 0, 0)
        self.place_combo_box = QComboBox()
        self.place_combo_box.setEditable(False)
        grid_lugar.addWidget(self.place_combo_box, 0, 1)

        info_label = QLabel(
            'Seleccione una ubicación del listado.'
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet('QLabel { padding: 5px; font-size: 9pt; color: #666; }')
        grid_lugar.addWidget(info_label, 1, 0, 1, 2)

        group_lugar.setLayout(grid_lugar)
        layout.addWidget(group_lugar)
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
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_clear.clicked.connect(self._on_clear)
        self.set_location_options(self._locations)

    def set_location_options(self, locations: list):
        self.place_combo_box.clear()
        if not locations:
            return
        for loc in locations:
            if loc is None:
                continue
            s = str(loc).strip()
            if s not in [self.place_combo_box.itemText(i) for i in range(self.place_combo_box.count())]:
                self.place_combo_box.addItem(s)

    def _on_apply(self):
        if self.place_combo_box.currentText().strip().lower() in (''):
            QMessageBox.information(self, 'Información', 'Debe seleccionar un lugar o cancelar')
            return

        self.accept()

    def _on_clear(self):
        if self.place_combo_box.count() > 0:
            self.place_combo_box.setCurrentIndex(0)

    def get_filter_params(self) -> dict:
        params = {
            'lugar': None
        }

        sel = self.place_combo_box.currentText().strip()
        if sel and sel.lower() not in ('todas', ''):
            params['lugar'] = sel

        return params
