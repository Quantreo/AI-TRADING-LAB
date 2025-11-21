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

def abs(x: pd.Series) -> pd.Series:
    """Absolute Value"""
    return x.abs()

def clip(x: pd.Series, lo: float, hi: float) -> pd.Series:
    """Clip"""
    return x.clip(lo, hi)

def lag(x: pd.Series, n: int) -> pd.Series:
    """Lag"""
    return x.shift(n)

def volatility_regime(df: pd.DataFrame, sma_window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Regime alpha specification.

    This function uses precomputed feature columns from the input DataFrame (feature store) 
    and does not recompute them. It calculates the alpha and conditioning based on the 
    provided formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window for Simple Moving Average (default is 20).

    Returns
    -------
    alpha : pd.Series
        Calculated alpha values.
    condition : pd.Series
        Calculated conditioning values.
    """
    required = {'rs_vol_50', 'log_vol_60', 'tail_vol_50', 'rs_vol_120', 'log_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = zscore(df['rs_vol_50'], 50) * rank(df['log_vol_60'], 60) - abs(df['tail_vol_50'] - df['rs_vol_120'])
    condition = df['log_vol_50'] > sma(df['log_vol_50'], sma_window)
    return alpha, condition