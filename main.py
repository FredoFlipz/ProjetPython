from flask import Flask, render_template, redirect, url_for, g, current_app, request
from datetime import datetime
from pathlib import Path
import sqlite3
import hashlib

app = Flask(__name__)

REQUEST_ID_EMPLOYEE = "SELECT Employee.id_employee FROM User INNER JOIN Employee ON User.id_user = Employee.id_user WHERE User.id_user = ?"
REQUEST_VACATION = "SELECT * FROM VacationRequest WHERE id_employee = ?"
REQUEST_USER = "SELECT * FROM User WHERE login = ?"
REQUEST_VACATION_TYPE = "SELECT wording FROM VacationType WHERE id_vacation_type = ?"
REQUEST_VACATION_DATA = "SELECT * FROM VacationLeaveBalance WHERE id_employee = ?"
BAD_PASS_MESSAGE = "Mauvais mot de passe"

fichier_db = Path("datasbase.db")
DATABASE = 'datasbase.db'

# Start region definition -------------------------------------------------------------------------------------
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

def calculate_number_days(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    nombre_jours = (end_date - start_date).days + 1
    return nombre_jours

def get_id_employee(user):
    cur = get_db().cursor()
    return cur.execute(REQUEST_ID_EMPLOYEE, [user[0]]).fetchone()

def load_data_vacation(user):
    cur = get_db().cursor()
    #id_employee = cur.execute(REQUEST_ID_EMPLOYEE, [user[0]]).fetchone()
    id_employee = get_id_employee(user)
    return cur.execute(REQUEST_VACATION, [id_employee[0]]).fetchall()
# End region definition ---------------------------------------------------------------------------------------

# Start region routes -----------------------------------------------------------------------------------------
@app.route("/")
def index():
    init_db()
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login-verify", methods=["POST"])
def login_verify():
    cur = get_db().cursor()
    username = request.form.get("username")
    password = request.form.get("password")

    user = cur.execute(REQUEST_USER, [username]).fetchone()
    vacation_request_list = load_data_vacation(user)

    if not user or not user[2] == hash_password(password):
        return render_template("login.html", text=BAD_PASS_MESSAGE)
    else:
        rows_html = ""
        for vacation_request in vacation_request_list:

            number_days = calculate_number_days(vacation_request[3], vacation_request[4])
            vacation_type = cur.execute(REQUEST_VACATION_TYPE, [vacation_request[2]]).fetchone()[0]
            dates = vacation_request[3] + " - " + vacation_request[4]
            status = vacation_request[6]

            row_html = f"""<tr>
                          <td>{vacation_type}</td>
                          <td>{dates}</td>
                          <td>{number_days}</td>
                          <td>{status}</td>
                        </tr>"""
            rows_html += row_html

            datas_vacation = cur.execute(REQUEST_VACATION_DATA, get_id_employee(user)).fetchone()

        return render_template(
            'accueil.html',
            rows=rows_html, prenom=user[1],
            a_cp=datas_vacation[4],
            a_rtt=datas_vacation[5],
            p_cp=datas_vacation[2],
            p_rtt=datas_vacation[3],
            r_cp=datas_vacation[4] - datas_vacation[2],
            r_rtt=datas_vacation[5] - datas_vacation[3]
        )

# End region routes ---------------------------------------------------------------------------------------
