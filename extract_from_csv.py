import pandas as pd

# Specify the path to your CSV file
file_path = 'Funds.csv'

# Define the column names
columns = ["Account Type", "Account Number", "Transaction Date", "Cheque Number", "Description 1", "Description 2", "CAD$", "USD$"]

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv(file_path, usecols=columns)
account_numbers = df["Account Number"].unique()

# Initialize an empty list to store account types
account_types = []

# Iterate over each account number in the account_numbers array
for account_number in account_numbers:
    # Find the corresponding account type for the current account number
    # Assuming each account number corresponds to one unique account type
    account_type = df[df['Account Number'] == account_number]['Account Type'].iloc[0]
    account_types.append(account_type)

# Display the DataFrame
print(account_numbers)
print(account_types)
