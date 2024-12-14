import csv
import json
import os
from collections import OrderedDict

def process_audit_logs(input_file, output_file, json_column_index=5):
    """
    Processes a CSV file containing JSON data in a specified column and converts it to a flattened CSV.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
        json_column_index (int): The zero-based index of the column containing JSON data.
    """
    # List to hold flattened data
    flattened_data = []

    # Open the input CSV file for reading
    with open(input_file, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)
        headers = next(reader)  # Skip the header row

        for row_number, row in enumerate(reader, start=2):
            try:
                json_data = json.loads(row[json_column_index])
                
                # Flatten the JSON data for each row
                flattened_row = flatten_json(json_data)
                flattened_data.append(flattened_row)

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on row {row_number}: {e}")
                continue

    # Dynamically determine all unique keys across all rows
    all_keys = set()
    for row in flattened_data:
        all_keys.update(row.keys())
    all_keys = sorted(all_keys)  # Sort for consistent output

    # Write the flattened data to the output CSV
    with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=all_keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(flattened_data)

    print(f"Processing complete. Output written to: {output_file}")

def flatten_json(data, parent_key='', sep='_'):
    """
    Flattens nested JSON data into a single-level dictionary.

    Args:
        data (dict): The JSON data to flatten.
        parent_key (str): The base key to use for recursion.
        sep (str): Separator to use for nested keys.

    Returns:
        dict: A flattened dictionary.
    """
    items = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, (dict, list)):
                items.extend(flatten_json(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
    elif isinstance(data, list):
        for i, element in enumerate(data):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_json(element, new_key, sep=sep).items())
    return dict(items)

# Prompt the user for the input file path and output file path
input_file = input("Enter the path to the input CSV file: ").strip()
output_file = input("Enter the path to the output CSV file: ").strip()

process_audit_logs(input_file, output_file)
