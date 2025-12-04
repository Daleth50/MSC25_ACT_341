from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGroupBox, QRadioButton
from PyQt5.QtCore import Qt

class ReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Reportes')
        self.setMinimumSize(400, 300)
        self.selected_report = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        title = QLabel('Seleccione el tipo de gráfica que desea ver:')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 16px; font-weight: bold; margin-bottom: 10px;')
        layout.addWidget(title)

        group = QGroupBox('Opciones de gráficas')
        group_layout = QVBoxLayout()
        self.radio_hist = QRadioButton('Distribución de saldos')
        self.radio_pie = QRadioButton('Distribución por tipo de cuenta')
        self.radio_time = QRadioButton('Tendencia temporal de apertura de cuentas')
        self.radio_credit = QRadioButton('Comparación balance vs límite de crédito (solo crédito)')
        group_layout.addWidget(self.radio_hist)
        group_layout.addWidget(self.radio_pie)
        group_layout.addWidget(self.radio_time)
        group_layout.addWidget(self.radio_credit)
        group.setLayout(group_layout)
        layout.addWidget(group)

        # Select a sensible default so the user can click "Ver gráfica" right away
        self.radio_hist.setChecked(True)

        btn_layout = QHBoxLayout()
        self.btn_show = QPushButton('Ver gráfica')
        self.btn_cancel = QPushButton('Cancelar')
        btn_layout.addWidget(self.btn_show)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.btn_show.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def get_selected_report(self):
        if self.radio_hist.isChecked():
            return 'hist'
        elif self.radio_pie.isChecked():
            return 'pie'
        elif self.radio_time.isChecked():
            return 'time'
        elif self.radio_credit.isChecked():
            return 'credit'
        return None
