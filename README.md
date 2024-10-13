# Data Migration API

## Overview

This API is a Flask-based web service designed to manage and analyze employee data. It provides endpoints for uploading CSV data and retrieving specific metrics about employee hiring patterns.

## Features

- CSV data upload for departments, jobs, and employees
- Endpoint to retrieve the number of employees hired for each job and department in 2021, divided by quarter
- Endpoint to list departments that hired more employees than the mean of employees hired in 2021

## Prerequisites

- Python 3.9+
- MySQL database

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/DPLATA/data-canon.git
   cd data-canon
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your MySQL database and update the `DB_CONFIG` in `app/config.py` with your database credentials.

## Usage

1. Start the Flask server:
   ```
   python wsgi.py
   ```

2. The API will be available at `http://localhost:5000`.

### API Endpoints

- `POST /upload/<table_name>`: Upload CSV data for departments, jobs, or employees.
- `GET /employees_hired_by_quarter`: Get the number of employees hired for each job and department in 2021, divided by quarter.
- `GET /departments_above_mean_hiring`: Get departments that hired more employees than the mean in 2021.

## Running Tests

To run the tests, use the following command:

```
python -m unittest discover app/tests
```

## Future Improvements and Enhancements
While the current version of the Data Canon API is functional, there are several areas for potential improvement and enhancement:

- Implement more input validation and sanitization to prevent SQL injection.
- Refactor into blueprints for more modularity and scalability.
- Add authentication and authorization to secure the API.
- Implement rate limiting to prevent abuse of the API.
- Conduct smoke and performance testing.
- Create a Dockerfile for containerization (currently not necessary as we can expose it as a Unix service in a standalone VM on Digital Ocean).

## Current Deployment
The application is currently deployed as a Unix service on a standalone Virtual Machine hosted on Digital Ocean. This setup provides a simple and effective way to run the application without the need for containerization at this stage.

## Contact

Silverboi - diegogplata@gmail.com

Project Link: [https://github.com/DPLATA/data-canon](https://github.com/DPLATA/data-canon)


