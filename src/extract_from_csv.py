# Author: Vasilii Pustovoit. 01/2024.
import re
import pandas as pd
from categorization import convert_ai_tuple, categorize_ith_expense, extract_descriptions, read_mappings, user_edit_categorization, categorize_expense_from_descriptions, write_new_category
from datetime import datetime

# Specify the path to your CSV files
transactions_file = './data/Funds.csv' # Path for RBC transactions file
account_translations_file = './config/accounts.csv' # Path for the file to convert from RBC account names to MM (MoneyManager)
categorizer_csv = './config/descriptions_categorization.csv'  # Path to conversion of descriptions to categories
categories_csv = './config/categories.csv' # Path to the list of categories
total_xlsx = './data/Money Manager - Excel 2023-01-01 ~ 2023-12-31.xlsx' # Path to excel file with all previous transaction data (MM format)

file_locations = (transactions_file, account_translations_file, categorizer_csv, categories_csv, total_xlsx) 

#-------------------------SOURCE CODE---------------------------------- {{{
# Loading/saving files {{{
def read_excel_to_df(file_path, sheet_name=0): #{{{
    """
    Reads an Excel file into a pandas DataFrame.

    Args:
    file_path (str): The path to the Excel file.
    sheet_name (str or int, optional): The name or index of the sheet to read.
                                       Default is 0, which reads the first sheet.

    Returns:
    pd.DataFrame: DataFrame containing the contents of the specified Excel sheet.

    Raises:
    FileNotFoundError: If the file at the specified path does not exist.
    ValueError: If the specified sheet_name is not found in the Excel file.
    """
    try:
        # Read the Excel file
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"No file found at specified path: {file_path}")
    except ValueError:
        raise ValueError(f"Sheet '{sheet_name}' not found in the Excel file.")
#}}}

def extract_csv_to_df(file_path): #{{{
    # Define the column names
    columns = ["Account Type", "Account Number", "Transaction Date", "Cheque Number", "Description 1", "Description 2", "CAD$", "USD$"]
    
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path, usecols=columns)
    return df
#}}}

def write_df_to_excel(df, file_path, sheet_name='Sheet1'): #{{{
    """
    Writes a DataFrame to an Excel file with a custom sheet name.

    Args:
    df (pd.DataFrame): The DataFrame to be written to the Excel file.
    file_path (str): The path where the Excel file will be saved.
    sheet_name (str): The name of the sheet in the Excel file. Default is 'Sheet1'.
    """
    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
#}}}

def write_df_to_tsv(df, file_path, sep='\t'): #{{{
    """
    Writes a DataFrame to a TSV file.

    Args:
    df (pd.DataFrame): The DataFrame to be written to the TSV file.
    file_path (str): The path where the TSV file will be saved.
    sep (str): The separator to use in the file. Default is tab character.
    """
    # Write the DataFrame to a TSV file
    df.to_csv(file_path, sep=sep, index=False)
#}}}
#}}}

# DataFrame Manipulation: RBC -> MM Conversion {{{
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

def create_extra_column(df): #{{{
    """ 
    We need to create an extra copy of the 'Amount' column in order to make the xlsx readable by MoneyManager
    """
    # Create a new column 'Account' (duplicate) with values from 'Amount'
    df['Account.1'] = df['Amount']
    
    # If you want to place this new column at the end, you can reorder the DataFrame
    columns = df.columns.tolist()
    columns.append(columns.pop(columns.index('Account.1')))
    df = df[columns]
    
    return df
#}}}

def convert_rbc_df_to_MMxlsx(df, mappings_df, categories_csv, categorizer_csv): #{{{
    """
    Converts a DataFrame into the format required by MoneyManager Excel file,
    categorizing each transaction and formatting the DataFrame accordingly.

    Args:
    df (pd.DataFrame): DataFrame containing transaction data.
    mappings_df (pd.DataFrame): DataFrame containing mappings for categorization.
    categories_csv (str): Path to the CSV file containing categories.
    categorizer_csv (str): Path to the CSV file containing categorizer data.

    Returns:
    pd.DataFrame: DataFrame formatted for MoneyManager Excel file.
    """
    #len_df = 1
    len_df = len(df)

    df = add_categorization_columns(df)
    # Categorize every transaction (row) in the array
    for i in range(len_df):
        category, subcategory, note = categorize_ith_expense(df, i, mappings_df, categories_csv, categorizer_csv)
        print(f"Categorized {i} transactions out of {len_df}")
        write_to_df_row(df, i, category, subcategory, note)
    
    df = identify_transferout_transactions(df)

    df = convert_df_to_MMxl_format_preCategory(df)
    print()

    # Last edit to align with the MoneyManager formatting
    df = create_extra_column(df)

    return df
#}}}

