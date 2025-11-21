from typing import Tuple
import pandas as pd
import numpy as np

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple moving average."""
    return x.rolling(window=n).mean()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Ranking."""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def zscore(x: pd.Series, n: int) -> pd.Series:
    """Z-score."""
    return (x - x.rolling(window=n).mean()) / x.rolling(window=n).std()

def compute_alpha(df: pd.DataFrame, sma_window: int = 20, rank_window: int = 50, zscore_window: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Regime-Dependent Volatility Indicator alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the alpha value based on the provided formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window size for the simple moving average (default is 20).
    rank_window : int, optional
        Window size for the ranking (default is 50).
    zscore_window : int, optional
        Window size for the z-score calculation (default is 50).

    Returns
    -------
    alpha : pd.Series
        The computed alpha values.
    condition : pd.Series
        The conditioning values.
    """
    required = {'rs_vol_50', 'log_vol_50', 'tail_vol_50'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - set(df.columns))}")

    alpha = -1 * (rank(df['rs_vol_50'], rank_window) - rank(df['log_vol_50'], rank_window)) * zscore(df['tail_vol_50'], zscore_window)
    condition = df['rs_vol_50'] < sma(df['rs_vol_50'], sma_window)

    return alpha, condition