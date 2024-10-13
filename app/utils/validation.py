# validation.py
import re

def validate_table_name(table_name):
    # Only allow alphanumeric characters and underscores
    if not re.match(r'^\w+$', table_name):
        raise ValueError("Invalid table name")
    return table_name

def validate_csv_data(rows):
    # Add any specific validation logic for your CSV data
    if not rows:
        raise ValueError("CSV file is empty")
    # Add more validation as needed
    return rows