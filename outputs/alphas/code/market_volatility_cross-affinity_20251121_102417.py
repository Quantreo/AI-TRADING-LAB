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

def compute_alpha(df: pd.DataFrame, ema_window: int = 20, sma_window: int = 50) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Market Volatility Cross-Affinity alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It applies the specified formula and conditioning to generate the alpha and condition Series.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store containing precomputed feature columns.
    ema_window : int, optional
        Window for the exponential moving average (default is 20).
    sma_window : int, optional
        Window for the simple moving average (default is 50).

    Returns
    -------
    alpha : pd.Series
        The computed alpha Series.
    condition : pd.Series
        The computed condition Series.
    """
    required = {'oil_vol_50', 'gold_vol_50', 'sp500_vol_100', 'bitcoin_vol_100', 'benchmark_USD_factor'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    alpha = zscore(df['oil_vol_50'], 50) * rank(df['gold_vol_50'], 50) + ema(df['sp500_vol_100'], ema_window) / sma(df['bitcoin_vol_100'], sma_window)
    condition = df['benchmark_USD_factor'] > 0

    return alpha, condition