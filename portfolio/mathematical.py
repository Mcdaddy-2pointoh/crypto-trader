import pandas as pd
import matplotlib.pyplot as plt 

def plot_equity(equity_df: pd.DataFrame):
    plt.figure(figsize=(12,4))
    plt.plot(equity_df.index, equity_df['equity'], label='Equity Curve')
    plt.title('Portfolio Value Over Time')
    plt.xlabel('Time')
    plt.ylabel('Equity (USD)')
    plt.legend()
    plt.show()

def backtest(df: pd.DataFrame, config: dict):
    """
    Function: To backtest a MA crossover strategy
    Args:   
        df: OHLCV data with a 'Signal' and 'Position' col
        config (dict): The entire config dictionary 
    Returns:
        equity_df: A DF with the transactional data for each col
        final_value: Final portfolio value
        returns: % returns from the strategy
    """
    
    initial_balance = config['trading']['initial_balance']
    balance = config['trading']['initial_balance']
    trade_fraction = config['trading']['trade_fraction']
    position = 0   # number of coins held
    equity_curve = []

    for i, row in df.iterrows():
        price = row['close']

        # Buy signal
        if row['Position'] == 1:
            amount_to_invest = balance * trade_fraction
            position = amount_to_invest / price
            balance -= amount_to_invest

        # Sell signal
        elif row['Position'] == -1 and position > 0:
            balance += position * price
            position = 0

        # Track total portfolio value
        total_value = balance + position * price
        equity_curve.append({"timestamp": i, "equity": total_value})

    equity_df = pd.DataFrame(equity_curve).set_index("timestamp")
    final_value = equity_df["equity"].iloc[-1]
    returns = (final_value - initial_balance) / initial_balance * 100

    return equity_df, final_value, returns