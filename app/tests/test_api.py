# test_app.py
import unittest
from app.server import app
from io import BytesIO

class TestDBMigrationAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_csv_success(self):
        data = {'file': (BytesIO(b'column1,column2\nvalue1,value2'), 'test.csv')}
        response = self.app.post('/upload/test_table', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Successfully uploaded', response.json['message'])

    def test_upload_csv_no_file(self):
        response = self.app.post('/upload/test_table')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'No file part')

    def test_upload_csv_empty_filename(self):
        data = {'file': (BytesIO(b''), '')}
        response = self.app.post('/upload/test_table', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'No selected file')

    def test_upload_csv_invalid_format(self):
        data = {'file': (BytesIO(b'content'), 'test.txt')}
        response = self.app.post('/upload/test_table', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid file format. Please upload a CSV file.')

if __name__ == '__main__':
    unittest.main()