import pandas as pd
from typing import Tuple

def trend_following_opportunity(df: pd.DataFrame, window_ema_1: int = 20, window_ema_2: int = 5) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate the Trend Following Opportunity alpha.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the precomputed feature columns.
    window_ema_1 : int, optional
        The span of the first exponential moving average (default is 20).
    window_ema_2 : int, optional
        The span of the second exponential moving average (default is 5).

    Returns
    -------
    Tuple[pd.Series, pd.Series]
        A tuple containing the alpha series and the conditioning series.

    Notes
    -----
    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the difference between the exponential moving average of returns_100 and returns_10, 
    and returns this value as the alpha, along with a conditioning series based on returns_100.
    """
    required = {'returns_100', 'returns_10'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

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

    alpha = ema(df['returns_100'], window_ema_1) - ema(df['returns_10'], window_ema_2)
    condition = df['returns_100'] > 0

    return alpha, condition