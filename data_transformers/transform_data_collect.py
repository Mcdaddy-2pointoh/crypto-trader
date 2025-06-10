import pandas as pd
from validators.validate_data_collect import validate_unix_datetime_to_tz_parameters

def transform_unix_datetime_to_tz(df:pd.DataFrame, tz:str, timestamp_column: str, time_unit: str="s"):
    """
    Funtion: Converts a column with unix timmestamp to a timezone
    Args:   
        df (pd.DataFrame): The dataframe to transform
        tz (str): The timezone to convert the unix timestamp to
        timestamp_column (str): The column name of the unix timestamp
        time_unit (str): The unit of the Unix timestamp, e.g. 's' or 'ms' etc
    """

    # Valiate the function arguments
    status, df, tz, timestamp_column, time_unit, errors = validate_unix_datetime_to_tz_parameters(df=df,
                                                                                                  tz=tz,
                                                                                                  timestamp_column=timestamp_column,
                                                                                                  time_unit=time_unit)
    
    # If validation fails return errors
    if not status:
        return status, None, errors
    
    else:
        errors = []
        # Convert the Unix timestamp to a UTC datetime column 
        df[f'timestamp_{tz}'] = pd.to_datetime(df[timestamp_column], unit=time_unit, utc=True).dt.tz_convert(tz)

        return status, df, errors
        


        
        