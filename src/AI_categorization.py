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
    response = client.chat.completions.create(model="gpt-4-turbo",  # or the model you are using
    messages=[
        {"role": "user", "content": f"""For the following description of transaction:\n{transaction_description}\n
               Choose the category and subcategory from the following list:\n{categories}\n
               Next, put the vendor. Separate each of these answers by a new line, so your response should be exactly 3 lines - other lengths are unnaceptable.\n
               You also should remove any extra parts from the response based on your judgement (i.e. transaction number).\n
               Example: for the transaction HAPPY BURGER #1234 TORONTO ON, your output should (omitting parts in brackets) 
               look exactly like this:\n
               (Beginning of output)\n
               Food\n
               Lunch\n
               Happy Burger\n
               (End of output)"""}
    ])

    try:
        #generated_content = response['choices'][0]['message']['content'].strip()
        generated_content = response.choices[0].message.content.strip()
    except KeyError as e:
        print(f"KeyError: {e}")
        print("Could not find the required key in the response.")
        return

    print("AI-generated response begin:")
    print(generated_content)
    print("AI-generated response end:")
    return generated_content

if __name__ == "__main__":
    folder = "/home/vasilii/Documents/Tutoring/Olexandr/Fall 2023/"
    generated_file = generate_homework(folder)
    print(f"Generated homework file: {generated_file}")

