import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required


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
    

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")


@app.route("/")
@login_required
def index():
    return apology("TODO")


@app.route("/todo", methods=["GET", "POST"])
@login_required
def buy():
    user_data = db.execute("SELECT * FROM 'users' WHERE (id = :user_id)", user_id=session["user_id"])
    todo_data = db.execute("SELECT * FROM 'todo' WHERE (id = :user_id)", user_id=session["user_id"])

    if request.method == "POST":
        if not request.form.get("message"):
            return apology("Must enter something to do in the input field")

        db.execute("INSERT INTO 'todo' (id, todo) VALUES (:user_id, :message)", 
                   user_id=session["user_id"], message=request.form.get("message"))
        db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)", user_id=session["user_id"],
                   typee="Added Item On ToDo", message=request.form.get("message"))

        return render_template("success.html", type_success="added item on to-do list",
                               message="The specified to-do item was successfully added on the to-do list and can be seen now.", 
                               path="Go Back")

    else:
        if not todo_data:
            return render_template("todo.html", username=user_data[0]['username'], rows=todo_data)
        return render_template("todo.html", username=user_data[0]['username'], rows=todo_data, exists=True)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if "clear_todo" in request.form:
        db.execute("DELETE FROM 'todo' WHERE (id = :user_id)", user_id=session["user_id"])
        db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)", user_id=session["user_id"],
                   typee="Deleted History", message="")
        
        return render_template("success.html", type_success="cleared to-do list", 
                               message="Your to-do list was cleared and you can proceed to add more items to the list.", path="Go Back")
    
    elif "clear_item_todo" in request.form:
        todo_data = db.execute("SELECT * FROM 'todo' WHERE (id = :user_id)", user_id=session["user_id"])
        
        for m in range(len(todo_data)):
            if todo_data[m]['todo'].lower() == request.form.get("list_item").lower():
                db.execute("DELETE FROM 'todo' WHERE (id = :user_id AND todo = :user_message)", user_id=session["user_id"], 
                           user_message=todo_data[m]['todo'])
                db.execute("INSERT INTO 'history' (id, type, message) VALUES (:user_id, :typee, :message)", user_id=session["user_id"],
                           typee="Deleted To-Do Item", message=todo_data[m]['todo'])
                break
        
        return render_template("success.html", type_success="cleared item", 
                               message="An Item was succesfully removed from your To-Do list.", path="Go Back")
                              
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
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                 'u', 'v', 'w', 'x', 'y', 'z']

    if request.method == "POST":
        user_password = request.form.get("password")

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not user_password:
            return apology("must provide password", 403)

        # Ensure password and confirmed password match before continue
        elif user_password != request.form.get("confirm-password"):
            return apology("Password and Confirmed Password did not match", 403)

        for c in user_password:
            if c == " ":
                return apology("Password cannot have spaces in them.", 403)

        # Query database for username
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

        return render_template("success.html", type_success="registered", message="You can now login to the website with your newly created account!", path="Go Back")

    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
