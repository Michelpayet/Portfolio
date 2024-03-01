import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import datetime


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    transactions_db = db.execute(
        "SELECT symbol, SUM(shares) as shares, price FROM portfolio WHERE users_id = ? GROUP BY symbol", user_id)
    cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_db[0]["cash"]

    total_result = db.execute("SELECT SUM(shares * price) AS total FROM portfolio WHERE users_id = ?", user_id)
    total = total_result[0]["total"] if total_result[0]["total"] else 0

    # Add cash balance to the total
    total += cash

    # Format total to 2 decimal places
    formatted_total = "{:.2f}".format(total)

    return render_template("index.html", database=transactions_db, cash=cash, total=formatted_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("Please Enter Symbol")

        stock = lookup(symbol.upper())

        if stock == None:
            return apology("Unavailable")

        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("Not Allowed")

        shares = int(shares)  # Convert shares to integer

        transaction_value = shares * stock["price"]

        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        if user_cash < transaction_value:
            return apology("Not Enough Money")

        uptd_cash = user_cash - transaction_value

        db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)

        # Update history
        date = datetime.datetime.now()
        db.execute("INSERT INTO portfolio (users_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)",
                   user_id, stock["symbol"], shares, stock["price"], date)

        flash("Transaction Successful!")

        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transaction_history = db.execute("SELECT * FROM portfolio WHERE users_id = ? ORDER BY date DESC", user_id)
    return render_template("history.html", database=transaction_history)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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
        symbol = request.form.get("symbol")
        quote = lookup(symbol.upper())
        if not quote:
            return apology("Please enter a symbol eg: AAPL", 400)
        return render_template("quote.html", quote=quote)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # forget user id
    session.clear()

    if request.method == "POST":

        # Add the user's entry into the database
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if fields are not empty
        if not username or not password or not confirmation:
            return apology("Please fill in all the fields")

        # Check if password matches the confirmation
        if password != confirmation:
            return apology("Password does not match")

        hashed = generate_password_hash(password)

        # The username field is already UNIQUE so we can do this:
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashed)
        except:
            return apology("Username already exist. Please choose a different one")

        # remember logged in user
        session["user_id"] = new_user

        # redirect to homepage
        return redirect("/")

    # If user reached via GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        user_id = session["user_id"]
        users_stocks = db.execute("SELECT symbol FROM portfolio WHERE users_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
        return render_template("sell.html", symbols=[row["symbol"] for row in users_stocks])
    else:
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if not symbol:
            return apology("Please Enter Symbol")

        stock = lookup(symbol.upper())

        if stock == None:
            return apology("Stock does not exist")

        if shares <= 0:
            return apology("Insuficient shares to sell")

        user_id = session["user_id"]
        balance = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = balance[0]["cash"]

        user_shares = db.execute("SELECT shares FROM portfolio WHERE users_id = ? AND symbol = ? GROUP BY symbol",
                                 user_id, symbol)
        if not user_shares:
            return apology("Not avaiable")

        shares_real = user_shares[0]["shares"]

        if shares > shares_real:
            return apology("Insuficient shares")

        transaction = shares * stock["price"]
        new_balance = user_cash + transaction

        # Update database and history
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)
        date = datetime.datetime.now()
        db.execute("INSERT INTO portfolio (users_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)",
                   user_id, stock["symbol"], (-1)*shares, stock["price"], date)

        flash("Transaction Successful!")

    return redirect("/")

