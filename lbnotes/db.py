from flask import current_app, g
from flask.cli import with_appcontext
import click 
import sqlite3
import os


def get_db():
    if not hasattr(g, "db"):
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    if hasattr(g, "db"):
        g.db.close()
        g.pop("db")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)


@click.command("init-db")
@with_appcontext
def init_db():
    # initialize the database
    if os.path.exists(current_app.config["DATABASE"]):
        answer = input("old database detected, proceed? (y/N):")
        if answer.upper() != "Y":
            return
        else:
            os.unlink(current_app.config["DATABASE"])

    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "db_schema.sql"
    )
    script = open(script_path)
    db = sqlite3.connect(current_app.config["DATABASE"])
    db.executescript(script.read())
    db.commit()
    db.close()
    script.close()
    click.echo("sqlite3 database initialized.")