def rename_last_column(df, new_name): #{{{
    """
    Renames the last column of a pandas DataFrame.

    Args:
    df (pd.DataFrame): The DataFrame whose last column needs to be renamed.
    new_name (str): The new name for the last column.

    Returns:
    pd.DataFrame: The DataFrame with the last column renamed.
    """
    # Ensure the DataFrame has at least one column
    if len(df.columns) == 0:
        raise ValueError("DataFrame has no columns to rename.")

    # Get a list of the current column names
    column_names = df.columns.tolist()

    # Change the name of the last column
    column_names[-1] = new_name

    # Assign the new list of column names to the DataFrame
    df.columns = column_names

    return df
#}}}
#}}}

def df_to_csv_main(transactions_data_file, account_translations_file): #{{{
    df= extract_csv_to_df(transactions_data_file)
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

def add_categorization_columns(df): # {{{
    df["CAD"] = abs(df["CAD$"])
    df["Income/Expense"] = None
    df["Description"] = ''
    df["Amount"] = None
    df["Currency"] = None
    df["Category"] = None
    df["Subcategory"] = None
    df["Note"] = None
    return df
#}}}

def convert_df_to_MMxl_format_preCategory(df): # {{{
    """
    This function converts the dataframe to the xlsx format, used in MoneyManager.
    The dataframe is not fully ready to be used in the MoneyManager yet - categorization needs to be performed first
    Also, the order is not the same yet.
    """
    df = df.rename(columns={'Account Number': 'Account'}) 
    # Remove not needed columns
    df = df.drop("Account Type", axis=1)
    df = df.drop("Description 1", axis=1)
    df = df.drop("Description 2", axis=1)
    df = df.drop("CAD$", axis=1)
    df = df.drop("USD$", axis=1)

    # Convert the 'Date' column to datetime objects
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    # Convert the datetime objects back to strings in the desired format
    df['Date'] = df['Date'].dt.strftime('%Y/%m/%d')

    # Define the desired column order
    new_column_order = [
        'Date', 'Account', 'Category', 'Subcategory', 'Note',
        'CAD', 'Income/Expense', 'Description', 'Amount', 'Currency'
    ]
    df = df[new_column_order]
    return df
#}}}

def sort_ith_expense(df, i): #{{{
    """
    Assigns values to Income/Expense column

    Args:
    df (DataFrame): The DataFrame for which to assign the Income/Expense values.
    i (int): The index of the row for which to assign the Income/Expense values.
    """
    money_difference = df.at[i, "CAD$"]
    account_name = df.at[i, "Account Number"]
    
    # Convert to numeric type if not already
    money_difference = pd.to_numeric(money_difference, errors='coerce')
    
    # Check if the value is NaN after conversion (indicating a conversion error)
    if pd.isna(money_difference):
        print(f"Conversion error for value {df.at[i, 'CAD']} at index {i}")
        #continue  # Skip this row or handle the error as needed
    
    # Reverse sign for credit card accounts if needed
    #if 'RBC Credit' in account_name or 'Other Credit Condition' in account_name:
    #    money_difference = -money_difference
    
    # Determine if it's income or expense
    income_expense = "Income" if money_difference > 0 else "Expense"

    return income_expense
#}}}

def write_to_df_row(df, i, category, subcategory, note): #{{{
    """
    Updates the DataFrame with new expense information for the specified row index.

    Args:
    df (pd.DataFrame): The DataFrame containing expense data.
    i (int): Index of the row to update.
    category (str): The new category value.
    subcategory (str): The new subcategory value.
    note (str): The new note value.
    """
    # Assuming sort_ith_expense is a function defined elsewhere
    income_expense = sort_ith_expense(df, i)

    df.loc[i, "Category"] = category
    df.loc[i, "Subcategory"] = subcategory
    df.loc[i, "Note"] = note
    df.loc[i, "Income/Expense"] = income_expense
    df.loc[i, "CAD"] = abs(df.loc[i, "CAD"])
    df.loc[i, "Amount"] = df.loc[i, "CAD"]
    df.loc[i, "Currency"] = "CAD"
#}}}

