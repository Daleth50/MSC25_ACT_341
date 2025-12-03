"""
Analytics Module
Data analysis using Pandas
Implements three different filters for account analysis
"""

from typing import List, Optional
import pandas as pd
from pktCuentas.account import Account
from pktCuentas.credit_account import CreditAccount


class Analytics:
    """
    Provides static methods for data analysis and filtering on accounts using pandas DataFrames.
    """

    @staticmethod
    def accounts_to_dataframe(accounts: List) -> pd.DataFrame:
        """
        Convert a list of Account/CreditAccount objects to a pandas DataFrame.

        Args:
            accounts: List of Account objects

        Returns:
            pd.DataFrame: DataFrame with account data
        """
        data = []
        for acc in accounts:
            acc_type = 'credit' if isinstance(acc, CreditAccount) else 'normal'
            credit_limit = acc.get_credit_limit() if acc_type == 'credit' else 0.0
            data.append({
                'account_no': acc.get_no_account(),
                'last_name': acc.get_apellido_paterno(),
                'middle_name': acc.get_apellido_materno(),
                'first_name': acc.get_nombre(),
                'full_name': f"{acc.get_apellido_paterno()} {acc.get_apellido_materno()} {acc.get_nombre()}",
                'balance': acc.get_balance(),
                'date': acc.get_fecha(),
                'location': acc.get_lugar() if hasattr(acc, 'get_lugar') else '',
                'account_type': acc_type,
                'credit_limit': credit_limit
            })
        df = pd.DataFrame(data)
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df

    @staticmethod
    def filter_by_balance_range(df: pd.DataFrame, min_balance: float,
                                max_balance: float) -> pd.DataFrame:
        """
        Filter accounts by a balance range.

        Args:
            df: DataFrame with accounts
            min_balance: Minimum balance
            max_balance: Maximum balance

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if df.empty:
            return df
        return df[(df['balance'] >= min_balance) & (df['balance'] <= max_balance)]

    @staticmethod
    def filter_by_account_type(df: pd.DataFrame, acc_type: str) -> pd.DataFrame:
        """
        Filter accounts by type: 'normal', 'credit', or 'all'.

        Args:
            df: DataFrame with accounts
            acc_type: 'normal', 'credit', or 'all'

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if df.empty or acc_type == 'all' or acc_type == 'todas':
            return df
        return df[df['account_type'] == acc_type]

    @staticmethod
    def filter_by_date_location(df: pd.DataFrame, date_start: Optional[str] = None,
                                date_end: Optional[str] = None,
                                location: Optional[str] = None) -> pd.DataFrame:
        """
        Filter accounts by date range and/or location.

        Args:
            df: DataFrame with accounts
            date_start: Start date (YYYY-MM-DD format)
            date_end: End date (YYYY-MM-DD format)
            location: Location to search (partial match)

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if df.empty:
            return df
        filtered = df
        if date_start:
            filtered = filtered[filtered['date'] >= pd.to_datetime(date_start)]
        if date_end:
            filtered = filtered[filtered['date'] <= pd.to_datetime(date_end)]
        if location:
            filtered = filtered[filtered['location'].str.contains(location, case=False, na=False)]
        return filtered

    @staticmethod
    def get_statistics(df: pd.DataFrame) -> dict:
        """
        Get statistics from a DataFrame of accounts.

        Args:
            df: DataFrame with accounts

        Returns:
            dict: Dictionary with statistics
        """
        if df.empty:
            return {
                'total_accounts': 0,
                'total_balance': 0.0,
                'average_balance': 0.0,
                'min_balance': 0.0,
                'max_balance': 0.0,
                'normal_accounts': 0,
                'credit_accounts': 0,
                'total_credit': 0.0,
                'average_credit': 0.0
            }
        stats = {
            'total_accounts': len(df),
            'total_balance': df['balance'].sum(),
            'average_balance': df['balance'].mean(),
            'min_balance': df['balance'].min(),
            'max_balance': df['balance'].max(),
        }
        if 'account_type' in df.columns:
            stats['normal_accounts'] = (df['account_type'] == 'normal').sum()
            stats['credit_accounts'] = (df['account_type'] == 'credit').sum()
        if 'credit_limit' in df.columns:
            stats['total_credit'] = df['credit_limit'].sum()
            stats['average_credit'] = df['credit_limit'].mean() if df['credit_limit'].count() > 0 else 0.0
        return stats

    @staticmethod
    def group_by_type(df: pd.DataFrame) -> pd.DataFrame:
        """
        Group accounts by type and return counts and sums.

        Args:
            df: DataFrame with accounts

        Returns:
            pd.DataFrame: Grouped DataFrame
        """
        if df.empty:
            return pd.DataFrame()
        return df.groupby('account_type').agg(
            count=('account_no', 'count'),
            total_balance=('balance', 'sum')
        ).reset_index()

    @staticmethod
    def group_by_date(df: pd.DataFrame, freq: str = 'M') -> pd.DataFrame:
        """
        Group accounts by date (monthly by default).

        Args:
            df: DataFrame with accounts
            freq: Frequency for grouping (e.g., 'M' for month)

        Returns:
            pd.DataFrame: Grouped DataFrame
        """
        if df.empty or 'date' not in df.columns:
            return pd.DataFrame()
        df = df.dropna(subset=['date'])
        if df.empty:
            return pd.DataFrame()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        grouped = df.groupby(pd.Grouper(key='date', freq=freq)).agg(
            count=('account_no', 'count'),
            total_balance=('balance', 'sum')
        ).reset_index()
        return grouped

    @staticmethod
    def compare_balance_credit(df: pd.DataFrame) -> pd.DataFrame:
        """
        Compare balance and credit limit for credit accounts.

        Args:
            df: DataFrame with accounts

        Returns:
            pd.DataFrame: Filtered DataFrame with balance and credit limit
        """
        if df.empty:
            return pd.DataFrame()
        filtered = df[df['account_type'] == 'credit']
        return filtered[['account_no', 'full_name', 'balance', 'credit_limit']]
