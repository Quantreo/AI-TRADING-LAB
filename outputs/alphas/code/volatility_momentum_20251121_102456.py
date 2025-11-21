import pandas as pd
from typing import Tuple

def rank(x, n=None):
    """Rank series."""
    return x.rank()

def sma(x, n):
    """Simple moving average."""
    return x.rolling(window=n).mean()

def volatility_momentum(df: pd.DataFrame, sma_window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Momentum alpha calculation.

    This function uses precomputed feature columns from the input DataFrame (feature store) 
    and does not recompute them. It calculates the rank of short-term and long-term volatility 
    and then computes their difference. The conditioning is based on the short-term volatility 
    being greater than its simple moving average.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window for simple moving average calculation (default is 20).

    Returns
    -------
    alpha : pd.Series
        Volatility Momentum alpha values.
    condition : pd.Series
        Conditioning values based on short-term volatility.
    """
    required = {'rs_vol_50', 'rs_vol_120', 'rs_vol_60'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - df.columns)}")

    alpha = rank(df['rs_vol_50']) - rank(df['rs_vol_120'])
    condition = df['rs_vol_60'] > sma(df['rs_vol_60'], sma_window)
    return alpha, condition