import pandas as pd
from typing import Tuple

def trend_following_volatility(df: pd.DataFrame, window_sma: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Trend Following Volatility alpha function.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    window_sma : int, optional
        Window size for the simple moving average (default is 20).

    Returns
    -------
    alpha : pd.Series
        Calculated alpha values.
    condition : pd.Series
        Conditioning filter results.

    Notes
    -----
    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the alpha value based on the linear slope and log volatility, and applies a conditioning filter.
    """
    required = {'linear_slope_100', 'log_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = -1 * (df['linear_slope_100'] * df['log_vol_50'])
    condition = (df['linear_slope_100'] < 0) & (df['log_vol_50'] > df['log_vol_50'].rolling(window=window_sma).mean())

    return alpha, condition