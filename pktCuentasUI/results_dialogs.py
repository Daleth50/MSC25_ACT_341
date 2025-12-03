"""
Results Dialog Module
Diálogos para mostrar resultados de filtros y gráficas
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QTextEdit,
                             QGroupBox, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class ChartDialog(QDialog):
    """
    Diálogo para mostrar gráficas de Matplotlib
    """

    def __init__(self, figure, title="Gráfica", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1000, 700)
        self.figure = figure
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()

        # Canvas de matplotlib
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Toolbar de navegación
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_save = QPushButton('Guardar Imagen')
        self.btn_close = QPushButton('Cerrar')

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Conectar señales
        self.btn_save.clicked.connect(self._save_figure)
        self.btn_close.clicked.connect(self.accept)

    def _save_figure(self):
        """Guarda la figura como imagen"""
        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Gráfica",
            "grafica.png",
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
    Diálogo para mostrar resultados de filtros aplicados
    """

    def __init__(self, df, filter_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Resultados: {filter_name}')
        self.setMinimumSize(1000, 600)
        self.df = df
        self.filter_name = filter_name
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()

        # Estadísticas
        stats_group = QGroupBox("Estadísticas del Filtro")
        stats_layout = QVBoxLayout()

        stats_text = self._generate_statistics()
        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        stats_label.setStyleSheet('QLabel { padding: 10px; background-color: #ffe082; color: #222; font-weight: bold; border-radius: 5px; }')
        stats_layout.addWidget(stats_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Tabla de resultados
        results_group = QGroupBox("Cuentas Encontradas")
        results_layout = QVBoxLayout()

        self.table = QTableWidget()
        self._populate_table()
        results_layout.addWidget(self.table)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_export = QPushButton('Exportar a CSV')
        self.btn_close = QPushButton('Cerrar')

        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Conectar señales
        self.btn_export.clicked.connect(self._export_results)
        self.btn_close.clicked.connect(self.accept)

    def _generate_statistics(self) -> str:
        """Genera texto con estadísticas del filtro"""
        from pktCuentas.analytics import Analytics

        if self.df.empty:
            return "No se encontraron resultados para este filtro."

        stats = Analytics.obtener_estadisticas(self.df)

        text = f"<b>Total de cuentas:</b> {stats['total_cuentas']}<br>"
        text += f"<b>Balance total:</b> ${stats['balance_total']:,.2f}<br>"
        text += f"<b>Balance promedio:</b> ${stats['balance_promedio']:,.2f}<br>"
        text += f"<b>Balance mínimo:</b> ${stats['balance_min']:,.2f}<br>"
        text += f"<b>Balance máximo:</b> ${stats['balance_max']:,.2f}<br>"

        if 'cuentas_normales' in stats:
            text += f"<b>Cuentas normales:</b> {stats['cuentas_normales']}<br>"
            text += f"<b>Cuentas de crédito:</b> {stats['cuentas_credito']}<br>"

        if 'credito_total' in stats:
            text += f"<b>Crédito total:</b> ${stats['credito_total']:,.2f}<br>"
            text += f"<b>Crédito promedio:</b> ${stats['credito_promedio']:,.2f}<br>"

        return text

    def _populate_table(self):
        """Puebla la tabla con los resultados"""
        if self.df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        # Configurar columnas
        columns = ['No. Cuenta', 'Nombre Completo', 'Balance', 'Tipo', 'Límite Crédito', 'Fecha', 'Lugar']
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Configurar filas
        self.table.setRowCount(len(self.df))

        # Llenar datos
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

        # Ajustar columnas
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Configuración de la tabla
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)

    def _export_results(self):
        """Exporta los resultados a CSV"""
        from PyQt5.QtWidgets import QFileDialog
        import pandas as pd

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
                # Preparar DataFrame para exportación
                df_export = self.df[['no_cuenta', 'apellido_paterno', 'apellido_materno',
                                    'nombre', 'balance', 'fecha', 'lugar',
                                    'tipo_cuenta', 'limite_credito']].copy()
                df_export.to_csv(file_path, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, 'Éxito', f'Resultados exportados a:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al exportar:\n{str(e)}')


class ImportResultDialog(QDialog):
    """
    Diálogo para mostrar resultados de importación CSV
    """

    def __init__(self, resultado, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Resultado de Importación')
        self.setMinimumSize(600, 400)
        self.resultado = resultado
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()

        # Resumen
        summary_group = QGroupBox("Resumen de Importación")
        summary_layout = QVBoxLayout()

        exitosos = self.resultado['exitosos']
        duplicados = len(self.resultado['duplicados'])
        errores = len(self.resultado['errores'])
        total = exitosos + duplicados + errores

        summary_text = f"""
        <b>Total de registros procesados:</b> {total}<br>
        <b style='color: green;'>Registros importados exitosamente:</b> {exitosos}<br>
        <b style='color: orange;'>Registros duplicados (omitidos):</b> {duplicados}<br>
        <b style='color: red;'>Registros con errores:</b> {errores}
        """

        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet('QLabel { padding: 15px; background-color: #ffe082; color: #222; font-weight: bold; border-radius: 5px; }')
        summary_layout.addWidget(summary_label)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Detalles de errores y duplicados
        if duplicados > 0 or errores > 0:
            details_group = QGroupBox("Detalles")
            details_layout = QVBoxLayout()

            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)

            details_content = ""

            if duplicados > 0:
                details_content += "<b>Cuentas Duplicadas:</b><br>"
                for no_cuenta in self.resultado['duplicados']:
                    details_content += f"  • Cuenta {no_cuenta} ya existe en la base de datos<br>"
                details_content += "<br>"

            if errores > 0:
                details_content += "<b>Errores Encontrados:</b><br>"
                for error in self.resultado['errores']:
                    details_content += f"  • {error}<br>"

            self.details_text.setHtml(details_content)
            details_layout.addWidget(self.details_text)

            details_group.setLayout(details_layout)
            layout.addWidget(details_group)

        # Botón cerrar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_close = QPushButton('Cerrar')
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Conectar señales
        self.btn_close.clicked.connect(self.accept)
