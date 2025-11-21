import pandas as pd
from typing import Tuple

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def ema(x: pd.Series, n: int) -> pd.Series:
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def zscore(x: pd.Series, n: int) -> pd.Series:
    """Z-score"""
    return (x - x.rolling(window=n).mean()) / x.rolling(window=n).std()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Rank"""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def volatility_regime_transition_signal(df: pd.DataFrame, ema_window: int = 20, sma_window: int = 50, zscore_window: int = 50, rank_window: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Regime Transition Signal.

    This function uses precomputed feature columns from a feature store (df) and does not recompute them.
    It calculates the alpha and conditioning signals based on the provided formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store containing precomputed feature columns.
    ema_window : int, optional
        Window for exponential moving average (default is 20).
    sma_window : int, optional
        Window for simple moving average (default is 50).
    zscore_window : int, optional
        Window for z-score calculation (default is 50).
    rank_window : int, optional
        Window for rank calculation (default is 50).

    Returns
    -------
    alpha : pd.Series
        Alpha signal.
    condition : pd.Series
        Conditioning signal.
    """
    required = {'rs_vol_50', 'tail_vol_50', 'log_vol_60'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {sorted(required - set(df.columns))}")

    alpha = zscore(df['rs_vol_50'], zscore_window) * rank(df['tail_vol_50'], rank_window) - ema(df['log_vol_60'], ema_window)
    condition = df['rs_vol_50'] > sma(df['rs_vol_50'], sma_window)
    return alpha, condition