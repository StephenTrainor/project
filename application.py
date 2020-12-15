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
    # TODO
    
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # TODO
    
    if request.method == "POST":
        return apology("TODO")
            
    else:
        return apology("TODO")


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    
    if request.method == "POST":
        ti = request.form.get("ticker")
        data = lookup(ti)
        if not ti:
            return apology("Must enter a ticker symbol", 403)
            
        elif not ti:
            return apology("Must enter a valid ticker symbol", 403)
        
        elif not data:
            return apology("Must enter a valid ticker symbol", 403)
        
        return render_template("success.html", type_success=f"Quoted {data['symbol']}", 
                          message=f"One share of {data['symbol']} ({data['name']}) costs ${data['price']}", path="Go Back")
    
    else:
        return render_template("quote.html")
    
    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        
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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    
    if request.method == "POST":
        try:
            num_shares = int(request.form.get("shares"))
            ticker_symbol = request.form.get("ticker").upper()
            
            if num_shares < 1 or not num_shares:
                raise ValueError
        
        except ValueError:
            return apology("You cannot sell zero or negative shares of stock.", 403)
            
        current_cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        current_shares = db.execute("SELECT * FROM stocks WHERE id = :user_id AND ticker = :ticker_symbol",
                          user_id=session["user_id"], ticker_symbol=ticker_symbol)
        
        if not ticker_symbol:
            return apology("You must specifiy a ticker symbol to sell", 403)
        
        elif not current_shares:
            return apology("You cannot sell a stock you do not own", 403)
            
        elif current_shares[0]['shares'] < num_shares:
            return apology("You cannot sell more shares than you own", 403)
            
        available_shares = current_shares[0]['shares']
        new_shares = available_shares - num_shares
        new_cash = current_cash[0]['cash'] + (num_shares * current_shares[0]['price'])
        
        db.execute("UPDATE users SET cash=:new_cash WHERE id = :user_id", new_cash=new_cash, user_id=session["user_id"])
        db.execute("UPDATE stocks SET shares=:new_shares WHERE id=:user_id AND ticker=:symbol", new_shares=new_shares, user_id=session["user_id"], symbol=ticker_symbol)
        db.execute("INSERT INTO history (id, ticker, shares, transfer) VALUES (:user_id, :ticker_symbol, :num_shares, :total_cost)", 
                          user_id=session["user_id"], ticker_symbol=ticker_symbol, num_shares=(-1 * num_shares), total_cost=num_shares * current_shares[0]['price'])
        
        return render_template("success.html", type_success=f"Sold {num_shares} shares of {ticker_symbol}", 
                          message=f"{num_shares} shares of {ticker_symbol} were sold for a total of {usd(num_shares * current_shares[0]['price'])}", path="Back To Main Page")
            
    else:
        return render_template("sell.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
