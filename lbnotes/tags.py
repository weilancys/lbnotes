from flask import Blueprint, g, request, abort
from lbnotes.auth import login_required, login_required_ajax
from lbnotes.db import get_db
import sqlite3

bp = Blueprint("tags", __name__, url_prefix="/tags")


class Tag():
    pass


@bp.route("/")
@login_required_ajax
def list_tags():
    db = get_db()
    sql = "select * from tags where user_id = ?;"
    tags = db.execute(sql, (g.user._id, )).fetchall()
    return {"tags": [dict(tag) for tag in tags]}


@bp.route("/create", methods=["POST", ])
@login_required_ajax
def create_tag():
    tag_name = request.form.get("tag_name", None)
    if tag_name is None:
        abort(400)
    db = get_db()
    sql = "insert into tags (name, user_id, created_at) values (?, ?, datetime());"
    try:
        db.execute(sql, (tag_name, g.user._id))
        db.commit()
        tag = db.execute("select * from tags where name = ?;", (tag_name, )).fetchone()
        return {"success": True, "tag": dict(tag), "reason": None}
    except sqlite3.IntegrityError as e:
        db.rollback()
        return {"success": False, "tag": None, "reason": "tag already exists."}
    except Exception as e:
        db.rollback()
        return {"success": False, "tag": None, "reason": str(e)}
