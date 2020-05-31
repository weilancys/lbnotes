import os
from lbnotes.db import get_db

def insert_test_data(app):
        script_file_path = os.path.join(os.path.dirname(__file__), "data_for_test.sql")
        script_file = open(script_file_path)
        with app.app_context():
            db = get_db()
            db.executescript(script_file.read())
            db.commit()
        script_file.close()
        db.close()


def login_for_test(user_id, client):
    if user_id == 1:
        response = client.post("/auth/login", data={"username": "test", "password": "test"}, follow_redirects=True)
    elif user_id == 2:
        response = client.post("/auth/login", data={"username": "test2", "password": "test"}, follow_redirects=True)
    return response