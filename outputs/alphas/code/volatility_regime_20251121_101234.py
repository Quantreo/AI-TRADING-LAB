import pandas as pd
from typing import Tuple

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def zscore(x: pd.Series, n: int) -> pd.Series:
    """Z-score"""
    return (x - x.rolling(window=n).mean()) / x.rolling(window=n).std()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Rank"""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def volatility_regime(df: pd.DataFrame, sma_window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Regime alpha function.

    This function uses precomputed feature columns from the input DataFrame (feature store) 
    and does not recompute them. It calculates the alpha and conditioning based on the 
    provided formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing precomputed feature columns.
    sma_window : int, optional
        Window for simple moving average, by default 20.

    Returns
    -------
    Tuple[pd.Series, pd.Series]
        Alpha and conditioning Series.
    """
    required = {'rs_vol_50', 'rs_vol_120', 'log_vol_60'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - df.columns)}")

    alpha = zscore(df['rs_vol_50'], 50) * rank(df['log_vol_60'], 60)
    condition = df['rs_vol_50'] > sma(df['rs_vol_120'], sma_window)
    return alpha, condition