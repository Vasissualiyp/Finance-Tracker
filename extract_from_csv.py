import pandas as pd

# Specify the path to your CSV file
transactions_file = 'Funds.csv'
account_translations_file = 'accounts.csv'

def df_to_csv_main(transactions_data_file, account_translations_file): #{{{
    df= extract_to_df(transactions_data_file)
    df = alter_transactions_df(account_translations_file, df)
    account_numbers, account_types = extract_account_numbers_and_types(df)
    return df, account_numbers, account_types
#}}}

def replace_account_numbers(translation_file, df): # {{{
    """
    Replaces account numbers in the DataFrame based on a translation file.

    :param translation_file: Path to the CSV file containing account translations.
    :param df: Pandas DataFrame with an 'Account Number' column to be replaced.
    :return: DataFrame with replaced account numbers.
    """
    # Read the translation file into a DataFrame
    translation_df = pd.read_csv(translation_file)

    # Create a dictionary for account number translation
    translation_dict = dict(zip(translation_df['RBCAccount'], translation_df['MoneyManagerAccount']))

    # Replace account numbers in the DataFrame
    df['Account Number'] = df['Account Number'].replace(translation_dict)

    return df
#}}}

def extract_account_numbers_and_types(df): #{{{
    account_numbers = df["Account Number"].unique()
    
    # Initialize an empty list to store account types
    account_types = []
    
    # Iterate over each account number in the account_numbers array
    for account_number in account_numbers:
        # Find the corresponding account type for the current account number
        # Assuming each account number corresponds to one unique account type
        account_type = df[df['Account Number'] == account_number]['Account Type'].iloc[0]
        account_types.append(account_type)
    return account_numbers, account_types
#}}}

def extract_to_df(file_path): #{{{
    # Define the column names
    columns = ["Account Type", "Account Number", "Transaction Date", "Cheque Number", "Description 1", "Description 2", "CAD$", "USD$"]
    
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path, usecols=columns)
    return df
#}}}

def alter_transactions_df(account_translations_file, df): #{{{
    df = df.rename(columns={'Transaction Date': 'Date'})
    df = df.drop("Cheque Number", axis=1)
    df = replace_account_numbers(account_translations_file, df)
    return df
#}}}
    
df, account_numbers, account_types = df_to_csv_main(transactions_file, account_translations_file)
# Display the DataFrame

print(df)
print(account_numbers)
print(account_types)

#for i in range(0, len(df["Account Type"])):
    #print(df["Description 1"][i])
    #print(df["Description 2"][i])

