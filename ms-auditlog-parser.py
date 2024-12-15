import csv
import json
import os

def process_audit_logs():
    # Prompt user for the input file path
    input_file_path = input("Enter the path of the input CSV file: ").strip()

    # Check if the file exists
    if not os.path.exists(input_file_path):
        print(f"Error: File '{input_file_path}' not found.")
        return

    # Read the input CSV and process each row
    output_file_path = os.path.splitext(input_file_path)[0] + "_processed.csv"

    with open(input_file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        processed_rows = []
        all_fieldnames = set()  # To track all unique fieldnames from all rows

        for row in reader:
            # Load the JSON data from the 6th column
            json_data = row[list(row.keys())[5]]
            try:
                data = json.loads(json_data.replace('""', '"'))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for row {reader.line_num}: {e}")
                continue

            # Flatten JSON data if necessary (you can add more flattening logic here if needed)

            # Consolidate IP addresses
            ip_addresses = set()
            if 'ClientIP' in data and data['ClientIP']:
                ip_addresses.add(data['ClientIP'])
            if 'ClientIPAddress' in data and data['ClientIPAddress']:
                ip_addresses.add(data['ClientIPAddress'])

            # Create a new IPAddresses field
            data['IPAddresses'] = ', '.join(ip_addresses)

            # Reorder columns: CreationTime first, followed by IPAddresses, then the rest
            ordered_data = {'CreationTime': data.get('CreationTime', '')}
            ordered_data['IPAddresses'] = data.get('IPAddresses', '')

            # Add the specified fields after 'CreationTime' and 'IPAddresses'
            ordered_data['Operation'] = data.get('Operation', '')
            ordered_data['Folders'] = data.get('Folders', '')
            ordered_data['AffectedItems'] = data.get('AffectedItems', '')
            ordered_data['Item'] = data.get('Item', '')

            # Add remaining fields
            for key, value in data.items():
                if key not in ['CreationTime', 'IPAddresses', 'Operation', 'Folders', 'AffectedItems', 'Item']:
                    ordered_data[key] = value
                    all_fieldnames.add(key)  # Track every key encountered

            processed_rows.append(ordered_data)

        # Include the fieldnames from the processed rows, ensuring every key is in the final list
        fieldnames = ['CreationTime', 'IPAddresses', 'Operation', 'Folders', 'AffectedItems', 'Item'] + list(all_fieldnames)

        # Write the processed data to a new CSV file
        with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)

    print(f"Processing complete! Output saved to '{output_file_path}'")

if __name__ == "__main__":
    process_audit_logs()
