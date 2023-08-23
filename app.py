import os
import re
import camelot
import fitz
import pandas as pd
import pdfplumber
import json
from flask import Flask, jsonify, request

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
            'hanger'
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
            "Supplier"
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

        return jsonify({"success": True, "text": text, 'keys': data})
    else:
        return jsonify({"success": False, "error": "Invalid file format. Only PDF files are supported."})


if __name__ == '__main__':
    app.run(debug=True)
