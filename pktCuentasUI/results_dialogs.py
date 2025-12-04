from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QTextEdit,
                             QGroupBox, QHeaderView, QMessageBox, QFileDialog)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ChartDialog(QDialog):
    """
    Dialog to show Matplotlib charts
    """

    def __init__(self, figure, title="Chart", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1000, 700)
        self.figure = figure
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_save = QPushButton('Guardar Imagen')
        self.btn_close = QPushButton('Cerrar')
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.btn_save.clicked.connect(self._save_figure)
        self.btn_close.clicked.connect(self.accept)

    def _save_figure(self):
        from PyQt5.QtWidgets import QFileDialog
        import datetime
        chart_type = self.windowTitle().replace(' ', '_').lower()
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"grafica_{chart_type}_{now}.png"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Gráfica",
            default_name,
            "PNG (*.png);;PDF (*.pdf);;SVG (*.svg);;Todos los archivos (*)"
        )
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, 'Éxito', f'Gráfica guardada en:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al guardar gráfica:\n{str(e)}')


class FilterResultDialog(QDialog):
    """
    Dialog to show filter results
    """

    def __init__(self, df, filter_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Resultados: {filter_name}')
        self.setMinimumSize(1000, 600)
        self.df = df
        self.filter_name = filter_name
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        stats_group = QGroupBox("Estadísticas del Filtro")
        stats_layout = QVBoxLayout()
        stats_text = self._generate_statistics()
        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        stats_label.setStyleSheet('QLabel { padding: 10px; background-color: #fff; color: #222; font-weight: bold; border-radius: 5px; }')
        stats_layout.addWidget(stats_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        results_group = QGroupBox("Cuentas Encontradas")
        results_layout = QVBoxLayout()
        self.table = QTableWidget()
        self._populate_table()
        results_layout.addWidget(self.table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_export = QPushButton('Exportar a CSV')
        self.btn_close = QPushButton('Cerrar')
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.btn_export.clicked.connect(self._export_results)
        self.btn_close.clicked.connect(self.accept)

    def _generate_statistics(self) -> str:
        from pktCuentas.analytics import Analytics
        if self.df.empty:
            return "No se encontraron resultados para este filtro."
        stats = Analytics.get_statistics(self.df)
        text = f"<b>Total de cuentas:</b> {stats.get('total_accounts', 0)}<br>"
        text += f"<b>Balance total:</b> ${stats.get('total_balance', 0.0):,.2f}<br>"
        text += f"<b>Balance promedio:</b> ${stats.get('average_balance', 0.0):,.2f}<br>"
        text += f"<b>Balance mínimo:</b> ${stats.get('min_balance', 0.0):,.2f}<br>"
        text += f"<b>Balance máximo:</b> ${stats.get('max_balance', 0.0):,.2f}<br>"
        if 'normal_accounts' in stats:
            text += f"<b>Cuentas normales:</b> {stats.get('normal_accounts', 0)}<br>"
            text += f"<b>Cuentas de crédito:</b> {stats.get('credit_accounts', 0)}<br>"
        if 'total_credit' in stats:
            text += f"<b>Crédito total:</b> ${stats.get('total_credit', 0.0):,.2f}<br>"
            text += f"<b>Crédito promedio:</b> ${stats.get('average_credit', 0.0):,.2f}<br>"
        return text

    def _populate_table(self):
        if self.df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        columns = ['No. Cuenta', 'Nombre Completo', 'Balance', 'Tipo', 'Límite Crédito', 'Fecha', 'Lugar']
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(self.df))
        for idx, row in self.df.iterrows():
            self.table.setItem(idx, 0, QTableWidgetItem(str(row['no_cuenta'])))
            self.table.setItem(idx, 1, QTableWidgetItem(row['nombre_completo']))
            self.table.setItem(idx, 2, QTableWidgetItem(f"${row['balance']:,.2f}"))
            tipo_text = 'Crédito' if row['tipo_cuenta'] == 'credit' else 'Normal'
            self.table.setItem(idx, 3, QTableWidgetItem(tipo_text))
            credito_text = f"${row['limite_credito']:,.2f}" if row['tipo_cuenta'] == 'credit' else 'N/A'
            self.table.setItem(idx, 4, QTableWidgetItem(credito_text))
            fecha_text = row['fecha'].strftime('%Y-%m-%d') if row['fecha'] is not None else 'N/A'
            self.table.setItem(idx, 5, QTableWidgetItem(fecha_text))
            self.table.setItem(idx, 6, QTableWidgetItem(row['lugar']))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)

    def _export_results(self):
        if self.df.empty:
            QMessageBox.information(self, 'Información', 'No hay datos para exportar')
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Resultados",
            f"filtro_{self.filter_name.lower().replace(' ', '_')}.csv",
            "CSV (*.csv);;Todos los archivos (*)"
        )
        if file_path:
            try:
                df_export = self.df[['no_cuenta', 'apellido_paterno', 'apellido_materno',
                                    'nombre', 'balance', 'fecha', 'lugar',
                                    'tipo_cuenta', 'limite_credito']].copy()
                df_export.to_csv(file_path, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, 'Éxito', f'Resultados exportados a:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al exportar:\n{str(e)}')


class ImportResultDialog(QDialog):
    """
    Dialog to show CSV import results
    """

    def __init__(self, resultado, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Resultado de Importación')
        self.setMinimumSize(600, 400)
        self.resultado = resultado
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        summary_group = QGroupBox("Resumen de Importación")
        summary_layout = QVBoxLayout()
        success = self.resultado.get('success', 0)
        duplicates = len(self.resultado.get('duplicates', []))
        errors = len(self.resultado.get('errors', []))
        total = success + duplicates + errors
        summary_text = f"""
        <b>Total de registros procesados:</b> {total}<br>
        <b style='color: green;'>Registros importados exitosamente:</b> {success}<br>
        <b style='color: orange;'>Registros duplicados (omitidos):</b> {duplicates}<br>
        <b style='color: red;'>Registros con errores:</b> {errors}
        """
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet('QLabel { padding: 15px; background-color: #fff; color: #222; font-weight: bold; border-radius: 5px; }')
        summary_layout.addWidget(summary_label)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        if duplicates > 0 or errors > 0:
            details_group = QGroupBox("Detalles")
            details_layout = QVBoxLayout()
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            details_content = ""
            if duplicates > 0:
                details_content += "<b>Cuentas Duplicadas:</b><br>"
                for account_no in self.resultado.get('duplicates', []):
                    details_content += f"  • La cuenta {account_no} ya existe<br>"
                details_content += "<br>"
            if errors > 0:
                details_content += "<b>Errores Encontrados:</b><br>"
                for error in self.resultado.get('errors', []):
                    details_content += f"  • {error}<br>"
            self.details_text.setHtml(details_content)
            details_layout.addWidget(self.details_text)
            details_group.setLayout(details_layout)
            layout.addWidget(details_group)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_close = QPushButton('Cerrar')
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.btn_close.clicked.connect(self.accept)
