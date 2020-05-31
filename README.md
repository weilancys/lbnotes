## lbnotes
---

- lbnotes is a lightweight web app for quick note taking in the markdown format with tags support.
- lbnotes is based on flask and sqlite3.
- lbnotes is licenced under GNU GPLv3.

---

### install:
```
pip install lbnotes
```

### database initialization:
```
# database initialization needs to be done before usage.
export FLASK_APP=lbnotes
flask init-db 
```

### config:
```
main config file "config.py" should be put in the instance folder.
details can be found in "config.py.example" file.
```

### run:
```
flask run
```

### deploy:
```
lbnotes is os independent.
lbnotes can be deployed with any webserver that flask supports.
choose your webserver of choice and see its details for deployment.
[deploy references](https://flask.palletsprojects.com/en/1.1.x/deploying/)
```