import pandas as pd
from typing import Tuple

def compute_alpha(df: pd.DataFrame, sma_window: int = 20, rank_window: int = 50, zscore_window: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Regime-Dependent Volatility Indicator alpha.

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

    Notes
    -----
    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the alpha value based on the provided formula and conditioning.
    """
    required = {'rs_vol_50', 'log_vol_50', 'tail_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    def sma(x: pd.Series, n: int) -> pd.Series:
        """Simple moving average."""
        return x.rolling(window=n).mean()

    def rank(x: pd.Series, n: int) -> pd.Series:
        """Ranking."""
        return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

    def zscore(x: pd.Series, n: int) -> pd.Series:
        """Z-score."""
        mean = x.rolling(window=n).mean()
        std = x.rolling(window=n).std()
        return (x - mean) / std.clip(lower=1e-12)

    alpha = -1 * (rank(df['rs_vol_50'], rank_window) - rank(df['log_vol_50'], rank_window)) * zscore(df['tail_vol_50'], zscore_window)
    condition = df['rs_vol_50'] < sma(df['rs_vol_50'], sma_window)

    return alpha, condition