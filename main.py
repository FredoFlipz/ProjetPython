from flask import Flask, render_template, redirect, url_for, g, current_app, request
from pathlib import Path
import sqlite3
import hashlib

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
def hash_password(password):
  hasher = hashlib.sha256()
  hasher.update(password.encode())
  return hasher.hexdigest()

@app.route("/")
def index():
    init_db()
    text = hash_password("azerty")
    return render_template("index.html", text=text)

@app.route("/login", methods=["POST"])
def login():
    return render_template("login.html")

@app.route("/login-verify", methods=["POST"])
def login_verify():
    message = ""
    cur = get_db().cursor()
    username = request.form.get("username")
    password = request.form.get("password")
    text = cur.execute("SELECT hashed_password FROM User WHERE login = ?",[username]).fetchone()#[0]
    if not text or not text[0] == hash_password(password):
        message = "Mauvais mot de passe"
    #else:
        #text = "Accès autorisé"
    return render_template("login.html", text=message)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()