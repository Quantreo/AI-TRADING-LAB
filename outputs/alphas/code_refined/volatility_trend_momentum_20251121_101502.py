import pandas as pd
from typing import Tuple

def volatility_trend_momentum(df: pd.DataFrame, window_ema: int = 20, window_sma: int = 50, eps: float = 1e-12) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Trend Momentum alpha specification.

    This function uses precomputed feature columns from the input DataFrame (feature store) 
    and does not recompute them. It calculates the alpha and conditioning based on the 
    provided formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store containing precomputed feature columns.
    window_ema : int, optional
        Exponential moving average window (default is 20).
    window_sma : int, optional
        Simple moving average window (default is 50).
    eps : float, optional
        Epsilon value for division protection (default is 1e-12).

    Returns
    -------
    alpha : pd.Series
        Volatility Trend Momentum alpha values.
    condition : pd.Series
        Conditioning values.

    Notes
    -----
    This function does not use the provided window_ema, window_sma, and eps parameters.
    """
    required = {'rs_vol_50', 'rs_vol_120', 'log_vol_60', 'log_vol_50'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = df['rs_vol_50'].rank(method='min', pct=True) * (df['log_vol_60'] - df['log_vol_50'])
    condition = df['rs_vol_50'] > df['rs_vol_120']
    return alpha, condition