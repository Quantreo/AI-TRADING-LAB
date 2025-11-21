from typing import Tuple
import pandas as pd
import numpy as np

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def ema(x: pd.Series, n: int) -> pd.Series:
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Ranking"""
    return x.rank(method='min', pct=True)

def log_vol(x: pd.Series) -> pd.Series:
    """Log of Volatility"""
    return np.log(x)

def volatility_trend_momentum(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Trend Momentum alpha specification.

    This function uses precomputed feature columns from the input DataFrame (feature store) 
    and does not recompute them. It calculates the alpha and conditioning based on the 
    provided formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store containing precomputed feature columns.

    Returns
    -------
    alpha : pd.Series
        Volatility Trend Momentum alpha values.
    condition : pd.Series
        Conditioning values.
    """
    required = {'rs_vol_50', 'rs_vol_120', 'log_vol_60', 'log_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = rank(df['rs_vol_50'], len(df)) * (df['log_vol_60'] - df['log_vol_50'])
    condition = df['rs_vol_50'] > df['rs_vol_120']
    return alpha, condition