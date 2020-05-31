-- users
-- password: test
insert into users (username, password, created_at) values ('test', 'pbkdf2:sha256:150000$TDBMd9qn$2920722cb08761ff369ce44e1ed44899ac455b0b9fd4b65ccbe4b4a8a775ac83', datetime());
insert into users (username, password, created_at) values ('test2', 'pbkdf2:sha256:150000$TDBMd9qn$2920722cb08761ff369ce44e1ed44899ac455b0b9fd4b65ccbe4b4a8a775ac83', datetime());


-- notes
insert into notes (title, body, author_id, created_at) values ('test', 'test.', 1, datetime());
insert into notes (title, body, author_id, created_at) values ('test 2', 'test with tag.', 1, datetime());

-- tags
insert into tags (name, user_id, created_at) values ('tag 1', 1, datetime());
insert into tags (name, user_id, created_at) values ('tag 2', 1, datetime());

-- note tag relation
insert into relation_notes_tags (note_id, tag_id, created_at) values (2, 1, datetime());