def identify_transferout_transactions(df): #{{{
    """
    Process transactions in the DataFrame to handle special case of matching income and expense transactions.

    Args:
    df (pd.DataFrame): DataFrame containing transaction data with columns 'Date', 'CAD$', 'Income/Expense', 'Account Number', 'Subcategory', 'Note'

    Returns:
    pd.DataFrame: Updated DataFrame after processing.
    """
    # Group the DataFrame by date
    grouped = df.groupby('Date')

    # Find indices of rows to be removed and rows to be updated
    rows_to_remove = []
    rows_to_update = []

    for _, group in grouped:
        # Iterate over each combination of transactions within the group
        for i in group.index:
            for j in group.index:
                if i != j and i not in rows_to_remove and j not in rows_to_remove:
                    #print(f"Checking date {group['Date']},")
                    #print(f"i={i}, j={j}...")
                    # Check if they are a matching pair
                    compare = abs( (group.at[i, 'CAD'] - group.at[j, 'CAD']) / group.at[j, 'CAD'] )
                    if (compare < 0.1 and
                        group.at[i, 'Income/Expense'] != group.at[j, 'Income/Expense']):
                        print("Success!")
                        print(f"Date: {group['Date']}")
                        
                        # Identify income and expense rows
                        income_row = i if group.at[i, 'Income/Expense'] == 'Income' else j
                        expense_row = j if income_row == i else i

                        # Record rows for removal and update
                        rows_to_remove.append(income_row)
                        rows_to_update.append(expense_row)

    # Process updates and removals
    for row in rows_to_update:
        account_number = df.at[rows_to_remove[rows_to_update.index(row)], 'Account Number']
        df.at[row, 'Category'] = account_number
        df.at[row, 'Subcategory'] = ''
        df.at[row, 'Note'] = ''
        df.at[row, 'Income/Expense'] = 'Transfer-Out'

    df = df.drop(rows_to_remove)
    df = df.reset_index(drop=True)

    return df
#}}}

def remove_duplicate_transactions(df): #{{{
    """
    Removes duplicate transactions from a DataFrame based on specific columns.

    Args:
    df (pd.DataFrame): The DataFrame from which to remove duplicate transactions.

    Returns:
    pd.DataFrame: A new DataFrame with duplicate transactions removed.
    """
    # Columns to consider for identifying duplicates
    columns_to_check = ['Date', 'Account', 'CAD', 'Income/Expense', 'Currency', 'Amount']

    # Remove duplicates
    df_without_duplicates = df.drop_duplicates(subset=columns_to_check, keep='first')

    return df_without_duplicates
#}}}

def drop_entries_before_date(df, date_str): #{{{
    """
    Drop all entries in the DataFrame that happened before the given date.

    Args:
    df (pd.DataFrame): DataFrame containing a date column with mixed date formats.
    date_str (str): The cutoff date in 'YYYY-MM-DD' format.

    Returns:
    pd.DataFrame: A DataFrame with entries on or after the given date.
    """
    # Convert date_str to a datetime object
    cutoff_date = datetime.strptime(date_str, '%Y-%m-%d')

    # Standardize the date format in the DataFrame
    def standardize_date(date_str):
        try:
            # Try parsing the full datetime format first
            return datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
        except ValueError:
            # If it fails, it's likely in the shorter date format
            # Set the time to 12:00:00
            return datetime.strptime(date_str + ' 12:00:00', '%Y/%m/%d %H:%M:%S')


    df['Date'] = df['Date'].apply(standardize_date)

    # Filter the DataFrame
    filtered_df = df[df['Date'] >= cutoff_date]

    return filtered_df
#}}}

def main(file_locations): #{{{
    """
    Main function to process transaction files and convert them into the
    format required by MoneyManager Excel file.

    Args:
    file_locations (tuple): A tuple containing paths to the files. The tuple should contain:
                            - Path to the transactions file.
                            - Path to the account translations file.
                            - Path to the CSV file containing categorizer data.
                            - Path to the CSV file containing categories.
                            - Path to the xlsx file containing all previous transactions.
    """
    transactions_file, account_translations_file, categorizer_csv, categories_csv, total_xlsx = file_locations
    output_tsv_path = './data/Funds2.tsv'
    drop_date = '2023-07-01' # A date before all transactions are dropped from the file

    df, account_numbers, account_types = df_to_csv_main(transactions_file, account_translations_file)
    mappings_df = read_mappings(categorizer_csv)

    df = convert_rbc_df_to_MMxlsx(df, mappings_df, categories_csv, categorizer_csv)

    # Obtain dataframe with all data
    df_total = read_excel_to_df(total_xlsx,'Money Manager')
    df_total = rename_last_column(df_total, 'Account.1')

    # Join the new and old transactions dataframes
    df = df.reset_index(drop=True)
    df_total = df_total.reset_index(drop=True)
    df_joined = pd.concat([df, df_total], ignore_index=True)
    df_joined = df_joined.sort_values(by='Date')
    df_joined = drop_entries_before_date(df_joined, drop_date)

    df_joined = rename_last_column(df_joined, 'Account')
    #write_df_to_excel(df_joined, output_tsv_path, sheet_name='Money Manager')
    write_df_to_tsv(df_joined, output_tsv_path)
    print("Export to tsv is complete!")
 
    #print(df_joined.iloc[0])
    
    """
    for i in range(0, len(df)):
        Descript1 = df.at[i, 'Description 1']
        if 'Payment' in Descript1:
            print(df.iloc[i])
    """
#}}}
#-------------------------SOURCE CODE END------------------------------ }}}

main(file_locations)
