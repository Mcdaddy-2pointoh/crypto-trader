import pandas as pd
import matplotlib.pyplot as plt


def apply_mca_dynamic_stoploss_strategy(df: pd.DataFrame, config: dict):
    """
    Function: Produces 'Position' and 'Signal' for Moving Average Crossover strategy on each Row
    Args:
        df: OHLCV data in pandas format
        config (dict): The entire config dictionary
        past_signal
    Returns:
        df: OHLCV data with a 'Signal' and 'Position' col
    """

    # Load the strategy config
    short_window = config['strategy']['mca_dynamic_stoploss']['short_window']
    long_window = config['strategy']['mca_dynamic_stoploss']['long_window']
    
    # Create a short and a long window MA
    SMA_SHORT = df[-short_window:]['close'].mean()
    SMA_LONG = df[-long_window:]['close'].mean()

    # Create a signal
    signal = int(SMA_SHORT > SMA_LONG)

    return signal