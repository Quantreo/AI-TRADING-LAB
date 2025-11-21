from typing import Tuple
import pandas as pd
import numpy as np

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def ema(x: pd.Series, n: int) -> pd.Series:
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def std(x: pd.Series, n: int) -> pd.Series:
    """Standard Deviation"""
    return x.rolling(window=n).std()

def zscore(x: pd.Series, n: int) -> pd.Series:
    """Z-Score"""
    return (x - sma(x, n)) / std(x, n)

def rank(x: pd.Series, n: int) -> pd.Series:
    """Rank"""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def lag(x: pd.Series, n: int) -> pd.Series:
    """Lag"""
    return x.shift(n)

def clip(x: pd.Series, lo: float, hi: float) -> pd.Series:
    """Clip"""
    return x.clip(lo=lo, hi=hi)

def abs(x: pd.Series) -> pd.Series:
    """Absolute"""
    return x.abs()

def volatility_regime_indicator(df: pd.DataFrame, sma_window: int = 20, zscore_window: int = 60, rank_window: int = 120, conditioning_window: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Regime Indicator.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the alpha value based on the given formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window size for Simple Moving Average (default is 20).
    zscore_window : int, optional
        Window size for Z-Score (default is 60).
    rank_window : int, optional
        Window size for Rank (default is 120).
    conditioning_window : int, optional
        Window size for Conditioning (default is 50).

    Returns
    -------
    alpha : pd.Series
        Calculated alpha value.
    condition : pd.Series
        Conditioning value.
    """
    required = {'rs_vol_60', 'rs_vol_120', 'oil_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = zscore(df['rs_vol_60'], zscore_window) + rank(df['rs_vol_120'], rank_window) - sma(df['oil_vol_50'], sma_window)
    condition = df['rs_vol_60'] > sma(df['rs_vol_60'], conditioning_window)
    return alpha, condition