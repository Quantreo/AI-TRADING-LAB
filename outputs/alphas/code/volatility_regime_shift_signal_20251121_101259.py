import pandas as pd
from typing import Tuple

def sma(x, n):
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def ema(x, n):
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def std(x, n):
    """Standard Deviation"""
    return x.rolling(window=n).std()

def zscore(x, n):
    """Z-Score"""
    return (x - sma(x, n)) / std(x, n)

def rank(x, n):
    """Rank"""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def abs(x):
    """Absolute Value"""
    return x.abs()

def clip(x, lo, hi):
    """Clip"""
    return x.clip(lo, hi)

def lag(x, n):
    """Lag"""
    return x.shift(n)

def volatility_regime_shift_signal(df: pd.DataFrame, sma_window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Regime Shift Signal.

    This function uses precomputed feature columns from the input DataFrame (feature store) 
    and does not recompute them. It calculates the alpha and conditioning signals based on 
    the provided formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window for simple moving average (default is 20).

    Returns
    -------
    alpha : pd.Series
        Alpha signal.
    condition : pd.Series
        Conditioning signal.
    """
    required = {'rs_vol_50', 'log_vol_60', 'tail_vol_50', 'rs_vol_120'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - df.columns)}")

    alpha = zscore(df['rs_vol_50'], 50) * rank(df['log_vol_60'], 60) - abs(df['tail_vol_50'] - df['rs_vol_120'])
    condition = df['rs_vol_50'] > sma(df['rs_vol_50'], sma_window)
    return alpha, condition