import unittest 
from lbnotes import create_app


class TestAppFactory(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()


    def test_testing_mode_enabled(self):
        self.assertTrue(self.app.testing)


    def test_hello_world(self):
        response = self.client.get('/hello')
        self.assertIn(b"hello world", response.data)