import pandas as pd
from typing import Tuple

def volatility_regime_detector(df: pd.DataFrame, sma_window: int = 120, zscore_window: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Compute volatility regime detector alpha.

    This function uses precomputed feature columns from the input DataFrame and does not recompute them.
    It calculates the absolute difference between the z-scores of two volatility features and applies a conditioning filter.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window for simple moving average (default is 120).
    zscore_window : int, optional
        Window for z-score calculation (default is 50).

    Returns
    -------
    alpha : pd.Series
        Volatility regime detector alpha.
    condition : pd.Series
        Conditioning filter.

    Notes
    -----
    This function assumes that the input DataFrame contains the required columns 'rs_vol_50' and 'log_vol_60'.
    """
    required = {'rs_vol_50', 'log_vol_60'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - set(df.columns))}")

    def zscore(x: pd.Series, n: int) -> pd.Series:
        """Compute z-score of a series."""
        return (x - x.rolling(window=n).mean()) / x.rolling(window=n).std().clip(lower=1e-12)

    def sma(x: pd.Series, n: int) -> pd.Series:
        """Compute simple moving average of a series."""
        return x.rolling(window=n).mean()

    alpha = abs(zscore(df['rs_vol_50'], zscore_window) - zscore(df['log_vol_60'], zscore_window))
    condition = df['rs_vol_50'] > sma(df['rs_vol_50'], sma_window)
    return alpha, condition