import pandas as pd
from typing import Tuple

def ema(x: pd.Series, n: int) -> pd.Series:
    """Exponential Moving Average"""
    return x.ewm(span=n, adjust=False).mean()

def sma(x: pd.Series, n: int) -> pd.Series:
    """Simple Moving Average"""
    return x.rolling(window=n).mean()

def zscore(x: pd.Series, n: int) -> pd.Series:
    """Z-score"""
    return (x - sma(x, n)) / x.rolling(window=n).std()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Rank"""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def volatility_regime_transition_signal(df: pd.DataFrame, window_ema: int = 20, window_sma: int = 50, zscore_window: int = 50, rank_window: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Volatility Regime Transition Signal.

    This function uses precomputed feature columns from a feature store (df) and does not recompute them.
    It calculates the alpha and conditioning signals based on the provided formula and conditioning.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store containing precomputed feature columns.
    window_ema : int, optional
        Window for exponential moving average (default is 20).
    window_sma : int, optional
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

    Notes
    -----
    This function assumes that the input DataFrame contains the required columns.
    """
    required = {'rs_vol_50', 'tail_vol_50', 'log_vol_60'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = zscore(df['rs_vol_50'], zscore_window) * rank(df['tail_vol_50'], rank_window) - ema(df['log_vol_60'], window_ema)
    condition = df['rs_vol_50'] > sma(df['rs_vol_50'], window_sma)
    return alpha, condition