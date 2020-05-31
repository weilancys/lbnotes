import unittest
from lbnotes.db import get_db, generate_database
from lbnotes import create_app
import os


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.cli_runner = self.app.test_cli_runner()
        with self.app.app_context():
            generate_database()
    

    def test_get_db(self):
        with self.app.app_context():
            db = get_db()
            self.assertIs(db, get_db())


    def test_warning_before_create_database(self):
        result = self.cli_runner.invoke(args=['init-db'])
        self.assertIn("old database detected", result.output)


    def tearDown(self):
        os.unlink(self.app.config["DATABASE"])