--
-- File generated with SQLiteStudio v3.2.1 on Sun Mar 22 00:46:07 2020
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: notes
CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL UNIQUE, body TEXT NOT NULL, author_id INTEGER REFERENCES users (id) ON DELETE SET NULL NOT NULL, created_at DATETIME NOT NULL, modified_at DATETIME);

-- Table: relation_notes_tags
CREATE TABLE relation_notes_tags (id INTEGER PRIMARY KEY AUTOINCREMENT, note_id INTEGER REFERENCES notes (id) ON DELETE CASCADE NOT NULL, tag_id INTEGER REFERENCES tags (id) ON DELETE CASCADE NOT NULL, created_at DATETIME NOT NULL, UNIQUE (note_id, tag_id));

-- Table: tags
CREATE TABLE tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, created_at DATETIME NOT NULL, user_id INTEGER REFERENCES users (id) ON DELETE CASCADE NOT NULL, modified_at DATETIME);

-- Table: users
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password INTEGER NOT NULL, created_at DATETIME NOT NULL);

-- Index: index_title_body
CREATE INDEX index_title_body ON notes (title, body);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;