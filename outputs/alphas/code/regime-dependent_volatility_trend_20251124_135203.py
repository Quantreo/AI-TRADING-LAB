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

def abs(x: pd.Series) -> pd.Series:
    """Absolute Value"""
    return x.abs()

def log_vol(x: pd.Series) -> pd.Series:
    """Logarithm of Volatility"""
    return np.log(x)

def compute_alpha(df: pd.DataFrame, ema_window: int = 20, sma_window: int = 30, std_window: int = 20, threshold: float = 1.5) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Regime-Dependent Volatility Trend alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the alpha as the difference between the exponential moving average of rs_vol_50 and the simple moving average of log_vol_60.
    The conditioning is based on the absolute value of tail_vol_50 being greater than 1.5 times the standard deviation of tail_vol_50.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    ema_window : int, optional
        Window size for the exponential moving average (default is 20).
    sma_window : int, optional
        Window size for the simple moving average (default is 30).
    std_window : int, optional
        Window size for the standard deviation (default is 20).
    threshold : float, optional
        Threshold value for the conditioning (default is 1.5).

    Returns
    -------
    alpha : pd.Series
        The computed alpha values.
    condition : pd.Series
        The conditioning values.
    """
    required = {'rs_vol_50', 'log_vol_60', 'tail_vol_50'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - df.columns)}")

    alpha = ema(df['rs_vol_50'], ema_window) - sma(log_vol(df['log_vol_60']), sma_window)
    condition = abs(df['tail_vol_50']) > threshold * std(df['tail_vol_50'], std_window)
    return alpha, condition