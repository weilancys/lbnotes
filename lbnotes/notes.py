from flask import Blueprint, request, render_template, abort, g, redirect, url_for, flash
from flask_simplemde import SimpleMDE
from lbnotes.auth import login_required
from lbnotes.db import get_db
from lbnotes.utils import parse_db_time, FLASH_MESSAGE_TYPES
from lbnotes.tags import Tag
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, FieldList
from wtforms.validators import DataRequired, Optional
import sqlite3

bp = Blueprint("notes", __name__, url_prefix="/notes")

simple_mde = SimpleMDE()


class Note(object):
    """ note class that represents a note, the core concept of this simple web app """
    def __init__(self, id, title, body, author_id, created_at, modified_at):
        self.id = id
        self.title = title
        self.body = body
        self.author_id = author_id
        self.created_at = created_at
        self.modified_at = modified_at
        self.tags = self.query_tags()
    

    def __str__(self):
        return "Note {name}".format(self.title)


    def query_tags(self):
        """ query database and populate the tags field of the note object  """
        db = get_db()
        sql = "select tags.id as id, tags.name as name, tags.user_id as user_id, tags.created_at as created_at, tags.modified_at as modified_at from relation_notes_tags as relation left join tags on relation.tag_id = tags.id where relation.note_id = ?;"
        rows = db.execute(sql, (self.id, )).fetchall()
        return [ Tag(row["id"], row["name"], row["user_id"], row["created_at"], row["modified_at"]) for row in rows ]


    def link_tag(self, tag):
        """ add a new relationship from current note to a tag  """
        db = get_db()
        sql = "insert into relation_notes_tags (note_id, tag_id, created_at) values (?, ?, datetime());"

        # check if tag belongs to current user
        if not tag.belongs_to_user(g.user):
            return False
        try:
            db.execute(sql, (self.id, tag.id))
            db.commit()
            return True
        except sqlite3.IntegrityError as e:
            db.rollback()
            return True
        except Exception as e:
            db.rollback()
            raise
            return False


    def unlink_all_tags(self):
        """ clears many to many relationships between current note and all its tags  """
        db = get_db()
        sql = "delete from relation_notes_tags where note_id = ?;"
        try:
            db.execute(sql, (self.id, ))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False


    def belongs_to_user(self, user):
        """ check if current note belongs to user """
        return self.author_id == user._id


    def update(self, title, body, tag_id_s=[]):
        """ update a note, clear its tags and re-add edited tags """
        # checks if note belongs to current user
        if not self.belongs_to_user(g.user):
            abort(403)

        db = get_db()
        sql = "update notes set title=?, body=?, modified_at=datetime() where id=?;"
        try:
            db.execute(sql, (title, body, self.id))
            self.unlink_all_tags()
            tags = Tag.get_tags_by_id_s(tag_id_s)
            for tag in tags:
                # get rid of tags that don't belong to current user.
                if not tag.belongs_to_user(g.user):
                    tags.remove(tag)
            for tag in tags:
                if not self.link_tag(tag):
                    raise RuntimeError("tags insertion failed.")
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise
            return False


    def remove(self):
        # remove the note from database and all its relationships with tags.
        if not self.belongs_to_user(g.user):
            abort(403)
        db = get_db()
        sql = "delete from notes where id = ?;"
        try:
            db.execute(sql, (self.id, ))
            if not self.unlink_all_tags():
                raise RuntimeError("error unlinking all tags while deleting note.")
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False


    @staticmethod
    def search_note_by_keyword(keyword):
        db = get_db()
        sql = "select * from notes where body like ? or title like ?;"
        rows = db.execute(sql, ("%"+keyword+"%", "%"+keyword+"%")).fetchall()
        notes = [ Note(row["id"], row["title"], row["body"], row["author_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"])) for row in rows ]
        return notes


    @staticmethod
    def create(title, body, author_id, tags=[]):
        db = get_db()
        sql = "insert into notes (title, body, author_id, created_at) values (?, ?, ?, datetime());"
        try:
            db.execute(sql, (title, body, author_id))
            row = db.execute("select * from notes where title=? and body=?;", (title, body)).fetchone()
            new_note = Note(row["id"], row["title"], row["body"], row["author_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"]))
            for tag in tags:
                if new_note.link_tag(tag) == False:
                    raise RuntimeError("tags insertion failed.")
            db.commit()
            return new_note
        except Exception as e:
            db.rollback()
            raise
            return None


    @staticmethod
    def get_note_by_id(note_id):
        db = get_db()
        sql = "select * from notes where id = ?;"
        row = db.execute(sql, (note_id, )).fetchone()
        if row is None:
            return None
        return Note(row["id"], row["title"], row["body"], row["author_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"]))
    

    @staticmethod
    def get_notes_by_user_and_tag(user, tag):
        if tag is None:
            # gets all notes of the user without any tags attached
            db = get_db()
            sql = "select * from notes where id not in (select distinct note_id from relation_notes_tags);"
            rows = db.execute(sql, ()).fetchall()
            return [ Note(row["id"], row["title"], row["body"], row["author_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"])) for row in rows ]
        else:
            # gets all notes that have tag attached
            db = get_db()
            sql = "select * from notes join relation_notes_tags as relation on notes.id = relation.note_id where relation.tag_id = ? and notes.author_id = ?;"
            notes = db.execute(sql, (tag.id, user._id)).fetchall()
            return notes


    @staticmethod
    def get_notes_by_user(user):
        db = get_db()
        sql = "select id, title, body, author_id, created_at, modified_at from notes where author_id = ? order by created_at desc;"
        rows = db.execute(sql, (user._id, )).fetchall()
        notes = [ Note(row["id"], row["title"], row["body"], row["author_id"], parse_db_time(row["created_at"]), parse_db_time(row["modified_at"])) for row in rows ]
        return notes


