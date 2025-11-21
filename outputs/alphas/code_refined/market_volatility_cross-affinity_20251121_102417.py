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
    return (x - x.rolling(window=n).mean()) / x.rolling(window=n).std()

def rank(x: pd.Series, n: int) -> pd.Series:
    """Rank"""
    return x.rolling(window=n).apply(lambda x: pd.Series(x).rank().iloc[-1])

def compute_alpha(df: pd.DataFrame, window_ema: int = 20, window_sma: int = 50, eps: float = 1e-12) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the Market Volatility Cross-Affinity alpha.

    This function uses precomputed feature columns from the input DataFrame (feature store) and does not recompute them.
    It applies the specified formula and conditioning to generate the alpha and condition Series.

    Parameters
    ----------
    df : pd.DataFrame
        Feature store containing precomputed feature columns.
    window_ema : int, optional
        Window for the exponential moving average (default is 20).
    window_sma : int, optional
        Window for the simple moving average (default is 50).
    eps : float, optional
        Epsilon value for division protection (default is 1e-12).

    Returns
    -------
    alpha : pd.Series
        The computed alpha Series.
    condition : pd.Series
        The computed condition Series.
    Notes
    -----
    This function requires the 'oil_vol_50', 'gold_vol_50', 'sp500_vol_100', 'bitcoin_vol_100', and 'benchmark_USD_factor' columns in the input DataFrame.
    """
    required = {'oil_vol_50', 'gold_vol_50', 'sp500_vol_100', 'bitcoin_vol_100', 'benchmark_USD_factor'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    z = zscore(df['oil_vol_50'], 50)
    r = rank(df['gold_vol_50'], 50)
    ema_sp500 = ema(df['sp500_vol_100'], window_ema)
    sma_bitcoin = sma(df['bitcoin_vol_100'], window_sma)

    alpha = z * r + ema_sp500 / sma_bitcoin.abs().clip(lower=eps)
    condition = df['benchmark_USD_factor'] > 0

    return alpha, condition