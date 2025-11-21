import pandas as pd
from typing import Tuple

def ema(x: pd.Series, n: int) -> pd.Series:
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def zscore(x: pd.Series, n: int) -> pd.Series:
    """Z-Score"""
    return (x - sma(x, n)) / x.rolling(window=n).std()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Rank"""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

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

    Notes
    -----
    This function requires the input DataFrame to have the following columns: 'rs_vol_60', 'rs_vol_120', 'oil_vol_50'.
    """
    required = {'rs_vol_60', 'rs_vol_120', 'oil_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = zscore(df['rs_vol_60'], zscore_window) + rank(df['rs_vol_120'], rank_window) - sma(df['oil_vol_50'], sma_window)
    condition = df['rs_vol_60'] > sma(df['rs_vol_60'], conditioning_window)
    return alpha, condition