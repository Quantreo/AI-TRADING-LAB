import pandas as pd
from typing import Tuple

def calculate_alpha(df: pd.DataFrame, sma_window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate the Volatility Regime Shift Indicator alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store)
    and does not recompute them. It applies the specified formula and conditioning to
    generate the alpha and condition Series.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Simple Moving Average window size (default is 20).

    Returns
    -------
    alpha : pd.Series
        Volatility Regime Shift Indicator alpha Series.
    condition : pd.Series
        Conditioning Series.
    Notes
    -----
    This function assumes that the input DataFrame contains the required columns.
    """
    required = {'rs_vol_50', 'log_vol_60', 'tail_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    def zscore(x: pd.Series, n: int) -> pd.Series:
        """Z-score"""
        return (x - x.rolling(window=n).mean()) / x.rolling(window=n).std()

    def rank(x: pd.Series, n: int) -> pd.Series:
        """Rank"""
        return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

    def abs(x: pd.Series) -> pd.Series:
        """Absolute value"""
        return x.abs()

    alpha = zscore(df['rs_vol_50'], 50) + rank(df['log_vol_60'], 60) - abs(df['tail_vol_50'])
    condition = df['rs_vol_50'] > df['rs_vol_50'].rolling(window=sma_window).mean()
    return alpha, condition