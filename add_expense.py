from datetime import datetime
import json
import os

# Define the path where the data will be saved
data_path = './personal_finance_data.json'

# Predefined lists for accounts and categories with subcategories
accounts_list = ['RBC Credit', 'RBC Chequing Account', 'Cash']
categories_dict = {
    'Food': ['Groceries', 'Eating out'],
    'Household': ['Appliances', 'Chandlery'],
    'Other': []
}

def initialize_data_file():
    """
    Initialize the data file with an empty list if the file doesn't exist.
    """
    if not os.path.exists(data_path):
        with open(data_path, 'w') as f:
            json.dump([], f)

# Modify the function for more optimized manual entry of expenses

def add_expense(date_time, account, category, subcategory, amount, note):
    """
    Manually add an expense entry.
    """
    # Initialize the data file if it doesn't exist
    initialize_data_file()

    # Read the existing data
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Prepare the new expense entry
    new_expense = {
        'Date': date_time,
        'Account': account,
        'Category': category,
        'Subcategory': subcategory,
        'Amount': amount,
        'Note': note
    }

    # Append the new entry to existing data
    data.append(new_expense)

    # Save the updated data back to the file
    with open(data_path, 'w') as f:
        json.dump(data, f)

    print(f"Expense added: {new_expense}")

def manually_add_expense_optimized():
    """
    Optimized interactive function to manually add an expense.
    """
    # Date and Time (current date and time as default)
    date_time_default = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    date_time_input = input(f"Enter Date and Time [{date_time_default}]: ") or date_time_default

    # Check if only date is provided
    try:
        datetime.strptime(date_time_input, '%Y/%m/%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        date_time_input += f" {current_time}"
    except ValueError:
        pass

    date_time = date_time_input

    # Account
    print("Available accounts:")
    for i, acc in enumerate(accounts_list):
        print(f"{i + 1}. {acc}")
    account_index = int(input("Enter the number corresponding to the Account: ")) - 1
    while account_index not in range(len(accounts_list)):
        print("Invalid choice. Please choose from the available accounts.")
        account_index = int(input("Enter the number corresponding to the Account: ")) - 1
    account = accounts_list[account_index]

    # Category and Subcategory
    print("Available categories:")
    for i, cat in enumerate(categories_dict.keys()):
        print(f"{i + 1}. {cat}")
    category_index = int(input("Enter the number corresponding to the Category: ")) - 1
    while category_index not in range(len(categories_dict)):
        print("Invalid choice. Please choose from the available categories.")
        category_index = int(input("Enter the number corresponding to the Category: ")) - 1
    category = list(categories_dict.keys())[category_index]

    print(f"Available subcategories for {category}:")
    for i, subcat in enumerate(categories_dict[category]):
        print(f"{i + 1}. {subcat}")
    subcategory_index = int(input("Enter the number corresponding to the Subcategory: ")) - 1
    while subcategory_index not in range(len(categories_dict[category])):
        print("Invalid choice. Please choose from the available subcategories.")
        subcategory_index = int(input("Enter the number corresponding to the Subcategory: ")) - 1
    subcategory = categories_dict[category][subcategory_index]

    # Amount
    amount = float(input("Enter Amount: "))

    # Note
    note = input("Enter Note/Vendor: ")

    # Add the expense
    add_expense(date_time, account, category, subcategory, amount, note)

# For testing, let's just call the function here, but in practice you would run this function in your own environment
manually_add_expense_optimized()
