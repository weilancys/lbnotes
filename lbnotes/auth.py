import functools
from flask import g, flash, redirect, Blueprint, session, request, render_template, url_for, abort
from lbnotes.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from lbnotes.utils import FLASH_MESSAGE_TYPES, parse_db_time
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import sqlite3

bp = Blueprint("auth", __name__, url_prefix="/auth")

class User(object):
    def __init__(self, _id, username, password, created_at):
        self._id = _id
        self.username = username
        self.password = password
        self.created_at = created_at
    
    @staticmethod
    def get_user_by_id(_id):
        db = get_db()
        sql = "select id, username, password, created_at from users where id=?;"
        row = db.execute(sql, (_id, )).fetchone()
        if row is None:
            return None
        else:
            return User(row["id"], row["username"], row["password"], parse_db_time(row["created_at"]))
    
    @staticmethod
    def get_user_by_username(username):
        db = get_db()
        sql = "select id, username, password, created_at from users where username=?;"
        row = db.execute(sql, (username, )).fetchone()
        if row is None:
            return None
        else:
            return User(row["id"], row["username"], row["password"], parse_db_time(row["created_at"]))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


@bp.before_app_request
def load_logged_in_user():
    if "user_id" in session:
        g.user = User.get_user_by_id(session["user_id"])
    else:
        g.user = None


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if g.user is None:
            flash("please login first", FLASH_MESSAGE_TYPES["info"])
            next = request.url
            return redirect(url_for("auth.login", next=next))
        return func(*args, **kwargs)
    return wrapper


def login_required_ajax(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if g.user is None:
            abort(403)
        return func(*args, **kwargs)
    return wrapper


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    elif request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)

        next = request.args.get("next", None)

        login_successful = False

        if not username or not password:
            flash("missing at least one field", FLASH_MESSAGE_TYPES["error"])
            abort(400)

        user = User.get_user_by_username(username)

        if g.user is not None:
            flash(g.user.username + " has already logged in", FLASH_MESSAGE_TYPES["error"])
        elif user is None:
            flash("user does not exist", FLASH_MESSAGE_TYPES["error"])
        elif not check_password_hash(user.password, password):
            flash("password incorrect", FLASH_MESSAGE_TYPES["error"])
        else:
            session["user_id"] = user._id
            login_successful = True

        if login_successful:
            if next:
                return redirect(next)
            else:
                return redirect(url_for("notes.list_notes"))
        else:
            if next:
                return redirect(url_for("auth.login", next=next))
            else:
                return redirect(url_for("auth.login"))
        

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    elif request.method == "POST":
        username = request.form.get("username", None)
        password_1 = request.form.get("password_1", None)
        password_2 = request.form.get("password_2", None)

        register_info_valid = True

        if not username or not password_1 or not password_2:
            flash("missing at least one field", FLASH_MESSAGE_TYPES["error"])
            register_info_valid = False
        
        if password_1 != password_2:
            flash("passwords don't match", FLASH_MESSAGE_TYPES["error"])
            register_info_valid = False

        if register_info_valid:
            db = get_db()
            sql = "insert into users (username, password, created_at) values (?, ?, datetime())"
            password = generate_password_hash(password_1)
            try:
                db.execute(sql, (username, password))
                db.commit()
            except sqlite3.IntegrityError as e:
                db.rollback()
                flash("user already exists", FLASH_MESSAGE_TYPES["error"])
                return redirect(url_for("auth.register"))
            flash("user successfully registered!", "info")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("auth.register"))


@bp.route("/logout")
def logout():
    if g.user is not None:
        g.user = None
    if "user_id" in session:
        session.clear()
        flash("successfully logged out", FLASH_MESSAGE_TYPES["info"])
    return redirect(url_for("auth.login"))


@bp.route("/profile")
@login_required
def user_profile():
    from lbnotes.tags import Tag
    return render_template("auth/user_profile.html", tags=Tag.get_tags_by_user(g.user))