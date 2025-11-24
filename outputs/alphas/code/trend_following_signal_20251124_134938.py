from typing import Tuple
import pandas as pd

def trend_following_signal(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Trend Following Signal alpha using precomputed feature columns.

    This function uses the precomputed feature columns from the input DataFrame
    and does not recompute them. It applies the specified formula and conditioning
    to generate the alpha and condition signals.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing the precomputed feature columns.

    Returns
    -------
    alpha : pd.Series
        The computed alpha signal.
    condition : pd.Series
        The computed conditioning signal.
    """
    required = {'returns_10', 'linear_slope_100', 'abs_returns_10', 'returns_100'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    def rank(x, n=None):
        return x.rank()

    def abs(x):
        return x.abs()

    alpha = rank(df['returns_10']) + rank(df['linear_slope_100']) - rank(abs(df['abs_returns_10']))
    condition = df['returns_100'] > 0
    return alpha, condition