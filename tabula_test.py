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

        if block_ended:
            break

# Use a list comprehension to keep items with the same length as the first item
filtered_data = [desired_block1[0]] + [desired_block1[i]
                                       for i in range(len(desired_block1)) if i % 2 != 0]

print(filtered_data)


def extract_values(data):
    print(data)

    # Split the data string into values using whitespace as the separator
    values = data.split()

    # Initialize a dictionary to store the extracted values
    extracted_values = {}

    # Define a dictionary to map keywords to their corresponding indexes in the split data
    keyword_mapping = {
        'Line': 0,
        'Category': 1,
        'Item': 2,
        'Order Qty': -1
    }

    # Iterate over the keyword_mapping dictionary to extract values
    for keyword, index in keyword_mapping.items():
        if index < len(values):
            extracted_values[keyword] = values[index]
        else:
            extracted_values[keyword] = ""

    description_pattern = rf'(?:{extracted_values["Item"]})(.*?)(?=\s+[A-Z][a-zA-Z]*[a-z])'
    swingTag_pattern = r'(\S+)(?=\s*-\s*[^-]*$)'

    # Extract "Description" using the regular expression pattern and convert it to uppercase
    description_match = re.search(description_pattern, data)
    swingTag_match = re.search(swingTag_pattern, data)

    captured_description = ""
    captured_swingTag = ""
    captured_color = ""

    if description_match:
        captured_description = description_match.group(1)
        print(captured_description)

    if swingTag_match:
        captured_swingTag = swingTag_match.group(1)
        print(captured_swingTag)

    color_pattern = rf'{captured_description} ([^\d]+) {captured_swingTag}'
    color_match = re.search(color_pattern, data)

    if (captured_description != "" and captured_swingTag != ""):

        if color_match:
            captured_color = color_match.group(1)
            print(captured_color)

    extracted_values['Description'] = captured_description
    extracted_values['Swing Tag'] = captured_swingTag
    extracted_values['Colour'] = captured_color

    return extracted_values


# Example data collection
data_collection = filtered_data

# Extract values from the example data collection
values = extract_values(data_collection[1])

# Print the extracted values
print(values)
