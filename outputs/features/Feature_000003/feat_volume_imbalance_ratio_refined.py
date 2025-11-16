import pandas as pd
import numpy as np

def volume_imbalance_ratio(df: pd.DataFrame, volume_col: str = 'volume', low_activity_threshold: float = 0.2) -> pd.Series:
    """
    Compute volume imbalance ratio.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    volume_col : str, optional
        Name of the volume column (default is 'volume').
    low_activity_threshold : float, optional
        Threshold for low activity (default is 0.2).

    Returns
    -------
    pd.Series
        Volume imbalance ratio.
    """
    # Calculate quantiles of the volume column
    high_quantile = df[volume_col].quantile(1 - low_activity_threshold)
    low_quantile = df[volume_col].quantile(low_activity_threshold)

    # Split the volume column into two groups based on the quantiles
    high_volume = df[volume_col][df[volume_col] > high_quantile]
    low_volume = df[volume_col][df[volume_col] < low_quantile]

    # Calculate the average traded volume for each group
    avg_high_volume = high_volume.mean()
    avg_low_volume = low_volume.mean()

    # Compute the ratio of the two averages
    imbalance_ratio = avg_high_volume / avg_low_volume

    return pd.Series([imbalance_ratio] * len(df))