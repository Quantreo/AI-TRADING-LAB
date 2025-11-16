import pandas as pd
import numpy as np

def historical_volatility_decay(df: pd.DataFrame, window: int = 20, decay_rate: float = 0.95, close_col: str = 'close') -> pd.Series:
    """
    Compute the decay of historical volatility over time.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    window : int, optional
        Window size (default is 20).
    decay_rate : float, optional
        Decay rate (default is 0.95).
    close_col : str, optional
        Close column name (default is 'close').

    Returns
    -------
    pd.Series
        Ratio of current historical volatility to its value at the beginning of the window.
    """
    # Compute daily returns using close_col
    returns = df[close_col].diff() / df[close_col].shift(1)
    
    # Calculate the cumulative sum of squared returns
    cum_sum_squared_returns = returns ** 2
    
    # Calculate the average of the cumulative sum of squared returns for the last 'window' days
    avg_cum_sum_squared_returns = cum_sum_squared_returns.rolling(window).mean()
    
    # Calculate historical volatility (vol_t) as the square root of the average of the cumulative sum of squared returns
    vol_t = avg_cum_sum_squared_returns ** 0.5
    
    # Repeat steps for the first 'window' days to compute historical volatility at the beginning of the window (vol_0) and one day ago (vol_1)
    vol_0 = (cum_sum_squared_returns.rolling(window).apply(lambda x: x.iloc[0])) ** 0.5
    vol_1 = (cum_sum_squared_returns.rolling(window).apply(lambda x: x.iloc[1])) ** 0.5
    
    # Compute vol_decay_ratio as specified in the mathematical formula
    vol_decay_ratio = (1 - decay_rate) * (vol_t - vol_1) / (vol_0 - vol_1)
    
    return vol_decay_ratio