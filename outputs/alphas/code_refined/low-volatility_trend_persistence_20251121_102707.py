import pandas as pd
from typing import Tuple

def ema(x: pd.Series, n: int) -> pd.Series:
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def compute_alpha(df: pd.DataFrame, window_ema: int = 20, window_sma: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Low-Volatility Trend Persistence alpha.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    window_ema : int, optional
        Window for the exponential moving average (default is 20).
    window_sma : int, optional
        Window for the simple moving average (default is 50).

    Returns
    -------
    alpha : pd.Series
        Computed alpha Series.
    condition : pd.Series
        Computed condition Series.

    Notes
    -----
    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It applies the specified formula and conditioning to generate the alpha and condition Series.
    """
    required = {'rs_vol_120', 'log_vol_60', 'rs_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = -df['rs_vol_120'].rank() * ema(df['log_vol_60'], window_ema)
    condition = df['rs_vol_50'] > df['rs_vol_120'].rolling(window=window_sma).mean()
    return alpha, condition