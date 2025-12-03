"""
Analytics Module
Análisis de datos usando Pandas
Implementa tres filtros diferentes para análisis de cuentas
"""

import pandas as pd
from typing import List, Optional
from datetime import datetime


class Analytics:
    """
    Clase para análisis de datos de cuentas bancarias
    Utiliza Pandas para filtrado y análisis
    """

    @staticmethod
    def cuentas_to_dataframe(accounts: List) -> pd.DataFrame:
        """
        Convierte lista de cuentas a DataFrame de Pandas

        Args:
            accounts: Lista de objetos Account

        Returns:
            pd.DataFrame: DataFrame con los datos de las cuentas
        """
        from pktCuentas.credit_account import CreditAccount

        data = []
        for acc in accounts:
            tipo_cuenta = 'credit' if isinstance(acc, CreditAccount) else 'normal'
            limite_credito = acc.get_credit_limit() if isinstance(acc, CreditAccount) else 0.0

            # Parsear fecha
            fecha_obj = None
            if acc.get_fecha():
                try:
                    fecha_obj = pd.to_datetime(acc.get_fecha())
                except:
                    pass

            data.append({
                'no_cuenta': acc.get_no_account(),
                'apellido_paterno': acc.get_apellido_paterno(),
                'apellido_materno': acc.get_apellido_materno(),
                'nombre': acc.get_nombre(),
                'nombre_completo': f"{acc.get_apellido_paterno()} {acc.get_apellido_materno()} {acc.get_nombre()}",
                'balance': float(acc.get_balance()),
                'fecha': fecha_obj,
                'lugar': acc.get_lugar() if acc.get_lugar() else '',
                'tipo_cuenta': tipo_cuenta,
                'limite_credito': float(limite_credito)
            })

        return pd.DataFrame(data)

    @staticmethod
    def filtrar_por_rango_balance(df: pd.DataFrame, balance_min: float,
                                   balance_max: float) -> pd.DataFrame:
        """
        Filtro 1: Filtra cuentas por rango de balance

        Args:
            df: DataFrame con las cuentas
            balance_min: Balance mínimo
            balance_max: Balance máximo

        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        if df.empty:
            return df

        # Filtrar por rango
        df_filtrado = df[(df['balance'] >= balance_min) & (df['balance'] <= balance_max)].copy()

        # Ordenar por balance descendente
        df_filtrado = df_filtrado.sort_values('balance', ascending=False)

        return df_filtrado

    @staticmethod
    def filtrar_por_tipo_cuenta(df: pd.DataFrame, tipo: str) -> pd.DataFrame:
        """
        Filtro 2: Filtra cuentas por tipo (normal o credit)

        Args:
            df: DataFrame con las cuentas
            tipo: 'normal', 'credit', o 'todas'

        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        if df.empty:
            return df

        if tipo == 'todas':
            df_filtrado = df.copy()
        else:
            df_filtrado = df[df['tipo_cuenta'] == tipo].copy()

        # Agregar estadísticas
        if not df_filtrado.empty:
            # Calcular balance promedio por tipo
            df_filtrado['balance_promedio'] = df_filtrado.groupby('tipo_cuenta')['balance'].transform('mean')

            # Ordenar por tipo y balance
            df_filtrado = df_filtrado.sort_values(['tipo_cuenta', 'balance'], ascending=[True, False])

        return df_filtrado

    @staticmethod
    def filtrar_por_fecha_lugar(df: pd.DataFrame, fecha_inicio: Optional[str] = None,
                                fecha_fin: Optional[str] = None,
                                lugar: Optional[str] = None) -> pd.DataFrame:
        """
        Filtro 3: Filtra cuentas por rango de fechas y/o lugar

        Args:
            df: DataFrame con las cuentas
            fecha_inicio: Fecha inicial (formato YYYY-MM-DD)
            fecha_fin: Fecha final (formato YYYY-MM-DD)
            lugar: Lugar a buscar (búsqueda parcial)

        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        if df.empty:
            return df

        df_filtrado = df.copy()

        # Filtrar por fecha
        if fecha_inicio or fecha_fin:
            # Eliminar filas sin fecha
            df_filtrado = df_filtrado[df_filtrado['fecha'].notna()]

            if fecha_inicio:
                try:
                    fecha_inicio_dt = pd.to_datetime(fecha_inicio)
                    df_filtrado = df_filtrado[df_filtrado['fecha'] >= fecha_inicio_dt]
                except:
                    pass

            if fecha_fin:
                try:
                    fecha_fin_dt = pd.to_datetime(fecha_fin)
                    df_filtrado = df_filtrado[df_filtrado['fecha'] <= fecha_fin_dt]
                except:
                    pass

        # Filtrar por lugar (búsqueda case-insensitive)
        if lugar and lugar.strip():
            df_filtrado = df_filtrado[
                df_filtrado['lugar'].str.contains(lugar, case=False, na=False)
            ]

        # Ordenar por fecha descendente
        if 'fecha' in df_filtrado.columns and not df_filtrado.empty:
            df_filtrado = df_filtrado.sort_values('fecha', ascending=False, na_position='last')

        return df_filtrado

    @staticmethod
    def obtener_estadisticas(df: pd.DataFrame) -> dict:
        """
        Calcula estadísticas descriptivas del DataFrame

        Args:
            df: DataFrame con las cuentas

        Returns:
            dict: Diccionario con estadísticas
        """
        if df.empty:
            return {
                'total_cuentas': 0,
                'balance_total': 0.0,
                'balance_promedio': 0.0,
                'balance_min': 0.0,
                'balance_max': 0.0
            }

        stats = {
            'total_cuentas': len(df),
            'balance_total': df['balance'].sum(),
            'balance_promedio': df['balance'].mean(),
            'balance_min': df['balance'].min(),
            'balance_max': df['balance'].max(),
            'balance_mediana': df['balance'].median(),
            'balance_std': df['balance'].std()
        }

        # Estadísticas por tipo de cuenta
        if 'tipo_cuenta' in df.columns:
            stats['cuentas_normales'] = len(df[df['tipo_cuenta'] == 'normal'])
            stats['cuentas_credito'] = len(df[df['tipo_cuenta'] == 'credit'])

        # Estadísticas de crédito
        if 'limite_credito' in df.columns:
            df_credito = df[df['tipo_cuenta'] == 'credit']
            if not df_credito.empty:
                stats['credito_total'] = df_credito['limite_credito'].sum()
                stats['credito_promedio'] = df_credito['limite_credito'].mean()

        return stats

