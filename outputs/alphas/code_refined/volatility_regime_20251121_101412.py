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

    Notes
    -----
    This function requires the following columns in the input DataFrame: 
    rs_vol_50, log_vol_60, tail_vol_50, rs_vol_120, log_vol_50.
    """
    required = {'rs_vol_50', 'log_vol_60', 'tail_vol_50', 'rs_vol_120', 'log_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = zscore(df['rs_vol_50'], 50) * rank(df['log_vol_60'], 60) - (df['tail_vol_50'] - df['rs_vol_120']).abs()
    condition = df['log_vol_50'] > sma(df['log_vol_50'], sma_window)
    return alpha, condition