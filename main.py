from flask import Flask, render_template
from markupsafe import escape

app = Flask(__name__)



@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"

@app.route("/")
def index():
    texte = "Ceci est un texte statique"
    return render_template("index.html", texte=texte)