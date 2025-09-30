import ccxt
import yaml
import pandas as pd

def get_exchange(config: dict):
    """
    Function: Connect to exchange using CCXT (public data).
    Args:
        config (dict): The entire config dictionary 
    Return:
        exchange: Binance exchange object
    """

    # Load a binaance exhnge engine
    if config['exchange'] == "binance":
        return ccxt.binance()
    
    # REject other engines
    else:
        raise ValueError(f"Exchange {config['exchange']} not supported")
    
def fetch_data(config: dict, exchange)-> pd.DataFrame:
    """
    Function: Fetch OHLCV data from the exchange.
    Args:
        config_dict (dict): The entire config dictionary 
        exchange: Binance exchange object
    Returns:
        df: OHLCV data in pandas format
    """

    # Load trading_configs
    symbol = str(config['trading']['symbol'])
    timeframe = str(config['trading']['timeframe'])
    limit = int(config['trading']['duration_limit'])

    # Get OHLCV data 
    ohlcv = exchange.fetch_ohlcv(symbol,
                                 timeframe=timeframe,
                                 limit=limit)
    
    # Convert data to df
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

    