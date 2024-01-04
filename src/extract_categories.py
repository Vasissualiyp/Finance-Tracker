import pandas as pd

def generate_category_subcategory_csv(excel_file_path, csv_file_path):
    """
    Generates a CSV file with unique category-subcategory pairs from an Excel file,
    sorted alphabetically by category and then subcategory.

    Args:
    excel_file_path (str): Path to the Excel file containing the transactions.
    csv_file_path (str): Path where the output CSV file will be saved.
    """
    # Read the Excel file
    transactions_df = pd.read_excel(excel_file_path)

    # Check if 'Category' and 'Subcategory' columns exist
    if 'Category' not in transactions_df.columns or 'Subcategory' not in transactions_df.columns:
        raise ValueError("Excel file must contain 'Category' and 'Subcategory' columns.")

    # Extract unique category-subcategory pairs
    unique_pairs_df = transactions_df[['Category', 'Subcategory']].drop_duplicates().dropna()

    # Sort by 'Category' and then by 'Subcategory'
    sorted_unique_pairs_df = unique_pairs_df.sort_values(by=['Category', 'Subcategory'])

    # Save to CSV
    sorted_unique_pairs_df.to_csv(csv_file_path, index=False)

# Example usage
excel_file_path = 'path_to_your_xlsx_MoneyManager_file.xlsx'  # Replace with the path to your Excel file
csv_file_path = '../config/categories.csv'
generate_category_subcategory_csv(excel_file_path, csv_file_path)
