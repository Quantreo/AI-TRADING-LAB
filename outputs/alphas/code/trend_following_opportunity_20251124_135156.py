from typing import Tuple
import pandas as pd

def ema(x: pd.Series, n: int) -> pd.Series:
    """
    Calculate the exponential moving average of a series.

    Parameters
    ----------
    x : pd.Series
        The input series.
    n : int
        The span of the exponential moving average.

    Returns
    -------
    pd.Series
        The exponential moving average of the input series.
    """
    return x.ewm(span=n, adjust=False).mean()

def trend_following_opportunity(df: pd.DataFrame, ema_window_1: int = 20, ema_window_2: int = 5) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate the Trend Following Opportunity alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the difference between the exponential moving average of returns_100 and returns_10, 
    and returns this value as the alpha, along with a conditioning series based on returns_100.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the precomputed feature columns.
    ema_window_1 : int, optional
        The span of the first exponential moving average (default is 20).
    ema_window_2 : int, optional
        The span of the second exponential moving average (default is 5).

    Returns
    -------
    Tuple[pd.Series, pd.Series]
        A tuple containing the alpha series and the conditioning series.
    """
    required = {'returns_100', 'returns_10'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - df.columns)}")

    alpha = ema(df['returns_100'], ema_window_1) - ema(df['returns_10'], ema_window_2)
    condition = df['returns_100'] > 0

    return alpha, condition