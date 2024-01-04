from mmbak_analysis_lib.db_driver import DbDriver
from mmbak_analysis_lib.data_analysis import plot_data
from mmbak_analysis_lib.categories_analysis import get_active_categories
from mmbak_analysis_lib.currencies_analysis import get_currencies
from datetime import datetime, timezone

# Path to your mmbak file
mmbak_file_path = './data/MMAuto[GF231230](2023-12-30-115403).mmbak'

# Initialize the database driver
db_driver = DbDriver(mmbak_file_path)

# Example: Fetch and plot income/outcome data
#query = "SELECT ZDATE, ZMONEY FROM INOUTCOME WHERE IS_DEL = 0;"
income_query =   "SELECT ZDATE, ASSET_NIC, ZMONEY FROM INOUTCOME WHERE DO_TYPE = 0;"
outcome_query =  "SELECT ZDATE, ASSET_NIC, ZMONEY FROM INOUTCOME WHERE DO_TYPE = 1;"
transfer_query = "SELECT ZDATE, ASSET_NIC, WDATE, toAssetUid, ZMONEY FROM INOUTCOME WHERE DO_TYPE = 3;"
income_df = db_driver.query_to_dataframe(income_query)
outcome_df = db_driver.query_to_dataframe(outcome_query)
transfer_df = db_driver.query_to_dataframe(transfer_query)
# Convert each timestamp to a readable date format
income_df['formatted_date']   =   income_df['ZDATE'].apply(lambda x: datetime.fromtimestamp(int(x) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'))
outcome_df['formatted_date']  =  outcome_df['ZDATE'].apply(lambda x: datetime.fromtimestamp(int(x) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'))
transfer_df['formatted_date'] = transfer_df['ZDATE'].apply(lambda x: datetime.fromtimestamp(int(x) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'))

print(income_df)
print(outcome_df)
print(transfer_df)
"""
#plot_data(income_outcome_df, 'Income/Outcome Over Time', 'ZDATE', 'ZMONEY', log_scale=True)

# Fetch active categories
categories_df = get_active_categories(mmbak_file_path)
print("Active Categories:")
print(categories_df)

# Fetch currency information
currencies_df = get_currencies(mmbak_file_path)
print("Currencies:")
print(currencies_df)

# Close the database connection
db_driver.close()
"""


