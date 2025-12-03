"""
Charts Module
Generación de gráficas con Matplotlib y Seaborn
Implementa tres tipos de visualizaciones diferentes
"""

from typing import List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure
from pktCuentas.analytics import Analytics


class ChartGenerator:
    """
    Generates charts for account data using matplotlib and seaborn.
    """

    # Configuración de estilo
    @staticmethod
    def _configure_style():
        """Configura el estilo visual de las gráficas"""
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")

    @staticmethod
    def generate_balance_histogram(accounts: List) -> Figure:
        """
        Generate a histogram of account balances.

        Args:
            accounts: Lista de objetos Account

        Returns:
            Figure: Objeto Figure de matplotlib
        """
        ChartGenerator._configure_style()

        # Convertir a DataFrame
        df = Analytics.cuentas_to_dataframe(accounts)

        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Distribución de Saldos')
            return fig

        # Crear figura
        fig, ax = plt.subplots(figsize=(12, 7))

        # Crear histograma con seaborn
        sns.histplot(data=df, x='balance', bins=20, kde=True, ax=ax,
                    color='skyblue', edgecolor='black', alpha=0.7)

        # Agregar línea vertical para el promedio
        promedio = df['balance'].mean()
        ax.axvline(promedio, color='red', linestyle='--', linewidth=2,
                  label=f'Promedio: ${promedio:,.2f}')

        # Agregar línea vertical para la mediana
        mediana = df['balance'].median()
        ax.axvline(mediana, color='green', linestyle='--', linewidth=2,
                  label=f'Mediana: ${mediana:,.2f}')

        # Configurar etiquetas y título
        ax.set_xlabel('Saldo', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frecuencia', fontsize=12, fontweight='bold')
        ax.set_title('Distribución de Saldos de Cuentas', fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # Formatear eje X con formato de moneda
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Agregar estadísticas en el gráfico
        stats_text = f'Total cuentas: {len(df)}\n'
        stats_text += f'Mín: ${df["balance"].min():,.2f}\n'
        stats_text += f'Máx: ${df["balance"].max():,.2f}\n'
        stats_text += f'Desv. Est.: ${df["balance"].std():,.2f}'

        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
               fontsize=9)

        plt.tight_layout()
        return fig

    @staticmethod
    def generate_account_type_pie(accounts: List) -> Figure:
        """
        Generate a pie chart of account types.

        Args:
            accounts: Lista de objetos Account

        Returns:
            Figure: Objeto Figure de matplotlib
        """
        ChartGenerator._configure_style()

        # Convertir a DataFrame
        df = Analytics.cuentas_to_dataframe(accounts)

        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Distribución por Tipo de Cuenta')
            return fig

        # Crear figura con dos subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Gráfica 1: Distribución por cantidad
        tipo_counts = df['tipo_cuenta'].value_counts()

        colores = ['#ff9999', '#66b3ff']
        explode = (0.05, 0.05)

        wedges, texts, autotexts = ax1.pie(tipo_counts,
                                           labels=['Cuenta Normal', 'Cuenta de Crédito'],
                                           autopct='%1.1f%%',
                                           startangle=90,
                                           colors=colores,
                                           explode=explode,
                                           shadow=True)

        # Mejorar apariencia del texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)

        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')

        ax1.set_title('Distribución por Cantidad de Cuentas',
                     fontsize=13, fontweight='bold', pad=20)

        # Agregar leyenda con totales
        legend_labels = [f'{label}: {count} cuentas'
                        for label, count in zip(['Normal', 'Crédito'], tipo_counts)]
        ax1.legend(legend_labels, loc='upper left', fontsize=10)

        # Gráfica 2: Distribución por saldo total
        saldo_por_tipo = df.groupby('tipo_cuenta')['balance'].sum()

        wedges2, texts2, autotexts2 = ax2.pie(saldo_por_tipo,
                                              labels=['Cuenta Normal', 'Cuenta de Crédito'],
                                              autopct=lambda pct: f'${pct*saldo_por_tipo.sum()/100:,.0f}\n({pct:.1f}%)',
                                              startangle=90,
                                              colors=colores,
                                              explode=explode,
                                              shadow=True)

        for autotext in autotexts2:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        for text in texts2:
            text.set_fontsize(11)
            text.set_fontweight('bold')

        ax2.set_title('Distribución por Saldo Total',
                     fontsize=13, fontweight='bold', pad=20)

        # Agregar leyenda con totales
        legend_labels2 = [f'{label}: ${saldo:,.2f}'
                         for label, saldo in zip(['Normal', 'Crédito'], saldo_por_tipo)]
        ax2.legend(legend_labels2, loc='upper left', fontsize=10)

        plt.tight_layout()
        return fig

    @staticmethod
    def generate_temporal_trend(accounts: List) -> Figure:
        """
        Generate a line chart showing account creation over time.

        Args:
            accounts: Lista de objetos Account

        Returns:
            Figure: Objeto Figure de matplotlib
        """
        ChartGenerator._configure_style()

        # Convertir a DataFrame
        df = Analytics.cuentas_to_dataframe(accounts)

        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Tendencia Temporal de Apertura de Cuentas')
            return fig

        # Filtrar cuentas con fecha
        df_con_fecha = df[df['fecha'].notna()].copy()

        if df_con_fecha.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos de fechas para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Tendencia Temporal de Apertura de Cuentas')
            return fig

        # Crear figura con dos subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Ordenar por fecha
        df_con_fecha = df_con_fecha.sort_values('fecha')

        # Gráfica 1: Cuentas acumuladas por tipo
        df_con_fecha['contador'] = 1
        df_con_fecha['cuentas_acumuladas'] = df_con_fecha['contador'].cumsum()

        # Separar por tipo
        df_normal = df_con_fecha[df_con_fecha['tipo_cuenta'] == 'normal'].copy()
        df_credit = df_con_fecha[df_con_fecha['tipo_cuenta'] == 'credit'].copy()

        # Calcular acumulados por tipo
        if not df_normal.empty:
            df_normal['acum_tipo'] = df_normal['contador'].cumsum()
            ax1.plot(df_normal['fecha'], df_normal['acum_tipo'],
                    marker='o', linestyle='-', linewidth=2, markersize=6,
                    label='Cuentas Normales', color='#ff9999')

        if not df_credit.empty:
            df_credit['acum_tipo'] = df_credit['contador'].cumsum()
            ax1.plot(df_credit['fecha'], df_credit['acum_tipo'],
                    marker='s', linestyle='-', linewidth=2, markersize=6,
                    label='Cuentas de Crédito', color='#66b3ff')

        # Total acumulado
        ax1.plot(df_con_fecha['fecha'], df_con_fecha['cuentas_acumuladas'],
                marker='D', linestyle='--', linewidth=2, markersize=5,
                label='Total Acumulado', color='green', alpha=0.7)

        ax1.set_xlabel('Fecha', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Número de Cuentas Acumuladas', fontsize=11, fontweight='bold')
        ax1.set_title('Cuentas Acumuladas por Tipo', fontsize=13, fontweight='bold', pad=15)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Rotar etiquetas del eje X
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Gráfica 2: Balance promedio por mes
        df_con_fecha['year_month'] = df_con_fecha['fecha'].dt.to_period('M')
        balance_por_mes = df_con_fecha.groupby('year_month').agg({
            'balance': ['mean', 'sum', 'count']
        }).reset_index()

        balance_por_mes.columns = ['year_month', 'balance_promedio', 'balance_total', 'cantidad']
        balance_por_mes['year_month_str'] = balance_por_mes['year_month'].astype(str)

        # Crear gráfica de barras y línea
        ax2_twin = ax2.twinx()

        x_pos = np.arange(len(balance_por_mes))
        bars = ax2.bar(x_pos, balance_por_mes['balance_promedio'],
                      alpha=0.6, color='skyblue', label='Balance Promedio')
        line = ax2_twin.plot(x_pos, balance_por_mes['cantidad'],
                            color='red', marker='o', linewidth=2, markersize=8,
                            label='Cantidad de Cuentas')

        ax2.set_xlabel('Mes', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Balance Promedio ($)', fontsize=11, fontweight='bold', color='blue')
        ax2_twin.set_ylabel('Cantidad de Cuentas', fontsize=11, fontweight='bold', color='red')
        ax2.set_title('Balance Promedio y Cantidad por Mes', fontsize=13, fontweight='bold', pad=15)

        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(balance_por_mes['year_month_str'], rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')

        # Formatear eje Y con formato de moneda
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Combinar leyendas
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

        plt.tight_layout()
        return fig

    @staticmethod
    def generate_credit_comparison(accounts: List) -> Figure:
        """
        Generate a bar chart comparing balance and credit limit for credit accounts.

        Args:
            accounts: Lista de objetos Account

        Returns:
            Figure: Objeto Figure de matplotlib
        """
        ChartGenerator._configure_style()

        # Convertir a DataFrame
        df = Analytics.cuentas_to_dataframe(accounts)

        # Filtrar solo cuentas de crédito
        df_credito = df[df['tipo_cuenta'] == 'credit'].copy()

        if df_credito.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay cuentas de crédito para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Análisis de Cuentas de Crédito')
            return fig

        # Crear figura
        fig, ax = plt.subplots(figsize=(12, 7))

        # Crear gráfica de barras agrupadas
        x_pos = np.arange(len(df_credito))
        width = 0.35

        bars1 = ax.bar(x_pos - width/2, df_credito['balance'], width,
                      label='Balance', color='#66b3ff', alpha=0.8)
        bars2 = ax.bar(x_pos + width/2, df_credito['limite_credito'], width,
                      label='Límite de Crédito', color='#ff9999', alpha=0.8)

        # Agregar etiquetas
        ax.set_xlabel('Cuenta', fontsize=12, fontweight='bold')
        ax.set_ylabel('Monto ($)', fontsize=12, fontweight='bold')
        ax.set_title('Comparación: Balance vs Límite de Crédito',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df_credito['no_cuenta'], rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        # Formatear eje Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Agregar valores encima de las barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}',
                       ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        return fig

