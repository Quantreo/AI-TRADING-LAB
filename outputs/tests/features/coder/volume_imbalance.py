import pandas as pd
import numpy as np

def volume_imbalance_avg(df: pd.DataFrame, window_size: int = 20, close_col: str = 'close', high_col ="high", volume_col: str = 'volume') -> pd.Series:
    """
    Compute average volume imbalance over a fixed window.

    """
    # Compute daily price changes
    price_change = df[close_col].diff()
    
    # Compute daily volume imbalance
    volume_imbalance = df[volume_col] * np.sign(price_change)
    
    # Apply a rolling window to calculate the average volume imbalance
    return volume_imbalance.rolling(window=window_size).mean()