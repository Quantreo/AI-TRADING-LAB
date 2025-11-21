from typing import Tuple
import pandas as pd

def sma(x: pd.Series, n: int) -> pd.Series:
    """
    Calculate the simple moving average of a series.

    Parameters
    ----------
    x : pd.Series
        The input series.
    n : int
        The window size.

    Returns
    -------
    pd.Series
        The simple moving average of the input series.
    """
    return x.rolling(window=n).mean()

def volatility_persistence_signal(df: pd.DataFrame, sma_window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate the Volatility Persistence Signal.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It calculates the signal as -1 * (rs_vol_120 / rs_vol_60) and applies a conditioning filter based on the simple moving average of rs_vol_60.

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
    """
    required = {'rs_vol_120', 'rs_vol_60'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - df.columns)}")

    signal = -1 * (df['rs_vol_120'] / df['rs_vol_60'])
    condition = df['rs_vol_60'] > sma(df['rs_vol_60'], sma_window)
    return signal, condition