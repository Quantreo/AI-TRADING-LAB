import pandas as pd
import numpy as np

def relative_peaks_proportion(df: pd.DataFrame, window_size: int = 5, high_col: str = 'high', peak_multiplier: float = 1.2) -> pd.Series:
    """
    Calculate proportion of time series exceeding the peak value.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    window_size : int, optional
        Size of the moving average window (default is 5).
    high_col : str, optional
        Name of the column containing high prices (default is 'high').
    peak_multiplier : float, optional
        Multiplier for the peak value (default is 1.2).

    Returns
    -------
    pd.Series
        Proportion of time series exceeding the peak value.
    """
    # Calculate peak values
    peak_values = df[high_col].rolling(window=window_size).max()
    
    # Normalize high prices by peak values
    normalized_high = df[high_col] / peak_values
    
    # Calculate proportion of normalized values exceeding 1
    proportion = (normalized_high > 1).mean()
    
    # Adjust proportion by peak multiplier
    adjusted_proportion = proportion * peak_multiplier
    
    # Apply moving average to filter noise
    result = adjusted_proportion.rolling(window=window_size).mean()
    
    return result