import pandas as pd
import matplotlib.pyplot as plt
from strategy.dynamic_stoploss import apply_mca_dynamic_stoploss_strategy
import plotly.graph_objects as go

def backtest(df: pd.DataFrame, config: dict):
    initial_balance = config['trading']['initial_balance']
    balance = initial_balance
    trade_fraction = config['trading']['trade_fraction']
    position = 0
    equity_curve, trades = [], []

    long_window = config['strategy']['mca_dynamic_stoploss']['long_window']
    short_window = config['strategy']['mca_dynamic_stoploss']['short_window']
    max_guard_window = config['strategy']['mca_dynamic_stoploss']['max_guard_window']
    delta = config['strategy']['mca_dynamic_stoploss']['delta']

    copy_df = df.copy(deep=True)
    copy_df.reset_index(inplace=True)

    for i, row in copy_df[long_window:].iterrows():
        price = row['close']

        hist_df = df[i-long_window : i]
        timestamp = hist_df.index[-1]
        hist_df['SMA_SHORT'] = hist_df['close'].rolling(short_window).mean()
        hist_df['SMA_LONG'] = hist_df['close'].rolling(long_window).mean()
        hist_df[f'MAX_{max_guard_window}_SMA_SHORT'] = hist_df['SMA_SHORT'].rolling(max_guard_window).max()

        sma_short = hist_df['SMA_SHORT'].iloc[-1]
        sma_long = hist_df['SMA_LONG'].iloc[-1]
        max_short = hist_df[f'MAX_{max_guard_window}_SMA_SHORT'].iloc[-1]

        # Phase detection
        phase = 1 if sma_short > sma_long else 0

        # BUY phase
        if phase == 1:
            if balance > 0 and sma_short > delta * max_short:
                amount_to_invest = balance * trade_fraction
                position = amount_to_invest / price
                balance -= amount_to_invest
                trades.append({"timestamp": timestamp, "price": price, "type": "buy"})
            elif position > 0 and sma_short < delta * max_short:
                balance += position * price
                position = 0
                trades.append({"timestamp": timestamp, "price": price, "type": "sell"})

        # SELL phase
        elif phase == 0 and position > 0:
            balance += position * price
            position = 0
            trades.append({"timestamp": timestamp, "price": price, "type": "sell"})

        total_value = balance + position * price
        equity_curve.append({"timestamp": timestamp, "equity": total_value, "phase": phase})

    equity_df = pd.DataFrame(equity_curve).set_index("timestamp")
    trades_df = pd.DataFrame(trades)
    final_value = equity_df["equity"].iloc[-1]
    returns = (final_value - initial_balance) / initial_balance * 100

    return equity_df, trades_df, final_value, returns


def plot_backtest(df, trades, equity_df, config: dict):

    long_window = config['strategy']['mca_dynamic_stoploss']['long_window']
    short_window = config['strategy']['mca_dynamic_stoploss']['short_window']

    df['SMA_SHORT'] = df['close'].rolling(short_window).mean()
    df['SMA_LONG'] = df['close'].rolling(long_window).mean()

    fig = go.Figure()

    # Price line
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines',
                             name='Price', line=dict(color='black')))

    # Short SMA
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_SHORT'], mode='lines',
                             name=f"SMA {short_window}", line=dict(color='blue')))

    # Long SMA
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_LONG'], mode='lines',
                             name=f"SMA {long_window}", line=dict(color='red')))

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

    # Phase markers (Buy = 1, Sell = 0) → shown at bottom of chart
    fig.add_trace(go.Scatter(
        x=equity_df.index, y=[min(df['close'])*0.9 if p==1 else min(df['close'])*0.85 for p in equity_df['phase']],
        mode='markers', name="Phase",
        marker=dict(color=['green' if p==1 else 'red' for p in equity_df['phase']], size=6, symbol="circle")
    ))

    fig.update_layout(title="Backtest with Price, SMAs, Trades, and Phase",
                      xaxis_title="Date",
                      yaxis_title="Price")
    fig.show()
