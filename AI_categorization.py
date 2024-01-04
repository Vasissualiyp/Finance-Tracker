import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import sys
from datetime import datetime

# Initialize the OpenAI API client (as you did before, not included here)
#openai.api_key = ""
model_engine = "gpt-3.5-turbo"

def generate_category(description1, description2, categories_csv):

    transaction_description=f"{description1}; {description2}"

    # Read the categories
    try:
        with open(categories_csv, 'r') as template_file:
            categories = template_file.read()
    except FileNotFoundError:
        print(f"Categories file {categories} not found.")
        return

    # Generate content for the homework (Assuming you have initialized openai before this)
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # or the model you are using
    messages=[
        {"role": "user", "content": f"""For the following description of transaction:\n{transaction_description}\n
               Choose the category and subcategory from the following list:\n{categories}\n
               Next, put the vendor. Separate each of these answers by a new line.\n
               Example: for the transaction HAPPY BURGER TORONTO ON, your output should (omitting parts in brackets and extra spaces) 
               look exactly like this:\n
               (Beginning of output)\n
               Food (Category)\n
               Lunch (Subcategory)\n
               Happy Burger (Note)\n
               (End of output)"""}
    ])

    try:
        generated_content = response['choices'][0]['message']['content'].strip()
    except KeyError as e:
        print(f"KeyError: {e}")
        print("Could not find the required key in the response.")
        return

    return generated_content

if __name__ == "__main__":
    folder = "/home/vasilii/Documents/Tutoring/Olexandr/Fall 2023/"
    generated_file = generate_homework(folder)
    print(f"Generated homework file: {generated_file}")

