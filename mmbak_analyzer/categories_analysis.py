
import pandas as pd
from .db_driver import DbDriver

def get_active_categories(db_file):
    """
    Returns a list of active categories from the mmbak file.

    Args:
    db_file (str): Path to the mmbak file.

    Returns:
    DataFrame: Active categories.
    """
    db_driver = DbDriver(db_file)
    query = "SELECT * FROM ZCATEGORY WHERE status=0 AND type=1 AND c_is_del IS NULL"
    categories_df = db_driver.query_to_dataframe(query)
    db_driver.close()
    return categories_df
