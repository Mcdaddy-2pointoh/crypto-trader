import pandas as pd
import matplotlib.pyplot as plt

def apply_mca_strategy(df: pd.DataFrame, config: dict):
    """
    Function: Produces 'Position' and 'Signal' for Moving Average Crossover strategy on each Row
    Args:
        df: OHLCV data in pandas format
        config (dict): The entire config dictionary 
    Returns:
        df: OHLCV data with a 'Signal' and 'Position' col
    """

    # Load the strategy config
    short_window = config['strategy']['mca']['short_window']
    long_window = config['strategy']['mca']['long_window']

    # Create a short and a long window MA 
    df['SMA_SHORT'] = df['close'].rolling(window=short_window).mean()
    df['SMA_LONG'] = df['close'].rolling(window=long_window).mean()

    # Create a Signal Column to mark signal
    df['Signal'] = 0
    df['Signal'][long_window:] = (df['SMA_SHORT'][long_window:] > df['SMA_LONG'][long_window:]).astype(int)
    df['Position'] = df['Signal'].diff()  
    return df

def plot_signals_mca_strategy(df: pd.DataFrame, config: dict):
    """
    Function: Plot price with moving averages and buy/sell signals.
    Args:
        df: OHLCV data with a 'Signal' and 'Position' col
        config_dict (dict): The entire config dictionary 
    """

    # Load the strategy config
    short_window = config['strategy']['mca']['short_window']
    long_window = config['strategy']['mca']['long_window']

    # Load the timeframe config
    timeframe = str(config['trading']['timeframe'])
    symbol = str(config['trading']['symbol'])

    # Plot the fig
    plt.figure(figsize=(12,6))
    plt.plot(df['close'], label='Price', alpha=0.7)
    plt.plot(df['SMA_SHORT'], label=f'SMA {short_window}')
    plt.plot(df['SMA_LONG'], label=f'SMA {long_window}')
    plt.plot(df[df['Position'] == 1].index, df['SMA_SHORT'][df['Position'] == 1], '^', markersize=10, color='g', label='Buy')
    plt.plot(df[df['Position'] == -1].index, df['SMA_SHORT'][df['Position'] == -1], 'v', markersize=10, color='r', label='Sell')
    plt.title(f'{symbol} {timeframe} - Signals')
    plt.legend()
    plt.show()



