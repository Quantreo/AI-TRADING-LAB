import pandas as pd
from typing import Tuple

def volatility_persistence_signal(df: pd.DataFrame, sma_window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate the Volatility Persistence Signal.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        The window size for the simple moving average (default is 20).

    Returns
    -------
    Tuple[pd.Series, pd.Series]
        A tuple containing the signal and the conditioning filter.

    Notes
    -----
    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the signal as -1 * (rs_vol_120 / rs_vol_60) and applies a conditioning filter based on the simple moving average of rs_vol_60.
    """
    required = {'rs_vol_120', 'rs_vol_60'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    eps = 1e-12
    signal = -1 * (df['rs_vol_120'] / df['rs_vol_60'].abs().clip(lower=eps))
    condition = df['rs_vol_60'] > df['rs_vol_60'].rolling(window=sma_window).mean()
    return signal, condition