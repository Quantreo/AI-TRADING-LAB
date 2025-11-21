import pandas as pd
from typing import Tuple

def volatility_exit_signal(df: pd.DataFrame, window_sma: int = 20, eps: float = 1e-12) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Volatility Exit Signal alpha using precomputed feature columns from the feature store.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store containing precomputed feature columns.
    window_sma : int, optional
        Window size for simple moving average (default is 20).
    eps : float, optional
        Epsilon value for division protection (default is 1e-12).

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

    alpha = -1 * (df['rs_vol_50'].rank() - df['log_vol_60'].rank()) * (sma(df['tail_vol_50'], window_sma) / sma(df['oil_vol_50'], window_sma).abs().clip(lower=eps))
    condition = df['benchmark_USD_factor'] > 0

    return alpha, condition