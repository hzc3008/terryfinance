import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    # Get user's information
    userstocks = db.execute("""
        SELECT u.id, t.symbol, SUM(t.shares) AS sumshares
        FROM users AS u JOIN transactions As t ON u.id = t.id
        WHERE u.id = ?
        GROUP BY u.id, t.symbol
        HAVING SUM(t.shares) <> 0;
    """, session["user_id"])

    stockvalue = 0
    # Loop in every stocks in the user's stock list
    for stock in userstocks:
        # Get individual symbol and check the current price
        Quotepricedictionary = lookup(stock["symbol"])
        currentprice = Quotepricedictionary["price"]
        # Write the current price into the stock dictionary as key "price" = value "currentprice"
        stock["price"] = currentprice
        # Calculate sum of price for stock and write back to key "totalvalue" = value "value"
        value = currentprice * stock["sumshares"]
        stock["totalvalue"] = value
        stockvalue += value  # Update stockvalue with the current stock value

    usercashlist = db.execute(" SELECT cash FROM users WHERE id = ?;", session["user_id"])
    usercash = usercashlist[0]["cash"]
    grandtotal = stockvalue + usercash
    return render_template("/index.html", userstocks=userstocks, stockvalue=stockvalue, usercash=usercash, grandtotal=grandtotal)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("must provide symbol to buy", 400)

        # Convert shares to an integer
        try:
            shares = int(shares)
        except ValueError:
            return apology("Invalid number of shares", 400)

        # Test if the shares is positive
        if shares < 1:
            return apology("Share to buy has to be positive", 400)

        # Lookup for Price of the symbol
        price = lookup(symbol)

        # Test if the symbol is valid
        if not price:
            return apology("Invalid Symbol", 400)

        moneyspend = price["price"] * shares

        # Chek if this guy has sufficient money
        userinfo = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        usercash = float(userinfo[0]["cash"])
        # Ensure username exists and password is correct
        if usercash < moneyspend:
            return apology("Insufficient Fund", 400)

        # Insert into transactions table
        db.execute("INSERT INTO transactions(id, symbol, shares, price) VALUES (?, ?, ?, ?);", session["user_id"], symbol, shares, price["price"])

        # Update users table
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?;", moneyspend, session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        cashavailable = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        return render_template("/buy.html",cash=cashavailable[0]["cash"])


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    historytransactions = db.execute("""
    SELECT
        CASE WHEN shares < 0
        THEN 'Short'
        ELSE 'Long'
        END AS position,
        symbol,
        shares,
        price,
        shares * price AS totalvalue,
        timestamp
    FROM
        transactions
    WHERE
        id = ?
    ORDER BY
        timestamp
    """, session["user_id"])

    return render_template("/history.html", historytransactions=historytransactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

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
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol to quote", 400)
        # Lookup for Price of the symbol
        price = lookup(symbol)

        # Test if the symbol is valid
        if not price:
            return apology("Invalid Symbol", 400)

        # Redirect user to home page
        return render_template("/quoted.html", symbol=symbol, price=price)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("/quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
        # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure username was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirm", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username not exists
        if len(rows) != 0:
            return apology("Username Exsists", 400)
        # Ensure password and password confirm are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("invalid Password or Password Confirm", 400)

        # Store the Username and Hashed Password into the database
        db.execute("INSERT INTO users(username, hash) VALUES (?, ?);", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("must provide symbol to sell", 400)

        # Convert shares to an integer
        try:
            shares = int(shares)
        except ValueError:
            return apology("Invalid number of shares", 400)

        # Test if the shares is positive
        if shares < 1:
            return apology("Share to sell has to be positive", 400)

        # Lookup for Price of the symbol
        price = lookup(symbol)

        # Test if the shares is positive
        if not price:
            return apology("Invalid Symbol", 400)

        moneyearned = price["price"] * shares

        # Chek if this guy has sufficient shares
        userinfo = db.execute("SELECT SUM(shares) AS totalshares FROM transactions WHERE id = ? AND symbol = ? GROUP BY id, symbol", session["user_id"], symbol)
        usershares = float(userinfo[0]["totalshares"])
        # Ensure username exists and password is correct
        if usershares < shares:
            return apology("Insufficient Shares", 400)

        # Insert into transactions table
        db.execute("INSERT INTO transactions(id, symbol, shares, price) VALUES (?, ?, -?, ?);", session["user_id"], symbol, shares, price["price"])

        # Update users table
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?;", moneyearned, session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        userstocks = db.execute("""
        SELECT u.id, t.symbol, SUM(t.shares) AS sumshares
        FROM users AS u JOIN transactions As t ON u.id = t.id
        WHERE u.id = ?
        GROUP BY u.id, t.symbol
        HAVING SUM(t.shares) <> 0;
        """, session["user_id"])

        stockvalue = 0
        # Loop in every stocks in the user's stock list
        for stock in userstocks:
            # Get individual symbol and check the current price
            Quotepricedictionary = lookup(stock["symbol"])
            currentprice = Quotepricedictionary["price"]
            # Write the current price into the stock dictionary as key "price" = value "currentprice"
            stock["price"] = currentprice
            # Calculate sum of price for stock and write back to key "totalvalue" = value "value"
            value = currentprice * stock["sumshares"]
            stock["totalvalue"] = value
            stockvalue += value  # Update stockvalue with the current stock value

        return render_template("/sell.html", userstocks=userstocks)
