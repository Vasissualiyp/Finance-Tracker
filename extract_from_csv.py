import pandas as pd
from AI_categorization import generate_category
import re

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

# Categorization {{{

def categorize_ith_expense(df, i, mappings_df, categories_csv, categorizer_csv): #{{{
    """
    Categorizes the ith expense in a DataFrame based on descriptions and mappings.

    Args:
    df (DataFrame): The DataFrame containing the expenses.
    i (int): The index of the expense to categorize in the DataFrame.
    mappings_df (DataFrame): The DataFrame containing the mappings for categorization.

    Returns:
    tuple: A tuple containing the category, subcategory, and note for the ith expense.
           Returns ("Index out of range", None, None) if the index is out of bounds.
    """
    if i < 0 or i >= len(df):
        return ("Index out of range", None, None)

    description1, description2 = extract_descriptions(df, i)
    return categorize_expense_from_descriptions(description1, description2, mappings_df, categories_csv, categorizer_csv)
#}}}

def extract_descriptions(df, i):#{{{
    """
    Extracts the descriptions from the ith row of a DataFrame.

    Args:
    df (DataFrame): The DataFrame from which to extract descriptions.
    i (int): The index of the row from which to extract descriptions.

    Returns:
    tuple: A tuple containing the values of 'Description 1' and 'Description 2' from the ith row.
           Returns (None, None) if the index is out of bounds.
    """
    if i < 0 or i >= len(df):
        return (None, None)
    
    description1 = df.at[i, 'Description 1'] if 'Description 1' in df.columns else None
    description2 = df.at[i, 'Description 2'] if 'Description 2' in df.columns else None
    
    return (description1, description2)
#}}}

def read_mappings(csv_file):#{{{
    """
    Reads the mappings from a CSV file and returns a DataFrame.

    Args:
    csv_file (str): The path to the CSV file containing the mappings.

    Returns:
    DataFrame: The DataFrame containing the mappings.
    """
    return pd.read_csv(csv_file)
#}}}

def handle_unknown_categorization(description1, description2, categorizer_csv, categories_csv): #{{{
    """
    Handles 'Unknown' categorizations by prompting the user to select a category, subcategory,
    and add a note. Updates the categorizer CSV file with the new mapping.

    Args:
    description1 (str): The first description of the expense.
    description2 (str): The second description of the expense, can be NaN.
    categorizer_csv (str): Path to the CSV file containing description-category mappings.
    categories_csv (str): Path to the CSV file containing category and subcategory listings.
    """
    # Load categories and subcategories
    categories_df = pd.read_csv(categories_csv)
    categories = categories_df['Category'].unique()
    
    print("Please choose a category:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    category_choice = int(input("Enter the number of your choice: "))
    chosen_category = categories[category_choice - 1]

    subcategories = categories_df[categories_df['Category'] == chosen_category]['Subcategory']
    print("\nPlease choose a subcategory:")
    for i, subcategory in enumerate(subcategories, 1):
        print(f"{i}. {subcategory}")
    subcategory_choice = int(input("Enter the number of your choice: "))
    chosen_subcategory = subcategories.iloc[subcategory_choice - 1]

    note = input("\nEnter a note for this expense: ")

    # Update the categorizer CSV
    new_row = {'Description 1': description1, 'Description 2': description2, 
               'Category': chosen_category, 'Subcategory': chosen_subcategory, 'Note': note}
    categorizer_df = pd.read_csv(categorizer_csv)
    new_row_df = pd.DataFrame([new_row])
    categorizer_df = pd.concat([categorizer_df, new_row_df], ignore_index=True)
    #categorizer_df = categorizer_df.append(new_row, ignore_index=True)
    categorizer_df.to_csv(categorizer_csv, index=False)

    return chosen_category, chosen_subcategory, note
#}}}

def categorize_expense_from_descriptions(description1, description2, mappings_df, categories_csv, categorizer_csv): #{{{
    """
    Categorizes an expense based on given descriptions and mappings. * is considered an 'any' character.

    Args:
    description1 (str): The first description of the expense.
    description2 (str): The second description of the expense, can be NaN.
    mappings_df (DataFrame): The DataFrame containing the mappings.

    Returns:
    tuple: A tuple containing the category, subcategory, and note.
    """
    # Handling NaN values
    description1 = description1 if pd.notna(description1) else ""
    description2 = description2 if pd.notna(description2) else ""

    def regex_from_pattern(pattern):
        """
        Converts a pattern with '*' into a regex pattern.
        '*' is replaced with '.*' to match any character sequence.
        """
        return '^' + re.escape(pattern).replace('\\*', '.*') + '$'

    for _, row in mappings_df.iterrows():
        pattern1 = regex_from_pattern(row['Description 1'])
        pattern2 = regex_from_pattern(row['Description 2']) if pd.notna(row['Description 2']) else None

        if re.match(pattern1, description1) and (pattern2 is None or re.match(pattern2, description2)):
            return (row['Category'], row['Subcategory'], row['Note'])
    # By this point, if the category was not found, create a category

    # Manual entry
    #return handle_unknown_categorization(description1, description2,categorizer_csv, categories_csv)

    # AI entry
    ai_categorization = generate_category(description1, description2, categories_csv)
    return tuple(ai_categorization.split('\n'))
    #return ("Unknown", "Unknown", "No note available")
#}}}
#}}}

def alter_transactions_df(account_translations_file, df): #{{{
    df = df.rename(columns={'Transaction Date': 'Date'})
    df = df.drop("Cheque Number", axis=1)
    df = replace_account_numbers(account_translations_file, df)
    #df = df.rename(columns={'Account Number': 'Account'}) # So far, breaks the code. But crucial for a final xlsx file
    return df
#}}}
    
df, account_numbers, account_types = df_to_csv_main(transactions_file, account_translations_file)
# Display the DataFrame

print(df)
print(account_numbers)
print(account_types)

print("---Categorization begin---")

# Example usage
categorizer_csv = 'descriptions_categorization.csv'  # Replace with the path to your CSV file
categories_csv = 'categories.csv'
mappings_df = read_mappings(categorizer_csv)

categorizator_i = 99
print(df.iloc[categorizator_i])

category, subcategory, note = categorize_ith_expense(df, categorizator_i, mappings_df, categories_csv, categorizer_csv)
print(f"Category: {category}, Subcategory: {subcategory}, Note: {note}")


"""
for i in range(0, len(df)):
    Descript1 = df.at[i, 'Description 1']
    if 'Payment' in Descript1:
        print(df.iloc[i])
"""

#for i in range(0, len(df["Account Type"])):
    #print(df["Description 1"][i])
    #print(df["Description 2"][i])

