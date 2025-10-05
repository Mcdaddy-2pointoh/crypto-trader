import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def apply_dip_top_strategy(df: pd.DataFrame, config:dict) -> tuple:
    """
    Function: Apply and generate signals for the dip top strategy
    Args:
        df (pd.DataFrame): A df with OHLCV data from the past window
        config (dict): Connfiguration dictionary
    """

    # Calculate window mean
    df_close_mean = df['close'].mean()
    df_close_min = df['close'].min()
    df_close_max = df['close'].max()

    # Strategy configs
    dip_pct = config['strategy']['dip_top']['dip_pct']
    top_pct = config['strategy']['dip_top']['top_pct']
    strat_type = config['strategy']['dip_top']['strat_type']

    # If the window mean is less than 
    if strat_type == "mean":
        
        # Create a buy signal
        if df_close_mean * (1-(dip_pct)/100) > df['close'][-1]:
            return 1
        
        # Create a sell signal
        elif df_close_mean * (1+(top_pct)/100) < df['close'][-1]:
            return -1
        
        # Create a none signal
        else:
            return 0

    elif strat_type == "min-max":

        # Create a buy signal
        if df_close_min > df['close'][-1]:
            return 1
        
        # Create a sell signal
        elif df_close_max < df['close'][-1]:
            return -1
        
        # Create a none signal
        else:
            return 0
        
    else:
        raise ValueError("Strat Type can either be `mean` or `min-max`")
