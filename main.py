from flask import Flask, render_template, redirect, url_for, g, current_app
from pathlib import Path
import sqlite3

app = Flask(__name__)
fichier_db = Path("database.db")
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    if not fichier_db.exists():
        with app.app_context():
            connection = get_db()
            with app.open_resource('script.sql', mode='r') as sql_file:
                instructions = sql_file.read()
                connection.cursor().executescript(instructions)
            connection.commit()

@app.route("/")
def index():
    init_db()
    cur = get_db().cursor()
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    return render_template("login.html")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()