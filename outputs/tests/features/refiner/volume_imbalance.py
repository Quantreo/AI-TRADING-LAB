import pandas as pd
import numpy as np

def volume_imbalance_avg(df: pd.DataFrame, window_size: int = 20, close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Compute average volume imbalance over a fixed window.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    window_size : int, optional
        Size of the rolling window (default is 20).
    close_col : str, optional
        Name of the column containing closing prices (default is 'close').
    volume_col : str, optional
        Name of the column containing volume data (default is 'volume').

    Returns
    -------
    pd.Series
        Average volume imbalance over the specified window.
    """
    # Compute daily price changes
    price_change = df[close_col].diff()
    
    # Compute daily volume imbalance
    volume_imbalance = df[volume_col] * np.sign(price_change)
    
    # Apply a rolling window to calculate the average volume imbalance
    return volume_imbalance.rolling(window=window_size).mean()