import pandas as pd
from typing import Tuple

def zscore(x, n):
    """Compute z-score of a series."""
    return (x - x.rolling(window=n).mean()) / x.rolling(window=n).std()

def sma(x, n):
    """Compute simple moving average of a series."""
    return x.rolling(window=n).mean()

def volatility_regime_detector(df: pd.DataFrame, sma_window: int = 120) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the volatility regime detector alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store) 
    and does not recompute them. It calculates the absolute difference between the z-scores 
    of two volatility measures and applies a conditioning filter based on the simple moving 
    average of one of the volatility measures.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window size for the simple moving average (default is 120).

    Returns
    -------
    alpha : pd.Series
        The computed alpha values.
    condition : pd.Series
        The conditioning filter values.
    """
    required = {'rs_vol_50', 'log_vol_60'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - df.columns)}")

    alpha = abs(zscore(df['rs_vol_50'], 50) - zscore(df['log_vol_60'], 60))
    condition = df['rs_vol_50'] > sma(df['rs_vol_50'], sma_window)
    return alpha, condition