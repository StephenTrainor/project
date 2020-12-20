import random
import pandas as pd
from cs50 import SQL
from tempfile import mkdtemp
from calendar import weekday
from datetime import datetime
from flask_session import Session
import plotly.graph_objects as go
import pandas_datareader.data as web
from helpers import apology, login_required, percent
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///data.db")


@app.route("/")
@login_required
def index():
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    user_data = db.execute("SELECT * FROM 'users' WHERE (id = :user_id)", user_id=session["user_id"])
    timestamp = datetime.now()
    y, m, d, h, mi = timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute
    amp = 'AM'
    current_day = weekday(y, m, d)

    if h > 12:
        h -= 12
        amp = 'PM'

    return render_template("index.html", username=user_data[0]['username'], day=days[current_day], hour=h,
                           minute=mi, amp=amp)


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    if "clear_todo" in request.form:
        db.execute("DELETE FROM 'todo' WHERE (id = :user_id)", user_id=session["user_id"])
        db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)",
                   user_id=session["user_id"],
                   typee="Deleted History", message="")

        return render_template("success.html", type_success="cleared to-do list",
                               message="Your to-do list was cleared and you can proceed to add more items to the list.",
                               path="Go Back")

    elif "clear_item_todo" in request.form:
        todo_data = db.execute("SELECT * FROM 'todo' WHERE (id = :user_id)", user_id=session["user_id"])

        for m in range(len(todo_data)):
            if todo_data[m]['todo'].lower() == request.form.get("list_item").lower():
                db.execute("DELETE FROM 'todo' WHERE (id = :user_id AND todo = :user_message)",
                           user_id=session["user_id"],
                           user_message=todo_data[m]['todo'])
                db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)",
                           user_id=session["user_id"], typee="Deleted To-Do Item", message=todo_data[m]['todo'])
                return render_template("success.html", type_success="cleared item",
                                       message="An Item was successfully removed from your To-Do list.", path="Go Back")

        return apology("Unable to delete specified item from to-do list, try again.", 403)

    elif "clear_item_manager" in request.form:
        user_data = db.execute("SELECT * FROM 'manager' WHERE (id = :user_id)", user_id=session["user_id"])

        for m in range(len(user_data)):
            if user_data[m]['service'].lower() == request.form.get("list_item").lower():
                db.execute("DELETE FROM 'manager' WHERE (id = :user_id AND service = :site)",
                           user_id=session["user_id"], site=user_data[m]['service'])
                db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)",
                           user_id=session["user_id"], typee="Deleted Password", message="")
                return render_template("success.html", type_success="cleared item",
                                       message="An Item was successfully removed from your To-Do list.", path="Go Back")

        return apology("Unable to delete specified service/site, try again.", 403)

    elif "clear_history" in request.form:
        db.execute("DELETE FROM 'history' WHERE (id = :user_id)", user_id=session["user_id"])

        return render_template("success.html", type_success="cleared history",
                               message="All previous history is now gone.", path="Go Back")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    history = db.execute("SELECT * FROM 'history' WHERE (id = :user_id)", user_id=session["user_id"])

    if not history:
        return render_template("history.html")
    return render_template("history.html", rows=history, exists=True)


@app.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    user_data = db.execute("SELECT * FROM 'users' WHERE (id = :user_id)", user_id=session["user_id"])
    todo_data = db.execute("SELECT * FROM 'todo' WHERE (id = :user_id)", user_id=session["user_id"])

    if request.method == "POST":
        if not request.form.get("message"):
            return apology("Must enter something to do in the input field")

        db.execute("INSERT INTO 'todo' (id, todo) VALUES (:user_id, :message)",
                   user_id=session["user_id"], message=request.form.get("message"))
        db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)",
                   user_id=session["user_id"],
                   typee="Added Item On ToDo List", message=request.form.get("message"))

        return render_template("success.html", type_success="added item on to-do list",
                               message="The specified to-do item was successfully added on the to-do list and can be seen now.",
                               path="Go Back")

    else:
        if not todo_data:
            return render_template("todo.html", username=user_data[0]['username'], rows=todo_data)
        return render_template("todo.html", username=user_data[0]['username'], rows=todo_data, exists=True)


@app.route("/stock", methods=["GET", "POST"])
@login_required
def stock():
    now = datetime.now()

    if request.method == "POST":
        global symbol
        symbol = request.form.get("ticker").upper()
        months = request.form.get("months")

        if not symbol:
            return apology("Must provide a ticker symbol", 403)

        elif not months:
            return apology("Must provide the number of months worth of data to collect", 403)

        month = now.month - int(months)
        year = now.year

        while not month >= 1:
            month += 12
            year -= 1

        start = datetime(year, month, now.day)
        end = datetime(now.year, now.month, now.day)

        try:
            data = web.DataReader(symbol, 'yahoo', start, end)
            data.to_csv('stock.csv')
            data = pd.read_csv('stock.csv')

        except (IOError, KeyError):
            return apology("Invalid Ticker Symbol, try again", 403)

        cols = ['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close']
        month_percent = {}
        week_percent = {}
        prev_percent = {}
        all_time = {}
        monthly = {}
        weekly = {}
        prev = {}
        current = data.tail(1)
        date_data = current['Date']

        for i in range(len(data)):
            for j in range(len(cols)):
                if i == 0:
                    all_time[cols[j]] = data[cols[j]][i]

                else:
                    all_time[cols[j]] += data[cols[j]][i]

        for m in range(len(cols)):
            all_time[cols[m]] /= len(data)

            prev_percent[cols[m]] = percent(data[cols[m]][len(data) - 2], data[cols[m]][len(data) - 1])
            prev[cols[m]] = data[cols[m]][len(data) - 1] - data[cols[m]][len(data) - 2]

            for n in range(len(data) - 4, len(data)):
                if n == len(data) - 4:
                    weekly[cols[m]] = data[cols[m]][n]

                else:
                    weekly[cols[m]] += data[cols[m]][n]

            for o in range(len(data) - 19, len(data)):
                if o == len(data) - 19:
                    monthly[cols[m]] = data[cols[m]][o]

                else:
                    monthly[cols[m]] += data[cols[m]][o]

            weekly[cols[m]] /= 5
            monthly[cols[m]] /= 20

        return render_template("summary.html", ticker_symbol=symbol)

    else:
        return render_template("stock.html")


@app.route("/candle", methods=["POST"])
@login_required
def candle():
    """
    The dataframe and candlestick figure code was from a tutorial

    https://www.youtube.com/watch?v=4fhBXFSS1lc

    Rest of the code was modified, removed, or added to.
    """
    df = pd.read_csv('stock.csv')

    df = df.set_index(pd.DatetimeIndex(df['Date'].values))
    figure = go.Figure(data=[
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            hovertext=df['Volume'],
            close=df['Close'])
    ])
    figure.update_layout(title=f'{symbol} stock analysis',
                         yaxis_title=f'{symbol} stock price (USD)',
                         xaxis_title=f'Volume of {symbol} with dates corresponding with dates above')

    figure.show()

    return render_template("success.html",
                           type_success="loaded graph",
                           message="The graph was successfully loaded in another tab.",
                           path="Back")


@app.route("/gen", methods=["GET", "POST"])
@login_required
def generator():
    if request.method == "POST":
        chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7',
                 '8', '9']
        dupes = []
        password = []

        if not request.form.get("length"):
            return apology("Must specify length of password", 403)

        for s in request.form.get("symbols"):
            chars.append(s)

        for li in range(len(chars)):
            if chars[li] not in dupes:
                dupes.append(chars[li])

            elif chars[li] in dupes:
                chars[li] = ""

        for c in range(int(request.form.get("length"))):
            password.append(chars[random.randint(0, len(chars) - 1)])

        new_pass = "".join(password)
        db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)",
                   user_id=session["user_id"], typee="Generated Password", message="")

        return render_template("pass.html", type_success="generated password", path="Exit",
                               password=new_pass)

    else:
        return render_template("generator.html")


@app.route("/checker", methods=["GET", "POST"])
@login_required
def checker():
    return render_template("checker.html")


@app.route("/manager", methods=["GET", "POST"])
@login_required
def manager():
    user_data = db.execute("SELECT * FROM 'users' WHERE (id = :user_id)", user_id=session["user_id"])
    content = db.execute("SELECT * FROM 'manager' WHERE (id = :user_id)", user_id=session["user_id"])

    if request.method == "POST":
        if not request.form.get("service"):
            return apology("Must specify service or site", 403)

        elif not request.form.get("username"):
            return apology("Must specify a username", 403)

        elif not request.form.get("password"):
            return apology("Must specify a password", 403)

        db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)",
                   user_id=session["user_id"],
                   typee="Additional Item for Password Manager", message="")
        db.execute(
            "INSERT INTO 'manager' (id, service, username, password) VALUES (:user_id, :site, :username, :password)",
            user_id=session["user_id"], site=request.form.get("service"), username=request.form.get("username"),
            password=request.form.get("password"))

        return render_template("success.html", type_success="added password",
                               message=f"Password for {request.form.get('service')} was successfully added to the Password Manager",
                               path="Go Back")

    else:
        if not content:
            return render_template("manager.html", username=user_data[0]['username'], rows=content)
        return render_template("manager.html", username=user_data[0]['username'], rows=content, exists=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                 'u', 'v', 'w', 'x', 'y', 'z']

    if request.method == "POST":
        user_password = request.form.get("password")

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not user_password:
            return apology("must provide password", 403)

        elif user_password != request.form.get("confirm-password"):
            return apology("Password and Confirmed Password did not match", 403)

        for c in user_password:
            if c == " ":
                return apology("Password cannot have spaces in them.", 403)

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        if len(rows) > 0:
            return apology("Username already taken", 403)

        letters, numbers, symbols = 0, 0, 0
        for char in user_password:
            if char.isnumeric():
                numbers += 1

            elif char.isalpha():
                letters += 1

            elif char.lower() not in lowercase and not char.isnumeric():
                symbols += 1

        if letters >= 8 and numbers >= 2 and symbols >= 1:
            pass

        else:
            return apology("Password Must Have At Least 8 letters, 2 numbers and 1 symbol for extra security.", 403)

        db.execute("INSERT INTO users (username, hash) VALUES (:user, :hash_value)",
                   user=request.form.get("username"), hash_value=generate_password_hash(user_password))

        return render_template("success.html", type_success="registered",
                               message="You can now login to the website with your newly created account!",
                               path="Go Back")

    else:
        return render_template("register.html")


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
