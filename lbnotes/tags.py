from flask import Blueprint, g, request, abort, render_template, flash, redirect, url_for
from lbnotes.auth import login_required, login_required_ajax
from lbnotes.db import get_db
import sqlite3
from lbnotes.utils import parse_db_time, convert_to_time_str, FLASH_MESSAGE_TYPES

bp = Blueprint("tags", __name__, url_prefix="/tags")


class Tag(object):
    """ Tag class that represents a tag """
    def __init__(self, id, name, user_id, created_at, modified_at):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.created_at = created_at
        self.modified_at = modified_at

    def __str__(self):
        return "Tag {name}".format(self.name)

    @staticmethod
    def create(name, user):
        """ create a new tag and return the new tag as an object, if tag already exists, return the existing tag, if create failed, return None """
        db = get_db()
        sql = "insert into tags (name, user_id, created_at) values (?, ?, datetime());"
        try:
            db.execute(sql, (name, user._id))
            db.commit()
            return Tag.get_tag_by_name(name)
        except sqlite3.IntegrityError as e:
            db.rollback()
            return Tag.get_tag_by_name(name)
        except Exception as e:
            db.rollback()
            return None

    def update(self, new_name):
        """
            update a tag.
            a tag has only one field to be updated: name.
            sets modified_at after update.

            if update is successful, return True
            if update is unsuccessful, return False
        """
        db = get_db()
        sql = "update tags set name = ?, modified_at = datetime() where id = ?;"
        try:
            db.execute(sql, (new_name, self.id))
            db.commit()
            self.name = new_name
            self.modified_at = self.get_tag_by_name(new_name).modified_at
            return True
        except sqlite3.IntegrityError as e:
            db.rollback()
            return False

    
    def belongs_to_user(self, user):
        return self.user_id == user._id


    def remove(self):
        """
            removes the current tag
            if successful, return True
            if unsuccessful, return False
        """
        db = get_db()
        sql = "delete from tags where id = ?;"
        sql2 = "delete from relation_notes_tags where tag_id = ?;"
        try:
            db.execute(sql, (self.id, )) # remove self
            db.execute(sql2, (self.id, )) # remove relationships
            db.commit()
            return True
        except:
            db.rollback()
            return False

    @staticmethod
    def get_tag_by_name(tag_name):
        db = get_db()
        sql = "select * from tags where name = ?;"
        row = db.execute(sql, (tag_name, )).fetchone()
        if row is None:
            return None
        return Tag(row["id"], row["name"], row["user_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"]))

    @staticmethod
    def get_tag_by_id(tag_id):
        db = get_db()
        sql = "select * from tags where id = ?;"
        row = db.execute(sql, (tag_id, )).fetchone()
        if row is None:
            return None
        return Tag(row["id"], row["name"], row["user_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"]))


    @staticmethod
    def get_tags_by_id_s(tag_id_s):
        tags = [ Tag.get_tag_by_id(tag_id) for tag_id in tag_id_s ]
        return tags


    @staticmethod
    def get_tags_by_user(user):
        db = get_db()
        sql = "select * from tags where user_id = ?;"
        rows = db.execute(sql, (user._id, )).fetchall()
        tags = [ Tag(row["id"], row["name"], row["user_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"])) for row in rows ]
        return tags

    @staticmethod
    def search_tag_by_keyword(keyword):
        db = get_db()
        sql = "select * from tags where name like ?;"
        rows = db.execute(sql, ("%"+keyword+"%", )).fetchall()
        tags = [ Tag(row["id"], row["name"], row["user_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"])) for row in rows ]
        return tags

    def to_dict(self):
        """ converts current tag to dict  """
        dictionary = dict(
            id = self.id,
            name = self.name,
            user_id = self.user_id,
            created_at = convert_to_time_str(self.created_at),
            modified_at = None if self.modified_at is None else convert_to_time_str(self.modified_at)
        )
        return dictionary


@bp.route("/")
@login_required_ajax
def list_tags():
    tags = Tag.get_tags_by_user(g.user)
    return {"tags": [ tag.to_dict() for tag in tags ]}


@bp.route("/create", methods=["POST", ])
@login_required_ajax
def create_tag():
    tag_name = request.form.get("tag_name", None)
    if tag_name is None:
        abort(400)
    
    new_tag = Tag.create(tag_name, g.user)
    if new_tag is None:
        return {"success": False, "tag": None, "reason": "tag creation failed."}
    else:
        return {"success": True, "tag": new_tag.to_dict(), "reason": None}


@bp.route("/manage")
def manage_tags():
    tags = Tag.get_tags_by_user(g.user)
    return render_template("tags/manage.html", tags=tags)


@bp.route("/new")
@login_required
def new_tag(parameter_list):
    pass


@bp.route("<int:tag_id>/delete_confirm")
@login_required
def delete_confirm(tag_id):
    tag = Tag.get_tag_by_id(tag_id)
    if tag is None:
        abort(404)
    return render_template("tags/delete_confirm.html", tag=tag)


@bp.route("<int:tag_id>/delete", methods=["POST", ])
@login_required
def delete(tag_id):
    tag = Tag.get_tag_by_id(tag_id)
    if tag is None:
        abort(404)
    if not tag.belongs_to_user(g.user):
        abort(401)

    if not tag.remove():
        flash("delete tag failed", FLASH_MESSAGE_TYPES["error"])
    else:
        flash("delete tag successful", FLASH_MESSAGE_TYPES["info"])
    return redirect(url_for('tags.manage_tags'))


@bp.route("<int:tag_id>/update", methods=["GET", "POST"])
@login_required
def update(tag_id):
    if request.method == "GET":
        tag = Tag.get_tag_by_id(tag_id)
        if tag is None:
            abort(404)
        if not tag.belongs_to_user(g.user):
            abort(401)
        return render_template("tags/update_tag.html", tag=tag)
    elif request.method == "POST":
        tag_name = request.form.get("tag_name", None)
        if tag_name is None:
            abort(404)
        tag = Tag.get_tag_by_id(tag_id)
        if not tag.update(tag_name):
            flash("update tag failed", FLASH_MESSAGE_TYPES["error"])
        else:
            flash("update tag successful", FLASH_MESSAGE_TYPES["info"])
        return redirect(url_for('tags.manage_tags'))
        