import unittest
import os
from lbnotes.notes import Note
from lbnotes.db import generate_database
from lbnotes import create_app
from lbnotes.tags import Tag
from utils import insert_test_data, login_for_test
from flask import g


class TestNote(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            generate_database()
            insert_test_data(self.app)
    

    def test_new_note(self):
        with self.app.app_context():
            new_note = Note.create('test note', 'this is a note for test.', 1, [])
            retrieved_note = Note.get_note_by_id(new_note.id)
            self.assertEqual(retrieved_note.title, "test note")
    

    def test_get_note(self):
        with self.app.app_context():
            note = Note.get_note_by_id(1)
            self.assertEqual(note.title, "test")
    

    def test_remove_note(self):
        with self.app.app_context():
            with self.client as client:
                login_for_test(1, client)
                note = Note.get_note_by_id(1)
                note.remove()
                self.assertIsNone(Note.get_note_by_id(1))

    
    def test_update_note(self):
        with self.app.app_context():
            with self.client as client:
                login_for_test(1, client)
                note = Note.get_note_by_id(1)
                note.update('test', 'test updated', [])
                note = Note.get_note_by_id(1)
                self.assertEqual(note.body, 'test updated')
    

    def test_link_tag(self):
        with self.app.app_context():
            with self.client as client:
                login_for_test(1, client)
                new_note = Note.create("test for tag", "test for tag", g.user._id)
                tag_1 = Tag.get_tag_by_name("tag 1")
                new_note.link_tag(tag_1)
                self.assertEqual(tag_1.name, new_note.query_tags()[0].name)
    

    def test_unlink_tags(self):
        with self.app.app_context():
            with self.client as client:
                login_for_test(1, client)
                new_note = Note.create("test for tag", "test for tag", g.user._id)
                note = Note.get_note_by_id(2)
                self.assertEqual(note.query_tags()[0].name, 'tag 1')
                note.unlink_all_tags()
                self.assertEqual(note.query_tags(), [])


    def tearDown(self):
        self.client.get("/auth/logout")
        os.unlink(self.app.config["DATABASE"])
        