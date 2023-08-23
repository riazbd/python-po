import os
import io
import re
import camelot
import fitz
import pandas as pd
import json
import pdfplumber


# Open the PDF file
with pdfplumber.open("./uploads/PO285746 (1).pdf") as pdf:
    # Initialize a flag to identify the start and end of the desired block
    block_started = False
    block_ended = False

    # Initialize a list to store the extracted block
    desired_block = []
    desired_block1 = []

    # Iterate through pages
    for page in pdf.pages:
        # Extract text from the page
        text = page.extract_text()

        # Split the text into lines
        lines = text.split("\n")

        # Iterate through lines
        for line in lines:
            # Check if the line matches the desired header row
            if line.startswith("Line Category Item Description Colour Style Number Swing Tag Order Qty"):
                block_started = True
                desired_block1.append(line)
            elif block_started and not line.startswith("Order"):
                # Continue adding lines to the block until "End Use" is encountered
                desired_block1.append(line)
            elif block_started and line.startswith("Order"):
                # Stop adding lines when "End Use" is encountered
                block_ended = True
                break

        print(desired_block1)

        if block_ended:
            break


# Combine the lines into a single string
table_text = '\n'.join(desired_block)

# Convert the table text into a Pandas DataFrame
df = pd.read_csv(io.StringIO(table_text), delimiter="\t")

# Print the DataFrame
# print(df)

# Convert the DataFrame to a list of dictionaries
table_data_dict = df.to_dict(orient="records")

# Convert the list of dictionaries to a JSON-formatted string
json_data = json.dumps(table_data_dict, indent=4)

# print(json_data)

data_object = json.loads(json_data)

# print(data_object)


# Initialize an empty list to store the converted data
converted_data = []

# Iterate through the input data
for item in data_object:
    # Get the single value from the dictionary
    value = list(item.values())[0]

    # Split the string by spaces to extract individual values
    values = value.split()

    # Create a dictionary with meaningful keys

    # size = ' '.join(filter(lambda x: not x.replace(
    #     '.', '', 1).isdigit(), values[1:]))
    converted_item = {
        "Line": values[0],
        "Category": values[2],
        "Item": int(values[-4]),
        "Description": float(values[-3]),
        "Colour": float(values[-2]),
        "Style Number": float(values[-1]),
        "Swing Tag": float(values[-2]),
        "Order Quantity": values[-1]
    }

    # Append the converted item to the list
    converted_data.append(converted_item)

    # Print the converted data
    for item in converted_data:
        print(item)
