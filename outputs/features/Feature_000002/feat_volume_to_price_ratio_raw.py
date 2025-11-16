import pandas as pd
import numpy as np

def volume_to_price_ratio(df: pd.DataFrame, window_size: int = 30, close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Compute the ratio of average traded volume to average price.

    Parameters
    ----------
    df : pd.DataFrame
    window_size : int, optional
    close_col : str, optional
    volume_col : str, optional

    Returns
    -------
    pd.Series
    """
    # Compute average traded volume over the window
    avg_traded_volume = df[volume_col].rolling(window=window_size).mean()
    
    # Compute average price over the window
    avg_price = df[close_col].rolling(window=window_size).mean()
    
    # Compute the ratio of average traded volume to average price
    ratio = avg_traded_volume / avg_price
    
    return ratio