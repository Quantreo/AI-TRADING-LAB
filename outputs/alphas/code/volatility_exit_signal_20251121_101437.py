from typing import Tuple
import pandas as pd

def volatility_exit_signal(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Volatility Exit Signal alpha using precomputed feature columns from the feature store.

    This function does not recompute features from raw data. It only applies light transforms to the 
    precomputed feature columns.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store containing precomputed feature columns.

    Returns
    -------
    alpha : pd.Series
        Volatility Exit Signal alpha values.
    condition : pd.Series
        Conditioning values based on the benchmark_USD_factor.

    Notes
    -----
    This function uses the following precomputed feature columns:
    - rs_vol_50
    - log_vol_60
    - tail_vol_50
    - oil_vol_50
    - benchmark_USD_factor
    """

    required = {'rs_vol_50', 'log_vol_60', 'tail_vol_50', 'oil_vol_50', 'benchmark_USD_factor'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    def sma(x, n):
        return x.rolling(window=n).mean()

    def rank(x, n):
        return x.rank()

    alpha = -1 * (rank(df['rs_vol_50'], 1) - rank(df['log_vol_60'], 1)) * (sma(df['tail_vol_50'], 20) / sma(df['oil_vol_50'], 20))
    condition = df['benchmark_USD_factor'] > 0

    return alpha, condition