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

def apply_mca_guarded_strategy(df: pd.DataFrame, config: dict):
    """
    Function: Produces 'Position' and 'Signal' for Moving Average Crossover Guarded with stop loss strategy on each Row
    Args:
        df: OHLCV data in pandas format
        config (dict): The entire config dictionary 
    Returns:
        df: OHLCV data with a 'Signal' and 'Position' col
    """
    df = df.copy(deep=True)

    # Load the strategy config
    short_window = config['strategy']['mca_guarded']['short_window']
    long_window = config['strategy']['mca_guarded']['long_window']
    trend_filter_window = config['strategy']['mca_guarded']['trend_filter_window']
    stop_loss_pct = config['strategy']['mca_guarded']['stop_loss_pct']
    take_profit_pct = config['strategy']['mca_guarded']['take_profit_pct']

    # Create MAs
    df['SMA_Short'] = df['close'].rolling(window=short_window).mean()
    df['SMA_Long'] = df['close'].rolling(window=long_window).mean()
    df['SMA_Trend'] = df['close'].rolling(window=trend_filter_window).mean()

    # Create Signal
    df['Signal'] = 0
    df['Position'] = 0
    buy_price = 0

    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        # Primary crossover signal
        if df['SMA_SHORT'].iloc[i] > df['SMA_LONG'].iloc[i] and df['SMA_SHORT'].iloc[i-1] <= df['SMA_LONG'].iloc[i-1]:
            # Guard: price above long-term trend MA
            if price > df['SMA_Trend'].iloc[i]:
                df['Signal'].iloc[i] = 1
                buy_price = price

        # Sell condition: crossover down OR stop-loss OR take-profit
        elif df['SMA_SHORT'].iloc[i] < df['SMA_LONG'].iloc[i] and df['SMA_SHORT'].iloc[i-1] >= df['SMA_LONG'].iloc[i-1]:
            df['Signal'].iloc[i] = -1
        elif buy_price > 0:
            if price <= buy_price * (1 - stop_loss_pct) or price >= buy_price * (1 + take_profit_pct):
                df['Signal'].iloc[i] = -1

        # Position tracking
        df['Position'].iloc[i] = df['Signal'].iloc[i]

    return df


def plot_signals_mca_strategy(df: pd.DataFrame, config: dict):
    """
    Function: Plot price with moving averages and buy/sell signals.
    Args:
        df: OHLCV data with 'Signal' and 'Position' columns
        config (dict): The entire config dictionary 
    """

    # Load the strategy config
    short_window = config['strategy']['mca']['short_window']
    long_window = config['strategy']['mca']['long_window']

    # Load the timeframe config
    timeframe = str(config['trading']['timeframe'])
    symbol = str(config['trading']['symbol'])

    df['slope_rud'] = df['SMA_SHORT'].diff() 
    df['slope_dir'] = df['SMA_SHORT'].diff() / abs(df['SMA_SHORT'].diff())
    df['slope_dir_change'] = df['slope_dir'].diff()

    # Create figure + primary axis
    fig, ax1 = plt.subplots(figsize=(12,6))

    # Primary axis: price + SMAs + buy/sell signals
    ax1.plot(df.index, df['close'], label='Price', alpha=0.7, color="black")
    ax1.plot(df.index, df['SMA_SHORT'], label=f'SMA {short_window}', color="blue")
    ax1.plot(df.index, df['SMA_LONG'], label=f'SMA {long_window}', color="red")

    # Buy signals
    ax1.plot(df[df['Position'] == 1].index,
             df['SMA_SHORT'][df['Position'] == 1],
             '^', markersize=10, color='g', label='Buy')
    # Sell signals
    ax1.plot(df[df['Position'] == -1].index,
             df['SMA_SHORT'][df['Position'] == -1],
             'v', markersize=10, color='r', label='Sell')

    ax1.set_ylabel("Price / SMAs")
    ax1.legend(loc="upper left")

    # Secondary axis: SMA slope
    ax2 = ax1.twinx()
    ax2.plot(df.index, df['slope_dir_change'],
             label=f"SMA {short_window} direction change", color="green")
    ax2.set_ylabel(f"SMA {short_window} direction change", color="green")
    ax2.legend(loc="upper right")

    # Title
    plt.title(f'{symbol} {timeframe} - Signals')
    plt.show()


