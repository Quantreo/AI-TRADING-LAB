import pandas as pd
from typing import Tuple

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def ema(x: pd.Series, n: int) -> pd.Series:
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Ranking"""
    return x.rank()

def compute_alpha(df: pd.DataFrame, ema_window: int = 20, sma_window: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Low-Volatility Trend Persistence alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It applies the specified formula and conditioning to generate the alpha and condition Series.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    ema_window : int, optional
        Window for the exponential moving average (default is 20).
    sma_window : int, optional
        Window for the simple moving average (default is 50).

    Returns
    -------
    alpha : pd.Series
        Computed alpha Series.
    condition : pd.Series
        Computed condition Series.
    """
    required = {'rs_vol_120', 'log_vol_60', 'rs_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = -rank(df['rs_vol_120'], len(df)) * ema(df['log_vol_60'], ema_window)
    condition = df['rs_vol_50'] > sma(df['rs_vol_120'], sma_window)
    return alpha, condition