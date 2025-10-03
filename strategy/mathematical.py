import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

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
    mid_window = config['strategy']['mca']['mid_window']
    long_window = config['strategy']['mca']['long_window']

    # Create a short and a long window MA 
    df['SMA_SHORT'] = df['close'].rolling(window=short_window).mean()
    df['SMA_MID'] = df['close'].rolling(window=mid_window).mean()
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
    Function: Plot price with moving averages and buy/sell signals using Plotly.
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

    # Create the figure
    fig = go.Figure()

    # Price
    fig.add_trace(go.Scatter(
        x=df.index, y=df['close'],
        mode='lines',
        name='Price',
        line=dict(color='black', width=1)
    ))

    # Short SMA
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA_SHORT'],
        mode='lines',
        name=f'SMA {short_window}',
        line=dict(color='blue')
    ))

    # Long SMA
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA_LONG'],
        mode='lines',
        name=f'SMA {long_window}',
        line=dict(color='red')
    ))

    # Buy signals
    fig.add_trace(go.Scatter(
        x=df[df['Position'] == 1].index,
        y=df['SMA_SHORT'][df['Position'] == 1],
        mode='markers',
        name='Buy',
        marker=dict(symbol='triangle-up', size=12, color='green')
    ))

    # Sell signals
    fig.add_trace(go.Scatter(
        x=df[df['Position'] == -1].index,
        y=df['SMA_SHORT'][df['Position'] == -1],
        mode='markers',
        name='Sell',
        marker=dict(symbol='triangle-down', size=12, color='red')
    ))

    # Layout with dual y-axes
    fig.update_layout(
        title=f"{symbol} {timeframe} - Signals",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price / SMAs"),
        yaxis2=dict(
            title=f"SMA {short_window} direction change",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
        template="plotly_white"
    )

    fig.show()
