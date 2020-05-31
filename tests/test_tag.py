import unittest
from lbnotes.tags import Tag
from lbnotes import create_app
from lbnotes.db import generate_database
from utils import insert_test_data, login_for_test
import json
import os


class TestTag(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            generate_database()
            insert_test_data(self.app)


    def test_get_tags(self):
        with self.client as client:
            login_for_test(1, client)
            response_raw = client.get("/tags/")
            response_json = response_raw.get_data(as_text=True)
            response = json.loads(response_json)
            self.assertEqual(len(response["tags"]), 2)
            self.assertIn(response["tags"][0]["name"], ["tag 1", "tag 2"])


    def test_create_tag(self):
        with self.client as client:
            login_for_test(1, client)
            response_raw = client.post("/tags/create", data={"tag_name": "tag 3"})
            response_json = response_raw.get_data(as_text=True)
            response = json.loads(response_json)
            self.assertTrue(response["success"])
            self.assertIsNotNone(Tag.get_tag_by_name("tag 3"))

    
    def test_update_tag(self):
        with self.client as client:
            tag_id = 2
            login_for_test(1, client)
            client.post("/tags/{tag_id}/update".format(tag_id=tag_id), data={"tag_name": "tag 3"})
            updated_tag = Tag.get_tag_by_id(tag_id)
            self.assertEqual(updated_tag.name, "tag 3")

        
    def test_delete_tag(self):
        with self.client as client:
            login_for_test(1, client)
            client.post("/tags/1/delete")
            tag = Tag.get_tag_by_id(1)
            self.assertIsNone(tag)


    def tearDown(self):
        os.unlink(self.app.config["DATABASE"])
