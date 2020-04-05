const tag_chooser = document.querySelector(".tag-chooser");
const btn_add_tag = document.querySelector("#btn-add-tag");
const tags_select = document.querySelector("#tags-select");
const a_open_tag_chooser = document.querySelector("#a-open-tag-chooser");
const tag_chooser_close = document.querySelector(".tag-chooser .tag-chooser-content .close");
const btn_create_and_add = document.querySelector("#btn-create-and-add");
const new_tag_input = document.querySelector(".tag-creater input");
const a_show_tag_creater = document.querySelector("#a-show-tag-creater");
const tag_icons_display = document.querySelectorAll(".tag-icons-display");


btn_add_tag.addEventListener("click", function(e) {
    const text = tags_select.options[tags_select.selectedIndex].text;
    const value = tags_select.options[tags_select.selectedIndex].value;

    // add tag display
    add_tag_display(text, value);

    // add hidden field
    add_tag_hidden_field(text, value);

    tag_chooser_close.click();
});


btn_create_and_add.addEventListener("click", function(e) {
    if (new_tag_input.value === "") {
        return;
    }

    // create a tag
    const xhr = new XMLHttpRequest();
    xhr.open("POST", document.location.origin + "/tags/create");
    xhr.responseType = "json";
    xhr.onload = function(e) {
        if (xhr.status === 400) {
            alert(xhr.response["reason"]);
            return;
        } else if (xhr.status === 200) {
            let success = xhr.response["success"];
            if (!success) {
                alert(xhr.response["reason"]);
                return;
            }

            // add the tag
            let new_tag = xhr.response["tag"];
            add_tag_display(new_tag.name, new_tag.id);
            add_tag_hidden_field(new_tag.name, new_tag.id);
            new_tag_input.value = "";
        }
        tag_chooser_close.click();
    }

    const form_data = new FormData();
    form_data.append("tag_name", new_tag_input.value);
    xhr.send(form_data);
});


a_show_tag_creater.addEventListener("click", function(e) {
    e.preventDefault();
    e.stopPropagation();
    document.querySelector(".tag-creater").style.display = "block";
    document.querySelector(".tag-picker").style.display = "none";
});


tag_chooser_close.addEventListener("click", function(e) {
    document.querySelector(".tag-creater").style.display = "none";
    document.querySelector(".tag-picker").style.display = "block";
    tag_chooser.style.display = "none";
});


a_open_tag_chooser.addEventListener("click", function(e) {
    e.preventDefault();
    e.stopPropagation();
    tag_chooser.style.display = "block";

    // clear existing tags in chooser
    tags_select.options.length = 0;
    // load tags-select options
    const xhr = new XMLHttpRequest();
    xhr.open("GET", document.location.origin + "/tags");
    xhr.responseType = "json";
    xhr.onload = function(e) {
        if (xhr.status === 200) {
            const tags = xhr.response["tags"];
            tags.forEach(tag => {
                const opt = document.createElement("option");
                opt.value = tag["id"];
                opt.text = tag["name"];
                tags_select.appendChild(opt);
            });
        }
        else {
            alert('Error fetching tags. Returned status of ' + xhr.status);
        }
    };
    xhr.send();
});


function check_tag_icon_already_displayed(text) {
    const existing_tags = document.querySelectorAll(".tag-icon-text");
    let already_displayed = false;
    for (let index = 0; index < existing_tags.length; index++) {
        if (existing_tags[index].textContent === text) {
            already_displayed = true;
            break;
        }
    }
    return already_displayed;
}


function check_tag_hidden_input_exists(value) {
    const existing_tags_hidden_fields = document.querySelectorAll(".tag-hidden-field");
    let already_in_form = false;
    for (let index = 0; index < existing_tags_hidden_fields.length; index++) {
        if (existing_tags_hidden_fields[index].value === value) {
            already_in_form = true;
            break;
        }
    }
    return already_in_form;
}


function add_tag_display(text, value) {
    if (!check_tag_icon_already_displayed(text)) {
        const tag = document.createElement("div");
        tag.classList.add("tag-icon");
        tag.dataset.id = value;

        const span_text = document.createElement("span");
        span_text.classList.add("tag-icon-text");
        span_text.innerText = text;
        tag.appendChild(span_text);

        const span_exit = document.createElement("span");
        span_exit.classList.add("tag-icon-close");
        span_exit.innerText = " ×";
        bind_tag_close_event(span_exit);
        tag.appendChild(span_exit);

        document.querySelector(".tag-icons-display").appendChild(tag);
    }
    
}


function bind_tag_close_event(span_exit) {
    span_exit.addEventListener("click", function(e) {
        const removed_node = e.target.parentNode.parentNode.removeChild(e.target.parentNode);
        remove_tag_hidden_field(removed_node.dataset.id);
    })
}


function remove_tag_display(text) {
    // this function is written but not used.
    const existing_tags = document.querySelectorAll(".tag-icons-display .tag-icon .tag-icon-text");
    for (let index = 0; index < existing_tags.length; index++) {
        if (existing_tags[index].textContent === text) {
            existing_tags[index].parentNode.parentNode.removeChild(existing_tags[index].parentNode);
            return true;
        }        
    }
    return false;
}


function add_tag_hidden_field(text, value) {
    if (!check_tag_hidden_input_exists(value)) {
        const tag_hidden_field = document.createElement("input");
        tag_hidden_field.type = "hidden";
        tag_hidden_field.name = "tags"
        tag_hidden_field.classList.add("tag-hidden-field");
        tag_hidden_field.value = value;
        tag_hidden_field.innerText = text;
        document.querySelector(".new-note-form").appendChild(tag_hidden_field);
    }
}


function remove_tag_hidden_field(value) {
    const hidden_fields = document.querySelectorAll(".tag-hidden-field"); 
    for (let i = 0; i < hidden_fields.length; i++) {
        if (hidden_fields[i].value === value) {
            hidden_fields[i].parentNode.removeChild(hidden_fields[i]);
            return true;
        }
    }
    return false;
}


document.addEventListener("click", function(e) {
    if (e.target == tag_chooser) {
        tag_chooser_close.click();
    }
})