import pandas as pd


def validate_get_price_parameters(crypto_id: str, currency_code: str, N: int)-> tuple: 
    """
    Funtion: Validates the input parameters for all the get_X_price functions
    Args:
        crypto_id (str): The crypto currency to get the live price for
        currency_code (str): The fiat currency to get the price of the crypto asset in
        N (int): The number of days you want the historical data for 
    Returns (tuple) (status, crypto_id, currency_code, N, errors):
        status (bool): status of the arguments, whether they are valid or not
        crypto_id (str): The crypto currency to get the live price for
        currency_code (str): The fiat currency to get the price of the crypto asset in
        N (int): The number of days you want the historical data for 
        errors (None or List): List of errors if any
    """

    # set the status as True
    status = True
    errors = []

    # Validate if the crypto_id is a string
    if not isinstance(crypto_id, str):
        status = False
        errors.append(TypeError(f"The argument `crypto_id` must be of type `str` found type `{type(crypto_id)}`"))

    # Validate the currency_code is a string
    if not isinstance(currency_code, str):
        status = False
        errors.append(TypeError(f"The argument `currency_code` must be of type `str` found type `{type(currency_code)}`"))
    
    # Lower and save the currency_code
    else:
        currency_code = currency_code.lower()

    # Validate the N days is a number 
    if not str(N).isnumeric():
        status = False
        errors.append(TypeError(f"The argument `N` must be of type `int` found type `{type(N)}`"))

    # If N days is not an integer convert it
    else:
        if not isinstance(N, int):
            N = int(N)

        # Check if the N is less than 1 and raise error if so
        if N < 1:
            status = False
            errors.append(ValueError(f"The argument `N` must be greater than 0, got value {N}"))

    # If no errors set it to none
    if len(errors) <= 0:
        errors = None

    return status, crypto_id, currency_code, N, errors
    
def validate_unix_datetime_to_tz_parameters(df:pd.DataFrame, tz:str, timestamp_column: str, time_unit: str="s"):
    """
    Funtion: Validates the input parameters for all the get_X_price functions
    Args:
        df (pd.DataFrame): The dataframe to transform
        tz (str): The timezone to convert the unix timestamp to
        timestamp_column (str): The column name of the unix timestamp
        time_unit (str): The unit of the Unix timestamp, e.g. 's' or 'ms' etc
    Returns (tuple) (status, crypto_id, currency_code, N, errors):
        status (bool): status of the arguments, whether they are valid or not
        df (pd.DataFrame): The dataframe to transform
        tz (str): The timezone to convert the unix timestamp to
        timestamp_column (str): The column name of the unix timestamp
        time_unit (str): The unit of the Unix timestamp, e.g. 's' or 'ms' etc
        errors (None or List): List of errors if any
    """

    status = True
    errors = []

    # Validate if the time_unit is valid argument
    if not isinstance(time_unit, str):
        errors.append(TypeError(f"Argument `time_unit` must be a sting with one of the following values 'D', 'h', 'm', 's', 'ms', 'us' or'ns'; found type {type(time_unit)}"))
        status = False
        return status, None, None, None, None, errors

    if time_unit not in ['D', 'h', 'm', 's', 'ms', 'us', 'ns']:
        errors.append(ValueError(f"Argument `time_unit` must be one of the following values 'D', 'h', 'm', 's', 'ms', 'us' or'ns'; found {time_unit}"))
        status = False
        return status, None, None, None, None, errors
    
    # Validate the time_stamp_column
    if not isinstance(timestamp_column, str):
        errors.append(TypeError(f"Argument `timestamp_column` must be of type `str` found type {timestamp_column}"))
        status = False
        return status, None, None, None, None, errors

    # Validate the df
    if not isinstance(df, pd.DataFrame):
        errors.append(TypeError(f"Argument `df` must be of type `pd.DataFrame` found type {type(df)}"))
        status = False
        return status, None, None, None, None, errors
    
    # Validate if the timestamp_column exists in the df
    if not timestamp_column in df.columns:
        errors.append(ValueError(f"Argument `timestamp_column` must be a column in `df`, could not find {timestamp_column} in the columns {df.columns}"))
        status = False
        return status, None, None, None, None, errors
    
    # Validate the tz 
    if not isinstance(tz, str):
        errors.append(TypeError(f"Argument `tz` must be a sting with one of the following values 'D', 'h', 'm', 's', 'ms', 'us' or'ns'; found type {type(tz)}"))
        status = False
        return status, None, None, None, None, errors

    else:
        errors = None
        return status, df, tz, timestamp_column, time_unit, errors  

