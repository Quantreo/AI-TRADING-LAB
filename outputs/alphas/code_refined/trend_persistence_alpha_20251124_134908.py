import pandas as pd
from typing import Tuple

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

    Notes
    -----
    This function assumes that the input DataFrame contains the required columns.
    """
    required = {'returns_100', 'linear_slope_100', 'entropy_returns_100'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    ema_returns = ema(df['returns_100'], ema_window)
    zscore_slope = zscore(df['linear_slope_100'], zscore_window)
    sma_entropy = sma(df['entropy_returns_100'], sma_window)
    alpha = rank(ema_returns, ema_window) * (1 - abs(zscore_slope)) + sma_entropy
    condition = df['returns_100'].shift(1) > 0
    if condition.isnull().all():
        condition = pd.Series(True, index=df.index)
    return alpha, condition