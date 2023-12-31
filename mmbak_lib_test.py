from mmbak_analysis_lib.db_driver import DbDriver
from mmbak_analysis_lib.data_analysis import plot_data
from mmbak_analysis_lib.categories_analysis import get_active_categories
from mmbak_analysis_lib.currencies_analysis import get_currencies

# Path to your mmbak file
mmbak_file_path = 'MMAuto[GF231230](2023-12-30-115403).mmbak'

# Initialize the database driver
db_driver = DbDriver(mmbak_file_path)

# Example: Fetch and plot income/outcome data
query = "SELECT ZDATE, ZMONEY FROM INOUTCOME WHERE IS_DEL = 0;"
income_outcome_df = db_driver.query_to_dataframe(query)
plot_data(income_outcome_df, 'Income/Outcome Over Time', 'ZDATE', 'ZMONEY', log_scale=True)

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



