const note_bodies = document.querySelectorAll(".note-body");
for (const note_body of note_bodies) {
    note_body.innerHTML = marked(note_body.innerHTML);
}
