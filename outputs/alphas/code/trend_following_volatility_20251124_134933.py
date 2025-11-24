import pandas as pd
from typing import Tuple

def sma(x: pd.Series, n: int) -> pd.Series:
    """
    Simple Moving Average.

    Parameters
    ----------
    x : pd.Series
        Input series.
    n : int
        Window size.

    Returns
    -------
    pd.Series
        Simple moving average of the input series.
    """
    return x.rolling(window=n).mean()

def trend_following_volatility(df: pd.DataFrame, sma_window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Trend Following Volatility alpha function.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the alpha value based on the linear slope and log volatility, and applies a conditioning filter.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window size for the simple moving average (default is 20).

    Returns
    -------
    alpha : pd.Series
        Calculated alpha values.
    condition : pd.Series
        Conditioning filter results.
    """
    required = {'linear_slope_100', 'log_vol_50'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - df.columns)}")

    alpha = -1 * (df['linear_slope_100'] * df['log_vol_50'])
    condition = (df['linear_slope_100'] < 0) & (df['log_vol_50'] > sma(df['log_vol_50'], sma_window))

    return alpha, condition