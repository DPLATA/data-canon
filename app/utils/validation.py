# validation.py
from datetime import datetime
import logging

def convert_datetime(dt_string):
    try:
        dt = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        logging.error(f"Invalid datetime format: {dt_string}")
        return None

def validate_integer(value):
    try:
        return int(value) if value else None
    except ValueError:
        return None