class NewNoteForm(FlaskForm):
    title = StringField('title', validators=[DataRequired("title required")])
    body = StringField('body', validators=[DataRequired("note body required")])
    #tags = FieldList(HiddenField("tags", Optional()))


class UpdateNoteForm(FlaskForm):
    title = StringField('title', validators=[DataRequired("title required")])
    body = StringField('body', validators=[DataRequired("note body required")])
    #tags = FieldList(HiddenField("tags", Optional())


class NoteDeleteConfirmForm(FlaskForm):
    pass


@bp.route("/")
@login_required
def list_notes():
    tag_name = request.args.get("tag", None)
    if tag_name:
        if tag_name == "no_tag":
            notes = Note.get_notes_by_user_and_tag(g.user, None)
        else:
            tag = Tag.get_tag_by_name(tag_name)
            if tag is None:
                abort(404)
            notes = Note.get_notes_by_user_and_tag(g.user, tag)
    else:
        # get all notes of user
        notes = Note.get_notes_by_user(g.user)
    tags = Tag.get_tags_by_user(g.user)
    return render_template("notes/list_notes.html", notes=notes, tags=tags)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_note():
    new_note_form = NewNoteForm()
    if new_note_form.validate_on_submit():
        title = new_note_form.title.data
        body = new_note_form.body.data
        #tags = new_note_form.tags.data
        tag_id_s = request.form.getlist("tags")
        tags = Tag.get_tags_by_id_s(tag_id_s)
        # make sure tags belong to user
        for tag in tags:
            if not tag.belongs_to_user(g.user):
                tags.remove(tag)
        new_note = Note.create(title, body, g.user._id, tags)
        return redirect(url_for('notes.view_note', note_id=new_note.id))
    return render_template("notes/new_note.html", form=new_note_form)
            

@bp.route("/<int:note_id>")
@login_required
def view_note(note_id):
    note = Note.get_note_by_id(note_id)
    if note is None:
        abort(404)
    if not note.belongs_to_user(g.user):
        abort(401)
    return render_template("notes/view_note.html", note=note, tags=note.tags)


@bp.route("/<int:note_id>/update", methods=["GET", "POST"])
@login_required
def update_note(note_id):
    form = UpdateNoteForm()
    note = Note.get_note_by_id(note_id)
    if note is None:
        abort(404)
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        tag_id_s = request.form.getlist("tags")
        if note.update(title, body, tag_id_s):
            flash("update successful", FLASH_MESSAGE_TYPES["info"])
            return redirect(url_for("notes.view_note", note_id=note.id))
        else:
            flash("update failed", FLASH_MESSAGE_TYPES["info"])
    return render_template("notes/update_note.html", note=note, tags=note.tags, form=form)


@bp.route("/<int:note_id>/delete_confirm")
@login_required
def delete_note_confirm(note_id):
    note = Note.get_note_by_id(note_id)
    form = NoteDeleteConfirmForm()
    if note is None:
        abort(404)
    return render_template("notes/delete_confirm.html", note=note, form=form)


@bp.route("/<int:note_id>/delete", methods=["POST", ])
@login_required
def delete_note(note_id):
    note = Note.get_note_by_id(note_id)
    if note is None:
        abort(404)
    if not note.belongs_to_user(g.user):
        abort(401)
    if note.remove():
        flash("note deleted", FLASH_MESSAGE_TYPES["info"])
        return redirect(url_for("notes.list_notes"))
    else:
        flash("note not deleted", FLASH_MESSAGE_TYPES["error"])
        return redirect(url_for("notes.update_note", note_id=note.id))


@bp.route("/search")
@login_required
def search():
    keyword = request.args.get("keyword", None)
    if keyword is None:
        abort(404)
    notes = Note.search_note_by_keyword(keyword)
    tags = Tag.search_tag_by_keyword(keyword)
    return render_template("notes/search_result.html", notes=notes, tags=tags)