import re
import pandas as pd
from categorization import convert_ai_tuple, categorize_ith_expense, extract_descriptions, read_mappings, user_edit_categorization, categorize_expense_from_descriptions, write_new_category

# Specify the path to your CSV file
transactions_file = './data/Funds.csv'
account_translations_file = './config/accounts.csv'
categorizer_csv = './config/descriptions_categorization.csv'  # Replace with the path to your CSV file
categories_csv = './config/categories.csv'

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
    """
    This is first alteration of transactions dataframe.
    Needed for converting the dataframe to the format, which the code can work with. 
    """
    df = df.rename(columns={'Transaction Date': 'Date'})
    df = df.drop("Cheque Number", axis=1)
    df = replace_account_numbers(account_translations_file, df)
    return df
#}}}

def convert_df_to_MMxl_format(df): # {{{
    """
    This function converts the dataframe to the xlsx format, used in MoneyManager
    """
    df = df.rename(columns={'Account Number': 'Account'}) 
    # Add extra columns
    df["CAD$"] = df["CAD"] 
    df["Income/Expense"] = None
    df["Description"] = None
    df["Amount"] = None
    df["Currency"] = None

    # Remove not needed columns
    df = df.drop("Account Type", axis=1)
    df = df.drop("Description 1", axis=1)
    df = df.drop("Description 2", axis=1)
    df = df.drop("CAD$", axis=1)
    df = df.drop("USD$", axis=1)
    return df
#}}}
    
def sort_ith_expense(df, i): #{{{
    """
    Assigns values to Income/Expense column

    Args:
    df (DataFrame): The DataFrame for which to assign the Income/Expense values.
    i (int): The index of the row for which to assign the Income/Expense values.
    """
    money_difference = df.at[i, "CAD"]
    if money_difference > 0:
        income_expense = "Income"
    else:
        income_expense = "Expense"
    return income_expense
#}}}

df, account_numbers, account_types = df_to_csv_main(transactions_file, account_translations_file)
# Display the DataFrame

print(df)
print(account_numbers)
print(account_types)

print("---Categorization begin---")

# Example usage
mappings_df = read_mappings(categorizer_csv)

categorizator_i = 53
print(df.iloc[categorizator_i])

category, subcategory, note = categorize_ith_expense(df, categorizator_i, mappings_df, categories_csv, categorizer_csv)
print(f"Category: {category}, Subcategory: {subcategory}, Note: {note}")
print("---Categorization end---")



"""
for i in range(0, len(df)):
    Descript1 = df.at[i, 'Description 1']
    if 'Payment' in Descript1:
        print(df.iloc[i])
"""

#for i in range(0, len(df["Account Type"])):
    #print(df["Description 1"][i])
    #print(df["Description 2"][i])

