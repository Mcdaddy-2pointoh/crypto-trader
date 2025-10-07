import numpy as np
import pandas as pd

def compute_atr(df: pd.DataFrame, config: dict):
    """
    Function: Computes the Average True Range to measure volatility
    Args:
        df: Latest OHLCV data for the past 50 periods
        config: Dictionary with config.yaml values
    """

    period = config['volatility']['atr']['periods']

    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr