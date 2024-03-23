import importlib

from flask import Flask, render_template, redirect, url_for, g, current_app, request, jsonify
from datetime import timedelta
from datetime import datetime
from pathlib import Path
import sqlite3
import hashlib

app = Flask(__name__)

INSERT_VACATION_REQUEST = "INSERT INTO VacationRequest (id_employee, id_vacation_type, start_date, end_date, number_days, status) VALUES(?, ?, ?, ?, ?, ?)"
GET_ID_EMPLOYEE = "SELECT Employee.id_employee FROM User INNER JOIN Employee ON User.id_user = Employee.id_user WHERE User.id_user = ?"
GET_LOGIN_USER = "SELECT User.login FROM Employee JOIN User ON Employee.id_user = User.id_user WHERE Employee.id_employee = ?;"
GET_ID_EMPLOYEE_FROM_VACATION_REQUEST = "SELECT id_employee FROM VacationRequest WHERE id_vacation_request = ?"
GET_NUMBER_DAYS_FROM_VACATION_REQUEST = "SELECT number_days FROM VacationRequest WHERE id_vacation_request = ?"
GET_VACATION_TYPE = "SELECT wording FROM VacationType WHERE id_vacation_type = ?"
GET_VACATION_DATA = "SELECT * FROM VacationLeaveBalance WHERE id_employee = ?"
GET_VACATION = "SELECT * FROM VacationRequest WHERE id_employee = ?"
GET_USER = "SELECT * FROM User WHERE login = ?"
BAD_PASS_MESSAGE = "Mauvais mot de passe"
STATUS = "en attente"

fichier_db = Path("datasbase.db")
DATABASE = 'datasbase.db'

# Start region definition -------------------------------------------------------------------------------------
def get_db():
    """
    Retrieves a connection to the SQLite database.
    This function first checks if there's already a database connection in the global object g.
    If a connection exists, it is returned.
    Otherwise, a new connection to the database is established using the path specified by the DATABASE variable.
    The new connection is then stored in the global object g for later use and returned.
    :return:
        sqlite3.Connection: The connection to the SQLite database.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    """
    Initializes the database by executing SQL script if the database file doesn't exist.
    If the database file doesn't exist, this function creates a connection to the database
    and executes the SQL script defined in 'script.sql' to create the necessary tables.
    It then commits the changes to the database.
    """
    if not fichier_db.exists():
        with app.app_context():
            connection = get_db()
            with app.open_resource('script.sql', mode='r') as sql_file:
                instructions = sql_file.read()
                connection.cursor().executescript(instructions)
            connection.commit()

def hash_password(password):
    """
    Hashes the given password using the SHA-256 algorithm.
    :param password: password (str): The password to be hashed.
    :return:
        str: The hashed password in hexadecimal format.
    """
    hasher = hashlib.sha256()
    hasher.update(password.encode())
    return hasher.hexdigest()

def calculate_number_days(start_date, end_date):
    """
    Calculates the number of days between the start and end dates, inclusive.
    :param start_date: The start date in the format 'YYYY-MM-DD'.
    :param end_date: The end date in the format 'YYYY-MM-DD'.
    :return:
        int: The number of days between the start and end dates, inclusive.
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    nombre_jours = (end_date - start_date).days + 1
    return nombre_jours

def get_id_employee(user):
    """
    Retrieves the employee ID associated with the given user.
    :param user: A tuple containing user information.
    :return:
        tuple: A tuple containing the employee ID associated with the user.
    """
    cur = get_db().cursor()
    return cur.execute(GET_ID_EMPLOYEE, [user[0]]).fetchone()

def load_data_vacation(user):
    cur = get_db().cursor()
    id_employee = get_id_employee(user)
    return cur.execute(GET_VACATION, [id_employee[0]]).fetchall()

def check_remaining_days(vacation_type, nombre_jours, remaining_holidays, remaining_working_time_reduction):
    """
    Checks if the requested number of days for a vacation type can be accommodated based on remaining days.
    :param vacation_type:
    :param nombre_jours:
    :param remaining_holidays:
    :param remaining_working_time_reduction:
    :return:
        bool: True if the requested number of days can be accommodated, False otherwise.
    """
    limit = remaining_holidays if vacation_type == "1" else remaining_working_time_reduction
    return nombre_jours <= limit

# End region definition ---------------------------------------------------------------------------------------

# Start region routes -----------------------------------------------------------------------------------------
@app.route("/")
def index():
    init_db()
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/infos", methods=["POST"])
def login_verify():
    cur = get_db().cursor()
    username = request.form.get("username")
    password = request.form.get("password")

    user = cur.execute(GET_USER, [username]).fetchone()
    vacation_request_list = load_data_vacation(user)

    if not user or not user[2] == hash_password(password):
        return render_template("login.html", text=BAD_PASS_MESSAGE)
    else:
        if (user[3] == 1):
            vacation_request_list = cur.execute("SELECT * FROM VacationRequest").fetchall()
            rows_html = ""
            for vacation_request in vacation_request_list:
                imployee_id = get_id_employee(user)
                number_days = calculate_number_days(vacation_request[3], vacation_request[4])
                vacation_type = cur.execute(GET_VACATION_TYPE, [vacation_request[2]]).fetchone()[0]
                dates = vacation_request[3] + " - " + vacation_request[4]
                status = vacation_request[6]
                request_id = vacation_request[0]
                user_name = cur.execute(GET_LOGIN_USER, (vacation_request[1],)).fetchone()[0]

                if status == 'en attente':
                    action_buttons = f"""
                                    <button onclick="acceptRequest({request_id}, '{username}', '{password}', '{imployee_id}')">Accepter</button>
                                    <button onclick="rejectRequest({request_id}, '{username}', '{password}')">Refuser</button>
                                    """
                else:
                    action_buttons = ""
                row_html = f"""<tr>
                                  <td>{user_name}</td>
                                  <td>{vacation_type}</td>
                                  <td>{dates}</td>
                                  <td>{number_days}</td>
                                  <td>{status}</td>
                                  <td>{action_buttons}</td>
                                </tr>"""
                rows_html += row_html
            return render_template("accueilhr.html", rows=rows_html)

        rows_html = ""
        for vacation_request in vacation_request_list:
            number_days = calculate_number_days(vacation_request[3], vacation_request[4])
            vacation_type = cur.execute(GET_VACATION_TYPE, [vacation_request[2]]).fetchone()[0]
            dates = vacation_request[3] + " - " + vacation_request[4]
            status = vacation_request[6]

            row_html = f"""<tr>
                              <td>{vacation_type}</td>
                              <td>{dates}</td>
                              <td>{number_days}</td>
                              <td>{status}</td>
                            </tr>"""
            rows_html += row_html
        holiday_data = cur.execute(GET_VACATION_DATA, get_id_employee(user)).fetchone()

        return render_template(
            'accueil.html',
            rows=rows_html, prenom=user[1],
            username=username,
            password=password,
            id=user[0],
            a_cp=holiday_data[4],
            a_rtt=holiday_data[5],
            p_cp=holiday_data[2],
            p_rtt=holiday_data[3],
            r_cp=holiday_data[4] - holiday_data[2],
            r_rtt=holiday_data[5] - holiday_data[3]
        )

@app.route('/approve-request', methods=['POST'])
def approve_request():
    conn = get_db()
    cursor = conn.cursor()
    request_id = request.form['id']
    username = request.form['username']
    password = request.form['password']
    imployee_id = cursor.execute(GET_ID_EMPLOYEE_FROM_VACATION_REQUEST, (request_id,)).fetchone()
    days_nb = cursor.execute(GET_NUMBER_DAYS_FROM_VACATION_REQUEST, (request_id,)).fetchone()

    cursor.execute("UPDATE VacationRequest SET status = 'approuvee' WHERE id_vacation_request = ?", (request_id,))
    cursor.execute("UPDATE VacationLeaveBalance SET day_used_payed = day_used_payed + ? WHERE id_employee = ?",(days_nb[0], imployee_id[0]))
    conn.commit()
    return render_template('redirect.html', username=username, password=password)

@app.route('/reject-request', methods=['POST'])
def reject_request():
    conn = get_db()
    cursor = conn.cursor()
    request_id = request.form['id']
    username = request.form['username']
    password = request.form['password']
    cursor.execute("UPDATE VacationRequest SET status = 'rejetee' WHERE id_vacation_request = ?", (request_id,))
    conn.commit()
    return render_template('redirect.html', username=username, password=password)

@app.route("/demande", methods=["POST"])
def demande():
    id = request.form.get('id')
    username = request.form.get('username')
    password = request.form.get('password')

    return render_template('demande.html',
                           id=id,
                           username=username,
                           password=password,
                           min_date=datetime.now().date() + timedelta(days=1)
                           )

@app.route("/calcul", methods=["POST"])
def calcul():
    cur = get_db()
    if request.method == "POST":
      id_user = request.form["id_user"]
      username = request.form["username"]
      password = request.form["password"]
      employee_id = get_id_employee(id_user)
      vacation_type = request.form["type"]

      start_date = datetime.strptime(request.form["date_debut"], "%Y-%m-%d")
      end_date = datetime.strptime(request.form["date_fin"], "%Y-%m-%d")

      nombre_jours = (end_date - start_date).days + 1

      holiday_data = cur.execute(GET_VACATION_DATA, get_id_employee(id_user)).fetchone()

      remaining_holidays = holiday_data[4] - holiday_data[2]
      remaining_working_time_reduction = holiday_data[5] - holiday_data[3]

      conges_valides = check_remaining_days(vacation_type, nombre_jours, remaining_holidays, remaining_working_time_reduction)
      if not conges_valides:
        return render_template('demande.html', message="Le nombre de congés demandés est supérieur à votre solde", id=id_user)
      else:
          cur.execute(INSERT_VACATION_REQUEST, (employee_id[0], vacation_type, start_date.date(), end_date.date(), nombre_jours, STATUS))
          cur.commit()
          return render_template('redirect.html', username=username, password=password)

# End region routes ---------------------------------------------------------------------------------------
