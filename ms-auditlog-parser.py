import csv
import json
import os
import re
from collections import Counter

def sanitize_json_field(json_field):
    """
    Sanitizes JSON-like data into valid JSON:
    - Removes embedded newlines.
    - Replaces improperly escaped slashes (\/) with unescaped slashes (/).
    - Ensures proper JSON formatting by addressing trailing commas.
    """
    try:
        if not json_field or not isinstance(json_field, str):
            return json_field  # Skip if empty or not a string

        # Replace escaped forward slashes
        sanitized = json_field.replace(r"\/", "/")

        # Remove embedded newline characters
        sanitized = sanitized.replace("\r", "").replace("\n", "")

        # Remove trailing commas before closing braces or brackets
        sanitized = re.sub(r",\s*([\]}])", r"\1", sanitized)

        return sanitized
    except Exception as e:
        print(f"Error sanitizing JSON field: {e}")
        return json_field  # Return the raw field if sanitization fails
    
def parse_audit_data(audit_data):
    """
    Parses the sanitized JSON field.
    """
    try:
        sanitized_data = sanitize_json_field(audit_data)
        return json.loads(sanitized_data)
    except json.JSONDecodeError as e:
        print(f"Error parsing AuditData: {e}")
        return None  # Return None if parsing fails    

def process_audit_logs():
    input_file_path = input("Enter the path of the input CSV file: ").strip()
    if not os.path.exists(input_file_path):
        print(f"Error: File '{input_file_path}' not found.")
        return

    output_file_path = os.path.splitext(input_file_path)[0] + "_processed.csv"
    ip_list_file_path = os.path.splitext(input_file_path)[0] + "_unique_ips.txt"

    ip_counter = Counter()
    processed_rows = []
    all_fieldnames = set()

    with open(input_file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            json_data = row.get("AuditData", "")
            audit_data_error = ""
            try:
                # Sanitize and parse AuditData
                sanitized_data = sanitize_json_field(json_data)
                data = json.loads(sanitized_data)
            except json.JSONDecodeError as e:
                audit_data_error = "Parsing failed"
                print(f"Error decoding JSON for row {reader.line_num}: {e}")
                data = {}  # Use empty dict to proceed with the row

            ip_addresses = set()
            if "ClientIP" in data:
                ip_addresses.add(data["ClientIP"])
            if "ClientIPAddress" in data:
                ip_addresses.add(data["ClientIPAddress"])

            ip_counter.update(ip_addresses)
            data["IPAddresses"] = ", ".join(ip_addresses)

            ordered_data = {
                "CreationTime": data.get("CreationTime", ""),
                "IPAddresses": data.get("IPAddresses", ""),
                "Operation": data.get("Operation", ""),
                "AffectedItems": json.dumps(data.get("AffectedItems", "")),
                "Item": json.dumps(data.get("Item", "")),
                "Folders": json.dumps(data.get("Folder", "")),
                "AuditData_Error": audit_data_error,
                "RawAuditData": json_data
            }

            for key, value in data.items():
                if key not in ordered_data:
                    ordered_data[key] = value
                    all_fieldnames.add(key)

            processed_rows.append(ordered_data)

    fieldnames = ["CreationTime", "IPAddresses", "Operation", "AffectedItems", "Item", "Folders", "AuditData_Error", "RawAuditData"] + list(all_fieldnames)

    with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)

    with open(ip_list_file_path, mode='w', encoding='utf-8') as ip_file:
        for ip, count in ip_counter.most_common():
            ip_file.write(f"{ip} - {count} occurrences\n")

    print(f"Processing complete! Output saved to '{output_file_path}'")
    print(f"Unique IPs saved to '{ip_list_file_path}'")

if __name__ == "__main__":
    process_audit_logs()
