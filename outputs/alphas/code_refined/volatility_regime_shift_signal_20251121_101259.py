import pandas as pd
from typing import Tuple

def ema(x, n):
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def sma(x, n):
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def std(x, n):
    """Standard Deviation"""
    return x.rolling(window=n).std()

def zscore(x, n):
    """Z-Score"""
    return (x - sma(x, n)) / std(x, n)

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

    Notes
    -----
    This function requires the input DataFrame to contain the following columns:
    'rs_vol_50', 'log_vol_60', 'tail_vol_50', 'rs_vol_120'.
    """
    required = {'rs_vol_50', 'log_vol_60', 'tail_vol_50', 'rs_vol_120'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    rs_vol_50 = df['rs_vol_50']
    log_vol_60 = df['log_vol_60']
    tail_vol_50 = df['tail_vol_50']
    rs_vol_120 = df['rs_vol_120']

    alpha = zscore(rs_vol_50, 50) * log_vol_60.rolling(window=60).apply(lambda x: pd.Series(x).rank().iloc[-1]) - (tail_vol_50 - rs_vol_120).abs()
    condition = rs_vol_50 > sma(rs_vol_50, sma_window)
    return alpha, condition