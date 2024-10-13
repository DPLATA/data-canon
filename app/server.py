# server.py
from flask import Flask, request, jsonify
import csv
import mysql.connector
from mysql.connector import Error
import logging
from app.config import DB_CONFIG
from app.utils.validation import convert_datetime, validate_integer

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

connection_pool = None

def get_connection_pool():
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
        except Error as e:
            logging.error(f"Error creating connection pool: {e}")
            raise
    return connection_pool


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
            csv_content = file.stream.read().decode("UTF-8").splitlines()
            csv_reader = csv.reader(csv_content)
            rows = list(csv_reader)

            table_schemas = {
                'departments': {'columns': ['id', 'department'], 'integer_cols': ['id'], 'datetime_cols': []},
                'jobs': {'columns': ['id', 'job'], 'integer_cols': ['id'], 'datetime_cols': []},
                'employees': {'columns': ['id', 'name', 'hire_datetime', 'department_id', 'job_id'],
                              'integer_cols': ['id', 'department_id', 'job_id'],
                              'datetime_cols': ['hire_datetime']}
            }

            if table_name not in table_schemas:
                return jsonify({"error": f"Unknown table name: {table_name}"}), 400

            connection = get_db_connection()
            if not connection:
                return jsonify({"error": "Database connection failed"}), 500

            cursor = connection.cursor(prepared=True)

            schema = table_schemas[table_name]
            columns = schema['columns']
            integer_cols = schema['integer_cols']
            datetime_cols = schema['datetime_cols']
            placeholders = ', '.join(['%s'] * len(columns))
            columns_escaped = ', '.join(f"`{col}`" for col in columns)
            query = f"INSERT INTO `{table_name}` ({columns_escaped}) VALUES ({placeholders})"

            processed_rows = []
            for row in rows:
                processed_row = []
                for i, col in enumerate(columns):
                    value = row[i] if i < len(row) else ''
                    if col in integer_cols:
                        processed_value = validate_integer(value)
                        if processed_value is None:
                            logging.warning(f"Invalid integer value '{value}' for column '{col}'. Row skipped.")
                            break
                        processed_row.append(processed_value)
                    elif col in datetime_cols:
                        processed_value = convert_datetime(value)
                        if processed_value is None:
                            logging.warning(f"Invalid datetime value '{value}' for column '{col}'. Row skipped.")
                            break
                        processed_row.append(processed_value)
                    else:
                        processed_row.append(value)

                if len(processed_row) == len(columns):
                    processed_rows.append(processed_row)

            if not processed_rows:
                return jsonify({"error": "No valid data to insert"}), 400

            for i in range(0, len(processed_rows), 1000):
                batch = processed_rows[i:i + 1000]
                cursor.executemany(query, batch)

            connection.commit()
            cursor.close()
            connection.close()

            logging.info(f"Successfully uploaded {len(processed_rows)} rows to {table_name}")
            return jsonify({"message": f"Successfully uploaded {len(processed_rows)} rows to {table_name}"}), 200
        except Error as e:
            logging.error(f"Database error: {e}")
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400


@app.route('/employees_hired_by_quarter', methods=['GET'])
def employees_hired_by_quarter():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT 
                d.department,
                j.job,
                SUM(CASE WHEN QUARTER(e.hire_datetime) = 1 THEN 1 ELSE 0 END) AS Q1,
                SUM(CASE WHEN QUARTER(e.hire_datetime) = 2 THEN 1 ELSE 0 END) AS Q2,
                SUM(CASE WHEN QUARTER(e.hire_datetime) = 3 THEN 1 ELSE 0 END) AS Q3,
                SUM(CASE WHEN QUARTER(e.hire_datetime) = 4 THEN 1 ELSE 0 END) AS Q4
            FROM 
                employees e
            JOIN 
                departments d ON e.department_id = d.id
            JOIN 
                jobs j ON e.job_id = j.id
            WHERE 
                YEAR(e.hire_datetime) = 2021
            GROUP BY 
                d.department, j.job
            ORDER BY 
                d.department, j.job
            """

        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify(results), 200

    except Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/departments_above_mean_hiring', methods=['GET'])
def departments_above_mean_hiring():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        query = """
            WITH department_hires AS (
                SELECT 
                    d.id,
                    d.department,
                    COUNT(*) as hired
                FROM 
                    employees e
                JOIN 
                    departments d ON e.department_id = d.id
                WHERE 
                    YEAR(e.hire_datetime) = 2021
                GROUP BY 
                    d.id, d.department
            ),
            mean_hires AS (
                SELECT AVG(hired) as mean_hired
                FROM department_hires
            )
            SELECT 
                dh.id,
                dh.department,
                dh.hired
            FROM 
                department_hires dh,
                mean_hires mh
            WHERE 
                dh.hired > mh.mean_hired
            ORDER BY 
                dh.hired DESC
            """

        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify(results), 200

    except Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
