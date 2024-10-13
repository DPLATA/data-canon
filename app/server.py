# wsgi.py
from flask import Flask, request, jsonify
import csv
import mysql.connector
from mysql.connector import Error, pooling
import logging
from app.config import DB_CONFIG
from app.utils.validation import validate_table_name, validate_csv_data


app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create connection pool
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
except Error as e:
    logging.error(f"Error creating connection pool: {e}")
    raise


def get_db_connection():
    try:
        return connection_pool.get_connection()
    except Error as e:
        logging.error(f"Error getting connection from pool: {e}")
        return None


@app.route('/upload/<table_name>', methods=['POST'])
def upload_csv(table_name):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        try:
            validate_table_name(table_name)
            csv_data = csv.DictReader(file.stream.read().decode("UTF-8").splitlines())
            rows = list(csv_data)
            validate_csv_data(rows)
            connection = get_db_connection()
            if not connection:
                return jsonify({"error": "Database connection failed"}), 500

            cursor = connection.cursor(prepared=True)

            for i in range(0, len(rows), 1000):
                batch = rows[i:i + 1000]
                columns = list(batch[0].keys())
                placeholders = ', '.join(['%s'] * len(columns))
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                values = [tuple(row[col] for col in columns) for row in batch]

                cursor.executemany(query, values)

            connection.commit()
            cursor.close()
            connection.close()

            logging.info(f"Successfully uploaded {len(rows)} rows to {table_name}")
            return jsonify({"message": f"Successfully uploaded {len(rows)} rows to {table_name}"}), 200
        except Error as e:
            logging.error(f"Database error: {e}")
            return jsonify({"error": "A database error occurred"}), 500
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500
    else:
        return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400
