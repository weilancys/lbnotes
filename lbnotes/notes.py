from flask import Blueprint, request, render_template, abort, g, redirect, url_for, flash
from flask_simplemde import SimpleMDE
from lbnotes.auth import login_required
from lbnotes.db import get_db

bp = Blueprint("notes", __name__, url_prefix="/notes")

simple_mde = SimpleMDE()


def check_note_belongs_to_user(note_id, user_id):
    note = get_note_by_id(note_id)
    return note["author_id"] == user_id


def get_note_by_id(note_id):
    db = get_db()
    sql = "select * from notes where id = ?;"
    note = db.execute(sql, (note_id, )).fetchone()
    return note


def get_notes_of_user(user_id):
    db = get_db()
    sql = "select id, title, body, author_id, created_at, modified_at from notes where author_id = ? order by created_at desc;"
    notes = db.execute(sql, (user_id, )).fetchall()
    return notes


def get_notes_of_user_by_tag(user_id, tag_name):
    db = get_db()
    if tag_name == "no_tag":
        sql = "select * from notes where id not in (select distinct note_id from relation_notes_tags);"
        notes = db.execute(sql).fetchall()
    else:
        tag = get_tag_by_name(tag_name) 
        sql = "select * from notes join relation_notes_tags as relation on notes.id = relation.note_id where relation.tag_id = ? and notes.author_id = ?;"
        notes = db.execute(sql, (tag["id"], user_id)).fetchall()
    return notes


def get_tag_by_name(tag_name):
    db = get_db()
    sql = "select * from tags where name = ?;"
    tag = db.execute(sql, (tag_name, )).fetchone()
    return tag


def get_tags_of_note(note_id):
    db = get_db()
    sql = "select tags.id as id, tags.name as name from relation_notes_tags as relation left join tags on relation.tag_id = tags.id where relation.note_id = ?;"
    tags = db.execute(sql, (note_id, )).fetchall()
    return tags


def get_tags_of_user(user_id):
    db = get_db()
    sql = "select * from tags where user_id = ?;"
    tags = db.execute(sql, (user_id, )).fetchall()
    return tags


def insert_new_note(title, body, user_id, tags):
    # this function inserts a new to and its tags into database
    # the parameter args is of type list
    db = get_db()
    sql = "insert into notes (title, body, author_id, created_at) values (?, ?, ?, datetime());"
    try:
        db.execute(sql, (title, body, user_id))
        new_note = db.execute("select * from notes where title=? and body=?;", (title, body)).fetchone()       
        if not insert_tags_of_note(new_note["id"], tags):
            raise Exception()
        db.commit()
        return new_note
    except Exception as e:
        db.rollback()
        return None


def insert_tags_of_note(note_id, tags):
    # insert tags of a note into database
    db = get_db()
    sql = "insert into relation_notes_tags (note_id, tag_id, created_at) values (?, ?, datetime());"
    try:
        for tag_id in tags:
            db.execute(sql, (note_id, tag_id))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    

def unlink_tags_of_note(note_id):
    # remove relations of note to all its tags, neither note nor tags are deleted.
    db = get_db()
    sql = "delete from relation_notes_tags where note_id = ?;"
    try:
        db.execute(sql, (note_id, ))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False


def update_note_by_id(note_id, title, body, tags):
    # update a note, clear its tags and re-add edited tags
    db = get_db()
    sql = "update notes set title=?, body=? where id=?;"
    try:
        db.execute(sql, (title, body, note_id))
        if not unlink_tags_of_note(note_id):
            raise Exception()
        if not insert_tags_of_note(note_id, tags):
            raise Exception()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False


def delete_note_by_id(note_id):
    # deleting a note takes the deletion of the note itself and its tags relation
    db = get_db()
    sql = "delete from notes where id = ?;"
    try:
        if not unlink_tags_of_note(note_id):
            raise Exception()
        db.execute(sql, (note_id, ))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False


def search_note_by_keyword(keyword):
    db = get_db()
    sql = "select * from notes where body like ? or title like ?;"
    db = get_db()
    notes = db.execute(sql, ("%"+keyword+"%", "%"+keyword+"%")).fetchall()
    return notes


def search_tag_by_keyword(keyword):
    db = get_db()
    sql = "select * from tags where name like ?;"
    db = get_db()
    tags = db.execute(sql, ("%"+keyword+"%", )).fetchall()
    return tags


@bp.route("/")
@login_required
def list_notes():
    tag_name = request.args.get("tag", None)
    if tag_name:
        if tag_name == "no_tag":
            notes = get_notes_of_user_by_tag(g.user._id, tag_name)
        else:
            notes = get_notes_of_user_by_tag(g.user._id, tag_name)
    else:
        notes = get_notes_of_user(g.user._id)
    tags = get_tags_of_user(g.user._id)
    return render_template("notes/list_notes.html", notes=notes, tags=tags)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_note():
    if request.method == "GET":
        return render_template("notes/new_note.html")
    elif request.method == "POST":
        title = request.form.get("title", None)
        body = request.form.get("body", None)
        tags = request.form.getlist("tags")
        if not title or not body:
            abort(400)
        new_note = insert_new_note(title, body, g.user._id, tags)
        if new_note is None:
            abort(400)
        else:
            return redirect(url_for("notes.view_note", note_id=new_note["id"]))
            

@bp.route("/<int:note_id>")
@login_required
def view_note(note_id):
    note = get_note_by_id(note_id)
    if note is None:
        abort(404)
    if note["author_id"] != g.user._id:
        abort(401)
    tags = get_tags_of_note(note_id)
    return render_template("notes/view_note.html", note=note, tags=tags)


@bp.route("/<int:note_id>/update", methods=["GET", "POST"])
@login_required
def update_note(note_id):
    if request.method == "GET":
        note = get_note_by_id(note_id)
        tags = get_tags_of_note(note_id)
        return render_template("notes/update_note.html", note=note, tags=tags)
    elif request.method == "POST":
        title = request.form.get("title", None)
        body = request.form.get("body", None)
        tags = request.form.getlist("tags")

        if not title or not body:
            abort(404)

        if update_note_by_id(note_id, title, body, tags):
            flash("update successful")
            return redirect(url_for("notes.view_note", note_id=note_id))
        else:
            flash("update uncessful")
            return redirect(url_for("notes.update_note", note_id=note_id))


@bp.route("/<int:note_id>/delete_confirm")
@login_required
def delete_note_confirm(note_id):
    return render_template("notes/delete_confirm.html", note_id=note_id)


@bp.route("/<int:note_id>/delete", methods=["POST", ])
@login_required
def delete_note(note_id):
    if not check_note_belongs_to_user(note_id, g.user._id):
        abort(401)
    if delete_note_by_id(note_id):
        flash("note deleted")
        return redirect(url_for("notes.list_notes"))
    else:
        flash("note not deleted")
        return redirect(url_for("notes.update_note", note_id=note_id))


@bp.route("/search")
@login_required
def search():
    keyword = request.args.get("keyword", None)
    if keyword is None:
        abort(404)
    notes = search_note_by_keyword(keyword)
    tags = search_tag_by_keyword(keyword)
    return render_template("notes/search_result.html", notes=notes, tags=tags)