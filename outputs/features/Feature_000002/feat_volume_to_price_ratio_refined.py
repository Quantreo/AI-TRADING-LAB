import pandas as pd
import numpy as np

def volume_to_price_ratio(df: pd.DataFrame, window_size: int = 30, close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Compute the ratio of average traded volume to average price.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    window_size : int, optional
        Size of the rolling window (default is 30).
    close_col : str, optional
        Name of the column containing closing prices (default is 'close').
    volume_col : str, optional
        Name of the column containing traded volumes (default is 'volume').

    Returns
    -------
    pd.Series
        Ratio of average traded volume to average price.
    """
    # Compute average traded volume over the window
    avg_traded_volume = df[volume_col].rolling(window=window_size).mean()
    
    # Compute average price over the window
    avg_price = df[close_col].rolling(window=window_size).mean()
    
    # Compute the ratio of average traded volume to average price
    ratio = avg_traded_volume / avg_price
    
    return ratio