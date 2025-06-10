from pycoingecko import CoinGeckoAPI
import datetime
import pandas as pd
import numpy as np
import math as m
from validators.validate_data_collect import validate_get_price_parameters
from data_transformers.transform_data_collect import transform_unix_datetime_to_tz
import pytz


def get_end_of_day_prices(crypto_id:str = "bitcoin", currency_code: str ="usd", N:int =30, timezone="Asia/Kolkata")->tuple:
    """
    Function: Gets the last daily recorded price of crypto_id for the last N days in the currency you need
    Args: 
        crypto_id (str): The crypto currency to get the live price for
        currency_code (str): The fiat currency to get the price of the crypto asset in
        N (int): The number of days you want the historical data for 
        timezone (str): The timezone of operation according to pytz string
    Returns (tuple) (status, crypto_id, currency_code, N):
        status (bool): status of the operation of function
        df (pd.Dataframe or None): We get a pandas dataframe of price if the function runs without problems. Else, we get an None value
        errors (None or List): List of errors if any
    """
    
    # Validate the function params
    status, crypto_id, currency_code, N, errors = validate_get_price_parameters(crypto_id=crypto_id,
                                                                                currency_code=currency_code,
                                                                                N=N)
    
    # If status is invalid write raise error
    if not status:
        return status, None, errors

    # Else setup the coingecko api object
    else:
        errors = []
        cg = CoinGeckoAPI()
        data = None

        # Get data using params
        try:
            data = cg.get_coin_market_chart_by_id(id=crypto_id, vs_currency=currency_code, days=N)
        
        # Exccept and raise suitable exceptions for failure of code
        except Exception as e:
            if str(e) == str(ValueError({'error': 'invalid vs_currency'})):
                e = ValueError(f"Could not find currency_code `{currency_code}`, please use a fiat currency code such as INR or USD.")

            if str(e) == str(ValueError({'error': 'coin not found'})):
                e = ValueError(f"Could not find crypto_id `{crypto_id}`, please use a crypto currency code such as bitcoin or ethereum.")

            errors.append(e)
            status = False
            return status, data, errors
        
        # Format the data 
        try:    

            # Create a pandas DataFrame 
            data = np.array(data['prices'])
            data = {"timestamps_unix" : data[:, 0], "price": data[:, 1]}
            data = pd.DataFrame(data=data)

            # Get the timestamp according to specified timezone
            status, data, errors = transform_unix_datetime_to_tz(df=data, tz=timezone, time_unit='ms', timestamp_column='timestamps_unix')

        except Exception as e:
            errors.append(e)
            status = False
            data = None
            return status, data, errors

    # if errors are empty return None as errors
    if len(errors) <= 0:
        errors = None

    return status, data, errors