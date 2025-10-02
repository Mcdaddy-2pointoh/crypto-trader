import pandas as pd
import matplotlib.pyplot as plt
from strategy.dynamic_stoploss import apply_mca_dynamic_stoploss_strategy

def backtest(df: pd.DataFrame, config: dict):
    """
    Function: To backtest a MA Dynamic Stoploss crossover strategy
    Args:   
        df: OHLCV data with a 'Signal' and 'Position' col
        config (dict): The entire config dictionary 
    Returns:
        equity_df: A DF with the transactional data for each col
        final_value: Final portfolio value
        returns: % returns from the strategy
    """
    
    # Load Config Data
    initial_balance = config['trading']['initial_balance']
    balance = config['trading']['initial_balance']
    total_value = balance
    trade_fraction = config['trading']['trade_fraction']
    position = 0   # number of coins held
    equity_curve = []
    long_window = config['strategy']['mca_dynamic_stoploss']['long_window']
    short_window = config['strategy']['mca_dynamic_stoploss']['short_window']
    past_signal = 0
    
    # Create a Copy of the data frame
    copy_df = df.copy(deep=True)
    copy_df.reset_index(inplace=True)

    for i, row in copy_df[long_window:].iterrows():

        # Get the days price        
        price = row['close']

        # Subset on the past long_window_days
        hist_df = df[i-long_window : i]

        # Generate postion and update past_signal from the 
        position_pred, past_signal = apply_mca_dynamic_stoploss_strategy(df= hist_df, config=config, past_signal=past_signal)

        # If the position is 1 buy the equity
        if position_pred == 1:
            amount_to_invest = balance * trade_fraction
            position = amount_to_invest / price
            balance -= amount_to_invest

        # If the position is > 0 and if the value drops below 80% of max equity or 
        elif ((len(equity_curve) != 0) and (0.8 * total_value == max([x['equity'] for x in equity_curve])) and (position > 0)):




        
        
    del copy_df

    #     # Buy signal
    #     if row['Position'] == 1:
    #         amount_to_invest = balance * trade_fraction
    #         position = amount_to_invest / price
    #         balance -= amount_to_invest

    #     # Sell signal
    #     elif row['Position'] == -1 and position > 0:
    #         balance += position * price
    #         position = 0

    #     # Track total portfolio value
    #     total_value = balance + position * price
    #     equity_curve.append({"timestamp": i, "equity": total_value})

    # equity_df = pd.DataFrame(equity_curve).set_index("timestamp")
    # final_value = equity_df["equity"].iloc[-1]
    # returns = (final_value - initial_balance) / initial_balance * 100

    return None

    # return equity_df, final_value, returns