import os

from flask import Flask


test_flask = Flask(__name__)
db_name = os.environ.get('DB_PATH', 'db')
project_directory = os.getcwd()
db_path = f'{project_directory}/{db_name}.db'
test_flask.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/signals/
test_flask.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# To see the queries that are being run
test_flask.config['SQLALCHEMY_ECHO'] = False

def reset_db():
    try:
        os.remove(db_path)
        print("=============Removed db successfully")
    except Exception as e:
        print("=============Removed db failed: " + str(e))
