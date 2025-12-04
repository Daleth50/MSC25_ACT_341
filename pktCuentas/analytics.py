from typing import List, Optional
import pandas as pd
from pktCuentas.credit_account import CreditAccount

class Analytics:

    @staticmethod
    def accounts_to_dataframe(accounts: List) -> pd.DataFrame:
        data = []
        for acc in accounts:
            acc_type = 'credit' if isinstance(acc, CreditAccount) else 'normal'
            credit_limit = acc.get_credit_limit() if acc_type == 'credit' else 0.0
            data.append({
                'account_no': acc.get_account_number(),
                'last_name': acc.get_last_name(),
                'middle_name': acc.get_maternal_last_name(),
                'first_name': acc.get_first_name(),
                'full_name': f"{acc.get_last_name()} {acc.get_maternal_last_name()} {acc.get_first_name()}",
                'balance': acc.get_balance(),
                'date': acc.get_date(),
                'location': acc.get_place() if hasattr(acc, 'get_place') else '',
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
        if df.empty:
            return df
        return df[(df['balance'] >= min_balance) & (df['balance'] <= max_balance)]

    @staticmethod
    def filter_by_account_type(df: pd.DataFrame, acc_type: str) -> pd.DataFrame:
        if df.empty or acc_type == 'all' or acc_type == 'todas':
            return df
        return df[df['account_type'] == acc_type]

    @staticmethod
    def filter_by_location(df: pd.DataFrame, location: Optional[str] = None) -> pd.DataFrame:
        if df.empty or 'location' not in df.columns:
            return df
        if not location:
            return df
        loc = str(location).strip()
        if loc == '' or loc.lower() in ('all', 'todas'):
            return df
        # Match location case-insensitively and trim whitespace
        return df[df['location'].astype(str).str.strip().str.lower() == loc.lower()]

    @staticmethod
    def get_location_options(df: pd.DataFrame) -> List[str]:
        if df is None or df.empty or 'location' not in df.columns:
            return []
        locs = (df['location'].astype(str)
                    .dropna()
                    .map(lambda s: s.strip())
                    .replace('', pd.NA)
                    .dropna()
                    .unique()
                )
        try:
            return sorted([str(x) for x in locs])
        except Exception:
            return [str(x) for x in locs]

    @staticmethod
    def get_statistics(df: pd.DataFrame) -> dict:
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
        if df.empty:
            return pd.DataFrame()
        return df.groupby('account_type').agg(
            count=('account_no', 'count'),
            total_balance=('balance', 'sum')
        ).reset_index()

    @staticmethod
    def group_by_date(df: pd.DataFrame, freq: str = 'M') -> pd.DataFrame:
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
        if df.empty:
            return pd.DataFrame()
        filtered = df[df['account_type'] == 'credit']
        return filtered[['account_no', 'full_name', 'balance', 'credit_limit']]
