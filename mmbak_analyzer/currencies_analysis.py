
import pandas as pd
from .db_driver import DbDriver

def get_currencies(db_file):
    """
    Returns a list of currencies from the mmbak file.

    Args:
    db_file (str): Path to the mmbak file.

    Returns:
    DataFrame: Currencies.
    """
    db_driver = DbDriver(db_file)
    query = "SELECT * FROM CURRENCY"
    currencies_df = db_driver.query_to_dataframe(query)
    db_driver.close()
    return currencies_df
