# test_server.py
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from app.server import app
import mysql.connector


class TestServer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.server.get_connection_pool')
    def test_upload_csv_success(self, mock_get_connection_pool):
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection_pool.return_value = mock_pool
        mock_pool.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        data = {'file': (BytesIO(b'id,department\n1,HR\n2,IT'), 'departments.csv')}
        response = self.app.post('/upload/departments', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Successfully uploaded', response.json['message'])

    def test_upload_csv_no_file(self):
        response = self.app.post('/upload/departments')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'No file part')

    def test_upload_csv_empty_filename(self):
        data = {'file': (BytesIO(b''), '')}
        response = self.app.post('/upload/departments', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'No selected file')

    def test_upload_csv_invalid_format(self):
        data = {'file': (BytesIO(b'content'), 'test.txt')}
        response = self.app.post('/upload/departments', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid file format. Please upload a CSV file.')

    @patch('app.server.get_connection_pool')
    def test_employees_hired_by_quarter(self, mock_get_connection_pool):
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection_pool.return_value = mock_pool
        mock_pool.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'department': 'HR', 'job': 'Manager', 'Q1': 1, 'Q2': 2, 'Q3': 0, 'Q4': 3},
            {'department': 'IT', 'job': 'Developer', 'Q1': 2, 'Q2': 1, 'Q3': 3, 'Q4': 1}
        ]

        response = self.app.get('/employees_hired_by_quarter')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['department'], 'HR')
        self.assertEqual(response.json[1]['job'], 'Developer')

    @patch('app.server.get_connection_pool')
    def test_departments_above_mean_hiring(self, mock_get_connection_pool):
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection_pool.return_value = mock_pool
        mock_pool.get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'department': 'IT', 'hired': 15},
            {'id': 2, 'department': 'Sales', 'hired': 12}
        ]

        response = self.app.get('/departments_above_mean_hiring')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['department'], 'IT')
        self.assertEqual(response.json[1]['hired'], 12)

    @patch('app.server.get_connection_pool')
    def test_database_connection_error(self, mock_get_connection_pool):
        mock_get_connection_pool.return_value = None

        response = self.app.get('/employees_hired_by_quarter')

        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json)


if __name__ == '__main__':
    unittest.main()