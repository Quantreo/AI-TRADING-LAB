from typing import Tuple
import pandas as pd
import numpy as np

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def zscore(x: pd.Series, n: int) -> pd.Series:
    """Z-score"""
    return (x - sma(x, n)) / x.rolling(window=n).std()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Rank"""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def abs(x: pd.Series) -> pd.Series:
    """Absolute value"""
    return x.abs()

def clip(x: pd.Series, lo: float, hi: float) -> pd.Series:
    """Clip"""
    return x.clip(lo, hi)

def lag(x: pd.Series, n: int) -> pd.Series:
    """Lag"""
    return x.shift(n)

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
    """
    required = {'rs_vol_50', 'log_vol_60', 'tail_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = zscore(df['rs_vol_50'], 50) + rank(df['log_vol_60'], 60) - abs(df['tail_vol_50'])
    condition = df['rs_vol_50'] > sma(df['rs_vol_50'], sma_window)
    return alpha, condition