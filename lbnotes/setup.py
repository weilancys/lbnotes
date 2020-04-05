# setup route

from flask import Blueprint, render_template, current_app, abort, request
import os
from lbnotes.db import init_db

bp = Blueprint("setup", __name__, url_prefix="/setup")

@bp.route("/initdb", methods=["GET", "POST"])
def setup():
    if os.path.exists(current_app.config["DATABASE"]):
        abort(404)

    if request.method == "GET":
        return render_template("setup/initdb.html")
    elif request.method == "POST":
        init_db()
        return "database initialized, /setup/initdb route will be destroyed."