import os
import re
import camelot
import fitz
import pandas as pd
import pdfplumber
import json
from flask import Flask, jsonify, request
from test import inner_table
from tabula_test import outer_table

app = Flask(__name__)

# Function to convert a Camelot table into a list of dictionaries with keys as headers


def table_to_list_of_dicts(table):
    headers = table.df.iloc[0]  # Assuming the first row contains headers
    data = table.df[1:]  # Assuming the data starts from the second row
    result = []
    for i, row in data.iterrows():
        row_dict = {}
        for j, value in enumerate(row):
            key = headers[j]
            row_dict[key] = value
        result.append(row_dict)
    return result


@app.route('/extract_table', methods=['POST'])
def extract_table():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})

    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.PDF')):
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        # Read the uploaded PDF and extract all text
        pdf_document = fitz.open(file_path)
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()

        # Read the uploaded PDF and extract all tables
        abc = camelot.read_pdf(file_path)

        # Extract values from the first table as a list of dictionaries
        first_table_values = table_to_list_of_dicts(abc[0])

        # close file
        pdf_document.close()

        # Remove the uploaded file after processing
        os.remove(file_path)

        # getting the keys,
        keys = [
            "Supplier No",
            "Department",
            "Currency",
            "Earliest Ship Date",
            "Supplier Name",
            "WW PO No",
            "Terms",
            'Payment Method',
            'Ship Method',
            'hanger',
            'PO Approval Date'
        ]

        data = {}
        for key in keys:
            pattern = r"{}:\s*([^\n]+)".format(key)
            match = re.search(pattern, text)
            if match:
                data[key] = match.group(1)
        # Special handling for "hanger" key
        try:
            hanger_pattern = r"hanger\s*([\d.]+)"
            hanger_match = re.search(hanger_pattern, text)
            data["hanger"] = hanger_match.group(
                1).strip() if hanger_match else "Not Found"
        except AttributeError:
            data["hanger"] = "Not Found"

        return jsonify({"success": True, "data": first_table_values, "text": text, 'keys': data})
    else:
        return jsonify({"success": False, "error": "Invalid file format. Only PDF files are supported."})


@app.route('/extract_mrp', methods=['POST'])
def extract_mrp():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})

    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.PDF')):
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        # Read the uploaded PDF and extract all text
        pdf_document = fitz.open(file_path)
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()

        # getting the keys,
        keys = [
            "Order No",
            "Ship From Date",
            "Currency",
            "Delivery Date",
            "Payment Terms",
            "Delivery Type",
            "Supplier",
            'Originally Approved Date'
        ]

        data = {}
        for key in keys:
            pattern = r"{}:\s*([^\n]+)".format(key)
            match = re.search(pattern, text)
            if match:
                data[key] = match.group(1)

        # Split the text by lines
        lines = text.split('\n')

        # Find the index of the line that contains "Supplier:"
        index_of_supplier = -1
        for i, line in enumerate(lines):
            if "Supplier:" in line:
                index_of_supplier = i
                break

        # Extract the line below "Supplier:"
        if index_of_supplier != -1 and index_of_supplier + 1 < len(lines):
            below_supplier_line = lines[index_of_supplier + 1]
        data["Supplier Name"] = below_supplier_line
        # Special handling for "hanger" key
        # try:
        #     hanger_pattern = r"hanger\s*([\d.]+)"
        #     hanger_match = re.search(hanger_pattern, text)
        #     data["hanger"] = hanger_match.group(
        #         1).strip() if hanger_match else "Not Found"
        # except AttributeError:
        #     data["hanger"] = "Not Found"

        inner_table_data = inner_table(file_path)

        outer_table_data = outer_table(file_path)

        return jsonify({"success": True, "text": text, 'keys': data, "inner_table": inner_table_data, "outer_table": outer_table_data})
    else:
        return jsonify({"success": False, "error": "Invalid file format. Only PDF files are supported."})


@app.route('/extract_ack', methods=['POST'])
def extract_ack():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})

    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.PDF')):
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        # Read the uploaded PDF and extract all text
        pdf_document = fitz.open(file_path)
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()

        # Read the uploaded PDF and extract all tables
        abc1 = camelot.read_pdf(file_path, flavor="stream", pages='1')
        abc = camelot.read_pdf(file_path, flavor="stream", pages='2')

        size_summery = []
        carton_summery = []
        for table in abc:
            table_data = table_to_list_of_dicts(table)
            size_summery.extend(table_data)

        for table in abc1:
            table_data = table_to_list_of_dicts(table)
            carton_summery.extend(table_data)

        all_table_data = {
            "size_summery": size_summery,
            "carton_summery": carton_summery
        }

        filtered_data = {}
        for table_name, table_data in all_table_data.items():
            filtered_table = []
            for item in table_data:
                if len(item) >= 4:
                    filtered_table.append(item)
            if table_name == "carton_summery" and filtered_table:
                # Remove the first item from carton_summery
                filtered_table = filtered_table[2:]

            if table_name == "size_summery" and filtered_table:
                # Remove the last item from size_summery
                filtered_table = filtered_table[:-1]

            if filtered_table:
                filtered_data[table_name] = filtered_table

        # Extract values from the first table as a list of dictionaries
        # first_table_values = table_to_list_of_dicts(abc[0])
        # third_table_values = table_to_list_of_dicts(abc[2])

        # close file
        pdf_document.close()

        # Remove the uploaded file after processing
        os.remove(file_path)

        # getting the keys,
        keys = [
            "Date Ordered",
            "Style Short Desc",
            "Currency",
            "Incoterm",
            "Supplier Name",
            "Supplier No",
            "Confirmation Report for",
            "Port of Load",
            'Handover by',
            'Book by',
        ]

        data = {}
        swap_flag = False  # Flag to indicate if we need to swap values
        prev_value = None  # Store the previous value when swapping
        for key in keys:
            pattern = r"{}:\s*([^\n]+)".format(key)
            match = re.search(pattern, text)
            if match:
                data[key] = match.group(1)

        if 'Book by' in data and 'Handover by' in data:
            data['Book by'], data['Handover by'] = data['Handover by'], data['Book by']
            print(data['Book by'])
            # Get the next word of "Book by" value
        book_by_match = re.search(r"Book by:\s*([^\n]+)\n", text)
        if book_by_match:
            next_line_match = re.search(r"\n(.+)", text[book_by_match.end():])
            if next_line_match:
                next_line_value = next_line_match.group(1)
                data['Handover by'] = next_line_value

        return jsonify({"success": True, "tables": filtered_data, "text": text, 'keys': data})
    else:
        return jsonify({"success": False, "error": "Invalid file format. Only PDF files are supported."})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
