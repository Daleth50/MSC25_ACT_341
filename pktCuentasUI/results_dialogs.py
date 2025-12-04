import pandas as pd
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel,
                             QGroupBox, QHeaderView, QMessageBox, QFileDialog)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ChartDialog(QDialog):
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
    def __init__(self, df, filter_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Resultados: {filter_name}')
        self.setMinimumSize(1000, 600)
        self.df = pd.DataFrame() if df is None else df.copy()
        self.filter_name = filter_name
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        stats_group = QGroupBox("Estadísticas del Filtro")
        stats_layout = QVBoxLayout()
        stats_text = self._generate_statistics()
        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        stats_label.setStyleSheet(
            'QLabel { padding: 10px; background-color: #fff; color: #222; font-weight: bold; border-radius: 5px; }')
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
        columns = ['No. Cuenta', 'Cliente', 'Saldo', 'Tipo', 'Crédito', 'Fecha', 'Lugar']
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(self.df))

        for i in range(len(self.df)):
            row = self.df.iloc[i]
            acct_no = row.get('account_no', '')
            self.table.setItem(i, 0, QTableWidgetItem(str(acct_no)))
            full_name = row.get('full_name') if 'full_name' in self.df.columns else None
            if not full_name:
                parts = []
                for k in ('last_name', 'middle_name', 'first_name'):
                    if k in self.df.columns and pd.notna(row.get(k)):
                        parts.append(str(row.get(k)).strip())
                full_name = ' '.join(parts).strip()
            self.table.setItem(i, 1, QTableWidgetItem(full_name if full_name else ''))
            bal = row.get('balance', 0.0)
            try:
                bal = float(bal)
            except Exception:
                bal = 0.0
            self.table.setItem(i, 2, QTableWidgetItem(f"${bal:,.2f}"))
            tipo_text = 'Crédito' if str(row.get('account_type', '')).lower() == 'credit' else 'Normal'
            self.table.setItem(i, 3, QTableWidgetItem(tipo_text))
            credit_limit = row.get('credit_limit', 0.0)
            try:
                credit_limit = float(credit_limit)
            except Exception:
                credit_limit = 0.0
            credito_text = f"${credit_limit:,.2f}" if str(row.get('account_type', '')).lower() == 'credit' else 'N/A'
            self.table.setItem(i, 4, QTableWidgetItem(credito_text))
            date_val = row.get('date', None)
            try:
                if pd.isna(date_val) or date_val is None or str(date_val) == '':
                    date_text = 'N/A'
                else:
                    if hasattr(date_val, 'strftime'):
                        date_text = date_val.strftime('%Y-%m-%d')
                    else:
                        parsed = pd.to_datetime(date_val, errors='coerce')
                        date_text = parsed.strftime('%Y-%m-%d') if not pd.isna(parsed) else 'N/A'
            except Exception:
                date_text = 'N/A'
            self.table.setItem(i, 5, QTableWidgetItem(date_text))
            loc = row.get('location', '') if 'location' in self.df.columns and row.get('location') else ''
            self.table.setItem(i, 6, QTableWidgetItem(loc))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
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
            f"filter_{self.filter_name.lower().replace(' ', '_')}.csv",
            "CSV (*.csv);;Todos los archivos (*)"
        )
        if file_path:
            try:
                df_export = self.df[[
                    'account_no', 'last_name', 'middle_name', 'first_name',
                    'balance', 'date', 'location', 'account_type', 'credit_limit'
                ]].copy()
                df_export.to_csv(file_path, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, 'Éxito', f'Resultados exportados a:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al exportar:\n{str(e)}')


class ImportResultDialog(QDialog):
    def __init__(self, resultado, parent=None):
        super().__init__(parent)
        self.resultado = resultado or {}
        self.setWindowTitle('Resultado de Importación')

    def exec_(self):
        success = self.resultado.get('success', 0)
        duplicates_list = self.resultado.get('duplicates', [])
        errors_list = self.resultado.get('errors', [])
        duplicates = len(duplicates_list)
        errors = len(errors_list)
        total = success + duplicates + errors

        summary = (
            f"Total registros procesados: {total}\n"
            f"Importados exitosamente: {success}\n"
            f"Duplicados (omitidos): {duplicates}\n"
            f"Errores: {errors}"
        )

        details = []
        if duplicates > 0:
            details.append('Cuentas duplicadas:')
            details.extend(str(x) for x in duplicates_list)
        if errors > 0:
            details.append('Errores encontrados:')
            details.extend(str(x) for x in errors_list)

        detailed_text = "\n".join(details) if details else ''
        parent_widget = None
        if self.parent() is not None:
            try:
                parent_widget = self.parent().window()
            except Exception:
                parent_widget = self.parent()
        if parent_widget is None:
            parent_widget = QApplication.activeWindow()

        msg = QMessageBox(parent_widget)
        if errors > 0:
            msg.setIcon(QMessageBox.Critical)
        elif duplicates > 0:
            msg.setIcon(QMessageBox.Warning)
        else:
            msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(self.windowTitle())
        msg.setText(summary)
        if detailed_text:
            msg.setDetailedText(detailed_text)
        msg.setStandardButtons(QMessageBox.Ok)

        try:
            if parent_widget is not None:
                msg.setWindowModality(Qt.WindowModal)
                parent_geo = parent_widget.frameGeometry()
                parent_center = parent_geo.center()
                size = msg.sizeHint()
                top_left = QPoint(parent_center.x() - size.width() // 2,
                                  parent_center.y() - size.height() // 2)
                msg.move(top_left)
        except Exception:
            pass

        msg.exec_()
        return QDialog.Accepted
