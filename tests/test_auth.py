import unittest
import os
from lbnotes import create_app
from lbnotes.auth import User
from lbnotes.db import generate_database, get_db
from flask import session, g, request
from flask_wtf.csrf import generate_csrf
from utils import insert_test_data, login_for_test


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True) 
        self.client = self.app.test_client()

        with self.app.app_context():
            generate_database()
            insert_test_data(self.app)

        self.login_url = "/auth/login"
        self.logout_url = "/auth/logout"
        self.register_url = "/auth/register"
        

    def test_login_get(self):
        with self.client as client:
            response = client.get(self.login_url)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"login - lbnotes", response.data)

    
    def test_login_post(self):
        with self.app.test_request_context():
            with self.client as client:
                response = login_for_test(1, client) 
                self.assertEqual(session["user_id"], 1)
                self.assertIn(b"notes - lbnotes", response.data)
                self.assertEqual(g.user.username, "test")
                self.assertEqual(g.user._id, 1)
            
    
    def test_logout(self):
        with self.app.test_request_context():
            with self.client as client:
                response = client.get(self.logout_url, follow_redirects=True)
                self.assertIn(b"login - lbnotes", response.data)
                self.assertNotIn("user_id", session)


    def test_register_get(self):
         with self.client as client:
            response = client.get(self.register_url)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"register - lbnotes", response.data)


    def test_register_post(self):
        with self.client as client:
            response_raw = client.post(self.register_url, data={"username": "test3", "password_1":"test", "password_2":"test"}, follow_redirects=True)
            new_user = User.get_user_by_username("test3")
            self.assertIsNotNone(new_user)


    def tearDown(self):
        os.unlink(self.app.config["DATABASE"])