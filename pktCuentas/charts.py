from typing import List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure
from pktCuentas.analytics import Analytics


class ChartGenerator:
    @staticmethod
    def _configure_style():
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")

    @staticmethod
    def generate_balance_histogram(accounts: List) -> Figure:
        ChartGenerator._configure_style()
        df = Analytics.accounts_to_dataframe(accounts)
        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Distribución de Saldos')
            return fig
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.histplot(data=df, x='balance', bins=20, kde=True, ax=ax,
                    color='skyblue', edgecolor='black', alpha=0.7)
        promedio = df['balance'].mean()
        ax.axvline(promedio, color='red', linestyle='--', linewidth=2,
                  label=f'Promedio: ${promedio:,.2f}')
        mediana = df['balance'].median()
        ax.axvline(mediana, color='green', linestyle='--', linewidth=2,
                  label=f'Mediana: ${mediana:,.2f}')
        ax.set_xlabel('Saldo', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frecuencia', fontsize=12, fontweight='bold')
        ax.set_title('Distribución de Saldos de Cuentas', fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
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
        ChartGenerator._configure_style()
        df = Analytics.accounts_to_dataframe(accounts)

        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Distribución por Tipo de Cuenta')
            return fig
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        tipo_counts = df['account_type'].value_counts()

        colores = ['#ff9999', '#66b3ff']
        explode = (0.05, 0.05)

        wedges, texts, autotexts = ax1.pie(tipo_counts,
                                           labels=['Cuenta Normal', 'Cuenta de Crédito'],
                                           autopct='%1.1f%%',
                                           startangle=90,
                                           colors=colores,
                                           explode=explode,
                                           shadow=True)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)

        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')

        ax1.set_title('Distribución por Cantidad de Cuentas',
                     fontsize=13, fontweight='bold', pad=20)

        legend_labels = [f'{label}: {count} cuentas'
                        for label, count in zip(['Normal', 'Crédito'], tipo_counts)]
        ax1.legend(legend_labels, loc='upper left', fontsize=10)

        # Sum balances by English 'account_type'
        saldo_por_tipo = df.groupby('account_type')['balance'].sum()

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

        legend_labels2 = [f'{label}: ${saldo:,.2f}'
                         for label, saldo in zip(['Normal', 'Crédito'], saldo_por_tipo)]
        ax2.legend(legend_labels2, loc='upper left', fontsize=10)

        plt.tight_layout()
        return fig

    @staticmethod
    def generate_temporal_trend(accounts: List) -> Figure:
        ChartGenerator._configure_style()
        df = Analytics.accounts_to_dataframe(accounts)

        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Tendencia Temporal de Apertura de Cuentas')
            return fig

        # Work with English 'date' column
        if 'date' not in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos de fechas para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Tendencia Temporal de Apertura de Cuentas')
            return fig

        df_con_fecha = df[df['date'].notna()].copy()

        if df_con_fecha.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay datos de fechas para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Tendencia Temporal de Apertura de Cuentas')
            return fig

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        df_con_fecha = df_con_fecha.sort_values('date')

        df_con_fecha['contador'] = 1
        df_con_fecha['cuentas_acumuladas'] = df_con_fecha['contador'].cumsum()

        # Use English 'account_type'
        df_normal = df_con_fecha[df_con_fecha['account_type'] == 'normal'].copy()
        df_credit = df_con_fecha[df_con_fecha['account_type'] == 'credit'].copy()

        if not df_normal.empty:
            df_normal['acum_tipo'] = df_normal['contador'].cumsum()
            ax1.plot(df_normal['date'], df_normal['acum_tipo'],
                    marker='o', linestyle='-', linewidth=2, markersize=6,
                    label='Cuentas Normales', color='#ff9999')

        if not df_credit.empty:
            df_credit['acum_tipo'] = df_credit['contador'].cumsum()
            ax1.plot(df_credit['date'], df_credit['acum_tipo'],
                    marker='s', linestyle='-', linewidth=2, markersize=6,
                    label='Cuentas de Crédito', color='#66b3ff')

        ax1.plot(df_con_fecha['date'], df_con_fecha['cuentas_acumuladas'],
                marker='D', linestyle='--', linewidth=2, markersize=5,
                label='Total Acumulado', color='green', alpha=0.7)

        ax1.set_xlabel('Fecha', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Número de Cuentas Acumuladas', fontsize=11, fontweight='bold')
        ax1.set_title('Cuentas Acumuladas por Tipo', fontsize=13, fontweight='bold', pad=15)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Gráfica 2: Balance promedio por mes
        df_con_fecha['year_month'] = df_con_fecha['date'].dt.to_period('M')
        balance_por_mes = df_con_fecha.groupby('year_month').agg({
            'balance': ['mean', 'sum', 'count']
        }).reset_index()

        balance_por_mes.columns = ['year_month', 'balance_promedio', 'balance_total', 'cantidad']
        balance_por_mes['year_month_str'] = balance_por_mes['year_month'].astype(str)
        ax2_twin = ax2.twinx()

        x_pos = np.arange(len(balance_por_mes))

        ax2.set_xlabel('Mes', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Balance Promedio ($)', fontsize=11, fontweight='bold', color='blue')
        ax2_twin.set_ylabel('Cantidad de Cuentas', fontsize=11, fontweight='bold', color='red')
        ax2.set_title('Balance Promedio y Cantidad por Mes', fontsize=13, fontweight='bold', pad=15)

        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(balance_por_mes['year_month_str'], rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

        plt.tight_layout()
        return fig

    @staticmethod
    def generate_credit_comparison(accounts: List) -> Figure:
        ChartGenerator._configure_style()
        df = Analytics.accounts_to_dataframe(accounts)

        # Use English 'account_type' to filter credit accounts
        if df.empty or 'account_type' not in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay cuentas de crédito para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Análisis de Cuentas de Crédito')
            return fig

        try:
            df_credito = df[df['account_type'] == 'credit'].copy()
        except Exception:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No hay cuentas de crédito para mostrar',
                   ha='center', va='center', fontsize=14)
            ax.set_title('Análisis de Cuentas de Crédito')
            return fig

        if df_credito.empty:
             fig, ax = plt.subplots(figsize=(10, 6))
             ax.text(0.5, 0.5, 'No hay cuentas de crédito para mostrar',
                    ha='center', va='center', fontsize=14)
             ax.set_title('Análisis de Cuentas de Crédito')
             return fig

        fig, ax = plt.subplots(figsize=(12, 7))

        x_pos = np.arange(len(df_credito))
        width = 0.35

        bars1 = ax.bar(x_pos - width/2, df_credito['balance'], width,
                      label='Balance', color='#66b3ff', alpha=0.8)
        bars2 = ax.bar(x_pos + width/2, df_credito['credit_limit'], width,
                      label='Límite de Crédito', color='#ff9999', alpha=0.8)

        ax.set_xlabel('Cuenta', fontsize=12, fontweight='bold')
        ax.set_ylabel('Monto ($)', fontsize=12, fontweight='bold')
        ax.set_title('Comparación: Balance vs Límite de Crédito',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        # Use 'account_no' for tick labels if present
        if 'account_no' in df_credito.columns:
            ax.set_xticklabels(df_credito['account_no'].astype(str), rotation=45, ha='right')
        else:
            ax.set_xticklabels([str(i) for i in df_credito.index], rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}',
                       ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        return fig

