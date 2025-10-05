import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from strategy.dip_top import apply_dip_top_strategy

def backtest(df: pd.DataFrame, config: dict):

    # Load the trading configurations from config.yaml
    initial_balance = config['trading']['initial_balance']
    balance = initial_balance
    trade_fraction = config['trading']['trade_fraction']
    position = 0
    equity_curve, trades = [], []

    # Load the trading strategy from config.yaml
    window = config['strategy']['dip_top']['window']

    copy_df = df.copy(deep=True)
    copy_df.reset_index(inplace=True)

    # Iteratively loop through each iteration to validate strategy
    for i, row in copy_df[window:].iterrows():
        price = row['close']
        hist_df = df[i-window : i]
        timestamp = df.index[i]

        signal = apply_dip_top_strategy(df=hist_df, config=config)

        # If signal is buy and there is balance available buy at price
        if signal == 1 and balance > 0:
            amount_to_invest = balance * trade_fraction
            position = amount_to_invest / price
            balance -= amount_to_invest
            trades.append({"timestamp": timestamp, "price": price, "type": "buy"})

        # If signal is sell and there is position available sell at price
        elif signal == -1 and position > 0:
            balance += position * price
            position = 0
            trades.append({"timestamp": timestamp, "price": price, "type": "sell"})

        total_value = balance + position * price
        equity_curve.append({"timestamp": timestamp, "equity": total_value})

    equity_df = pd.DataFrame(equity_curve).set_index("timestamp")
    trades_df = pd.DataFrame(trades)
    final_value = equity_df["equity"].iloc[-1]
    returns = (final_value - initial_balance) / initial_balance * 100

    return equity_df, trades_df, final_value, returns

def plot_backtest(df, trades, equity_df, config: dict):

    symbol = config['trading']['symbol']
    window = config['strategy']['dip_top']['window']
    df[f'MOVING_MEAN_{window}_PERIODS'] = df['close'].rolling(window).mean()
    df[f'MOVING_MIN_{window}_PERIODS'] = df['close'].rolling(window).min()
    df[f'MOVING_MAX_{window}_PERIODS'] = df['close'].rolling(window).max()

    fig = go.Figure()

    # Price line
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines',
                             name='Price', line=dict(color='black')))

    # Short SMA
    fig.add_trace(go.Scatter(x=df.index, y=df[f'MOVING_MEAN_{window}_PERIODS'], mode='lines',
                             name=f'MOVING_MEAN_{window}_PERIODS', line=dict(color='blue')))

    # Long SMA
    fig.add_trace(go.Scatter(x=df.index, y=df[f'MOVING_MIN_{window}_PERIODS'], mode='lines',
                             name=f'MOVING_MIN_{window}_PERIODS', line=dict(color='green')))    
    
    # Long SMA
    fig.add_trace(go.Scatter(x=df.index, y=df[f'MOVING_MAX_{window}_PERIODS'], mode='lines',
                             name=f'MOVING_MAX_{window}_PERIODS', line=dict(color='red')))

    # Buy signals
    buys = trades[trades['type'] == 'buy']
    fig.add_trace(go.Scatter(
        x=buys["timestamp"], y=buys["price"], mode='markers',
        name='Buy', marker=dict(symbol='triangle-up', color='green', size=10)
    ))

    # Sell signals
    sells = trades[trades['type'] == 'sell']
    fig.add_trace(go.Scatter(
        x=sells["timestamp"], y=sells["price"], mode='markers',
        name='Sell', marker=dict(symbol='triangle-down', color='red', size=10)
    ))

    # Update Chart Layout
    fig.update_layout(
        title=f"{symbol} {window} - Signals",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price / Moving Min, Max, Mean "),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
        template="plotly_white"
    )

    fig.show()
