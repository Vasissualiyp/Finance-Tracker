import os
from time import sleep
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import sys
from datetime import datetime

# Initialize the OpenAI API client (as you did before, not included here)
#openai.api_key = ""
model_engine = "gpt-4"

def generate_category(description1, description2, categories_csv):

    transaction_description=f"{description1}; {description2}"
    print(f"Using ChatGPT for {transaction_description}...")

    # Read the categories
    try:
        with open(categories_csv, 'r') as template_file:
            categories = template_file.read()
    except FileNotFoundError:
        print(f"Categories file {categories} not found.")
        return

    # Generate content for the homework (Assuming you have initialized openai before this)
    response = client.chat.completions.create(model=model_engine,  # or the model you are using
    #messages = [
    #{"role": "user", "content": f"""
    #For the transaction described below, categorize it by selecting a category and subcategory from the provided list, and identify the vendor or a unique identifier for the transaction.
    #The response should strictly adhere to the following format:

    #1. First line: Category
    #2. Second line: Subcategory (if applicable, otherwise leave this line empty)
    #3. Third line: Vendor or unique identifier

    #Important notes:
    #- Ensure each element (Category, Subcategory, Vendor/Identifier) is on a separate line.
    #- Do not use commas or any other separators besides the newline character.
    #- The response must be exactly three lines. If any of the fields (like Subcategory) do not apply, leave the line empty but still include it.
    #- If the provided information is insufficient for a detailed categorization, categorize as 'Other' with no subcategory.
    #- Exclude any extraneous information from the transaction details (like transaction numbers).

    #Example:
    #Transaction Description: {transaction_description}
    #Categories List: {categories}

    #Your response should look like this (without brackets):
    #(Beginning of output)
    #[Category]
    #[Subcategory]
    #[Vendor/Identifier]
    #(End of output)

    #For instance, for the transaction 'HAPPY BURGER #1234 TORONTO ON', the output should be:
    #(Beginning of output)
    #Food
    #Lunch
    #Happy Burger
    #(End of output)

    #Please follow this format strictly for accurate categorization.
    #"""}
    messages = [
    {"role": "user", "content": f"""
    Please categorize the following transaction:
    Transaction: {transaction_description}
    Categories: {categories}

    Format your response as exactly three lines:
    1. Category
    2. Subcategory (leave blank if not applicable)
    3. Vendor or identifier

    Notes:
    - Use only newline characters to separate lines.
    - If details are insufficient, categorize as 'Other' without a subcategory.
    - Exclude extraneous information (e.g., transaction numbers).

    Example for 'HAPPY BURGER #1234 TORONTO ON':
    Food
    Lunch
    Happy Burger
    """}
    ])


    try:
        #generated_content = response['choices'][0]['message']['content'].strip()
        generated_content = response.choices[0].message.content.strip()
    except KeyError as e:
        print(f"KeyError: {e}")
        print("Could not find the required key in the response.")
        return

    #print("AI-generated response begin:")
    #print(generated_content)
    #print("AI-generated response end:")
    return generated_content

if __name__ == "__main__":
    folder = "/home/vasilii/Documents/Tutoring/Olexandr/Fall 2023/"
    generated_file = generate_homework(folder)
    print(f"Generated homework file: {generated_file}")

