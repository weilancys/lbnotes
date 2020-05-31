from flask import Flask
from flask_wtf import CSRFProtect
import os

def create_app(testing=False):
    # app instance
    app = Flask(__name__, instance_relative_config=True)

    # make sure app instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # config
    # dev config
    app.config.from_mapping(
        SECRET_KEY = "lightblue",
        DATABASE = os.path.join(app.instance_path, "lbnotes.sqlite3"),

        # config for simplemde
        SIMPLEMDE_JS_IIFE = False,
        SIMPLEMDE_USE_CDN = False,
    )

    if testing:
        # testing config
        app.config.update(
            DATABASE = os.path.join(app.instance_path, "test_lbnotes.sqlite3"),
            SECRET_KEY = "testing",
            TESTING = True,
            WTF_CSRF_ENABLED = False,
        )
    else:
        # production config from config.py in instance folder
        app.config.from_pyfile("config.py", silent=True)

    # a route to test app works
    @app.route("/hello")
    def hello():
        return "<h1>hello world.</h1>"

    # database
    from lbnotes import db
    db.init_app(app)

    # register blueprints
    from lbnotes import auth, notes, tags
    app.register_blueprint(auth.bp)
    app.register_blueprint(notes.bp)
    app.register_blueprint(tags.bp)

    app.add_url_rule('/', "notes.list_notes")

    # simplemde init
    notes.simple_mde.init_app(app)

    # flask-wtf init
    CSRFProtect(app)

    return app