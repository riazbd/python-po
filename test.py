import io
import pandas as pd
import json
import pdfplumber


def inner_table(path):

    # Open the PDF file
    with pdfplumber.open(path) as pdf:
        # Initialize a flag to identify the start and end of the desired block
        block_started = False
        block_ended = False

        # Initialize a list to store the extracted block
        desired_block = []

        # Iterate through pages
        for page in pdf.pages:
            # Extract text from the page
            text = page.extract_text()

            # Split the text into lines
            lines = text.split("\n")

            # Iterate through lines
            for line in lines:
                # Check if the line matches the desired header row
                if line.startswith("SKU Code Size Qty Cost (Excl VAT) Cost (Incl VAT) Selling Price"):
                    block_started = True
                    desired_block.append(line)
                elif block_started and not line.startswith("End Use"):
                    # Continue adding lines to the block until "End Use" is encountered
                    desired_block.append(line)
                elif block_started and line.startswith("End Use"):
                    # Stop adding lines when "End Use" is encountered
                    block_ended = True
                    break

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

        size = ' '.join(filter(lambda x: not x.replace(
            '.', '', 1).isdigit(), values[1:]))
        converted_item = {
            "SKU Code": values[0],
            "Size": size,
            "Qty": int(values[-4]),
            "Cost (Excl VAT)": float(values[-3]),
            "Cost (Incl VAT)": float(values[-2]),
            "Selling Price": float(values[-1])
        }

        # Append the converted item to the list
        converted_data.append(converted_item)

    return (converted_data)
