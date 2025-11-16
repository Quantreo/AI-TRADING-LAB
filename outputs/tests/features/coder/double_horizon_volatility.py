import pandas as pd
import numpy as np

def double_horizon_volatility(df: pd.DataFrame, horizon1: int = 20, horizon2: int = 60, close_col: str = 'close') -> pd.Series:
    """
    Compute double horizon volatility ratio.

    Parameters
    ----------
    df : pd.DataFrame
    horizon1 : int, optional
    horizon2 : int, optional
    close_col : str, optional

    Returns
    -------
    pd.Series
    """
    # Compute returns for shorter horizon
    r1 = df[close_col].pct_change(periods=horizon1)
    # Compute volatility for shorter horizon
    sigma1 = r1.rolling(window=horizon1).std()
    # Compute returns for longer horizon
    r2 = df[close_col].pct_change(periods=horizon2)
    # Compute volatility for longer horizon
    sigma2 = r2.rolling(window=horizon2).std()
    # Compute ratio of volatilities
    return sigma1 / sigma2