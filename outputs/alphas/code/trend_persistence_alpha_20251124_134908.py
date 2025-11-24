from typing import Tuple
import pandas as pd
import numpy as np

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

def ema(x: pd.Series, n: int) -> pd.Series:
    """
    Exponential Moving Average.

    Parameters
    ----------
    x : pd.Series
        Input series.
    n : int
        Window size.

    Returns
    -------
    pd.Series
        Exponential moving average of the input series.
    """
    return x.ewm(span=n, adjust=False).mean()

def zscore(x: pd.Series, n: int) -> pd.Series:
    """
    Z-score.

    Parameters
    ----------
    x : pd.Series
        Input series.
    n : int
        Window size.

    Returns
    -------
    pd.Series
        Z-score of the input series.
    """
    return (x - x.rolling(window=n).mean()) / x.rolling(window=n).std()

def rank(x: pd.Series, n: int) -> pd.Series:
    """
    Rank.

    Parameters
    ----------
    x : pd.Series
        Input series.
    n : int
        Window size.

    Returns
    -------
    pd.Series
        Rank of the input series.
    """
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def lag(x: pd.Series, n: int) -> pd.Series:
    """
    Lag.

    Parameters
    ----------
    x : pd.Series
        Input series.
    n : int
        Lag size.

    Returns
    -------
    pd.Series
        Lagged input series.
    """
    return x.shift(n)

def abs(x: pd.Series) -> pd.Series:
    """
    Absolute value.

    Parameters
    ----------
    x : pd.Series
        Input series.

    Returns
    -------
    pd.Series
        Absolute value of the input series.
    """
    return x.abs()

def trend_persistence_alpha(df: pd.DataFrame, ema_window: int = 20, sma_window: int = 10, zscore_window: int = 100) -> Tuple[pd.Series, pd.Series]:
    """
    Trend Persistence Alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the trend persistence alpha based on the given formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    ema_window : int, optional
        Window size for the exponential moving average (default is 20).
    sma_window : int, optional
        Window size for the simple moving average (default is 10).
    zscore_window : int, optional
        Window size for the z-score calculation (default is 100).

    Returns
    -------
    Tuple[pd.Series, pd.Series]
        A tuple containing the trend persistence alpha and the conditioning series.
    """
    required = {'returns_100', 'linear_slope_100', 'entropy_returns_100'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = rank(ema(df['returns_100'], ema_window)) * (1 - abs(zscore(df['linear_slope_100'], zscore_window))) + sma(df['entropy_returns_100'], sma_window)
    condition = lag(df['returns_100'], 1) > 0
    if condition.isnull().all():
        condition = pd.Series(True, index=df.index)
    return alpha, condition