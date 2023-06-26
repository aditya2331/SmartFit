import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fitness.db")

# Initialize data
bodyparts = [bp['bodyPart'] for bp in db.execute("SELECT DISTINCT bodyPart FROM uniqueExercises")]
equipment = [e['equipment'] for e in db.execute("SELECT DISTINCT equipment FROM uniqueExercises")]


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
@login_required
def index():
    exerciselist1 = db.execute("SELECT * FROM uniqueExercises WHERE id IN (SELECT exercise_id FROM userFavorites WHERE user_id = ? AND favState='true')", session["user_id"])
    for exercise in exerciselist1:
        exercise['favorited'] = 'true'
        id = exercise['id']
        exercise['commentcount'] = db.execute("SELECT COUNT (review) FROM userRatings WHERE exercise_id = ? AND NOT review=''", id)[0]['COUNT (review)']

    exerciselist2 = db.execute("SELECT * FROM uniqueExercises WHERE id IN (SELECT exercise_id FROM userRatings WHERE user_id = ?)", session["user_id"])
    def Extra(exercise):
        id = exercise['id']
        favstate = db.execute("SELECT favState FROM userFavorites WHERE user_id = ? AND exercise_id = ?", session["user_id"], id)[0]['favState']
        exercise['favorited'] = favstate
        exercise['commentcount'] = db.execute("SELECT COUNT (review) FROM userRatings WHERE exercise_id = ? AND NOT review=''", id)[0]['COUNT (review)']
        return exercise
    exerciselist2 = list(filter(Extra, exerciselist2))
    return render_template("index.html", exerciselist1=exerciselist1, exerciselist2=exerciselist2)

@app.route("/searchpage", methods=["GET"])
@login_required
def searchpage():
    return render_template("search.html", bodyparts=bodyparts, equipment=equipment)

@app.route("/search", methods=["GET"])
@login_required
def search():
    allowedParts = []
    allowedEquipment = []
    searched = '%' + request.args.get('exercise') + '%'
    exercises = db.execute("SELECT * FROM uniqueExercises WHERE name LIKE ?", searched)
    for bodypart in bodyparts:
        if request.args.get(bodypart) == "true":
            allowedParts.append(bodypart)
    for machine in equipment:
        if request.args.get(machine) == "true":
            allowedEquipment.append(machine)
    def Filter(exercise):
        if len(allowedParts) == 0 and len(allowedEquipment) != 0:
            if exercise["equipment"] in allowedEquipment:
                return exercise
        elif len(allowedParts) != 0 and len(allowedEquipment) == 0:
            if exercise["bodyPart"] in allowedParts:
                return exercise
        elif len(allowedParts) == 0 and len(allowedEquipment) == 0:
            return exercise
        else:
            if exercise["bodyPart"] in allowedParts and exercise["equipment"] in allowedEquipment:
                return exercise
    filtered = filter(Filter, exercises)
    def Extra(exercise):
        id = exercise['id']
        favstate = db.execute("SELECT favState FROM userFavorites WHERE user_id = ? AND exercise_id = ?", session["user_id"], id)[0]['favState']
        exercise['favorited'] = favstate
        exercise['commentcount'] = db.execute("SELECT COUNT (review) FROM userRatings WHERE exercise_id = ? AND NOT review=''", id)[0]['COUNT (review)']
        return exercise
    filtered = list(filter(Extra, filtered))
    return render_template("exercises.html", exerciselist=filtered)

@app.route("/exerciselist", methods=["GET"])
@login_required
def exerciselist():
    def find():
        for value in request.args.values():
            if request.args.get(value):
                id = request.args.get(value)
                return id
    id = find()
    session['ex_id'] = id
    return redirect("/afterInteraction")

@app.route("/afterInteraction", methods=["GET"])
@login_required
def afterInteraction():
    favstate = db.execute("SELECT favState FROM userFavorites WHERE user_id = ? AND exercise_id = ?", session["user_id"], session["ex_id"])[0]['favState']
    rated = 'true'
    if db.execute("SELECT rating FROM userRatings WHERE user_id = ? AND exercise_id = ?", session["user_id"], session["ex_id"]) == []:
        rated = 'false'
    reviews = db.execute("SELECT username, rating, review FROM userRatings WHERE exercise_id = ?", session["ex_id"])
    params = db.execute("SELECT * FROM uniqueExercises WHERE id = ?", session["ex_id"])[0]
    return render_template("exercise.html", params=params, favstate=favstate, rated=rated, reviews=reviews, username = session['username'])


@app.route("/favorite", methods=["GET","POST"])
@login_required
def favorite():
    if request.method == "POST":
        favstate = db.execute("SELECT favState FROM userFavorites WHERE user_id = ? AND exercise_id = ?", session["user_id"], session["ex_id"])[0]['favState']
        def toggle(a):
            if a == 'true':
                a = 'false'
            else:
                a = 'true'
            return a
        favstate = toggle(favstate)
        db.execute("UPDATE userFavorites SET favState = ? WHERE user_id = ? AND exercise_id = ?", favstate, session['user_id'], session["ex_id"])
        favnum = db.execute("SELECT COUNT (favState) FROM userFavorites WHERE favState= 'true' AND exercise_id = ?", session["ex_id"])[0]['COUNT (favState)']
        db.execute("UPDATE uniqueExercises SET favorites = ? WHERE id = ?", favnum, session["ex_id"])
        return redirect("/favorite")
    return redirect("/afterInteraction")

@app.route("/rate", methods=["POST", "GET"])
@login_required
def rate():
    if request.method == "POST":
        rating = request.form.get('rating')
        if request.form.get('review'):
            review = request.form.get('review')
        else:
            review = ''
        db.execute("INSERT INTO userRatings (user_id, exercise_id, rating, review, username) VALUES (?, ?, ?, ?, ?)", session["user_id"], session['ex_id'], rating, review, session["username"])
        avg = db.execute("SELECT AVG (rating) FROM userRatings WHERE exercise_id = ?", session['ex_id'])[0]['AVG (rating)']
        if avg is None:
            db.execute("UPDATE uniqueExercises SET rating = ?, reviewcount = ? WHERE id = ?", 0, 0, session['ex_id'])
        else:
            reviewnum = db.execute("SELECT COUNT (rating) FROM userRatings WHERE exercise_id = ?", session['ex_id'])[0]['COUNT (rating)']
            db.execute("UPDATE uniqueExercises SET rating = ?, reviewcount = ? WHERE id = ?", avg, reviewnum, session['ex_id'])
        return redirect("/rate")
    return redirect("/afterInteraction")

@app.route("/delete", methods=["POST", "GET"])
@login_required
def delete():
    if request.method == "POST":
        db.execute("DELETE FROM userRatings WHERE user_id = ? AND exercise_id = ?", session['user_id'], session['ex_id'])
        avg = db.execute("SELECT AVG (rating) FROM userRatings WHERE exercise_id = ?", session['ex_id'])[0]['AVG (rating)']
        if avg is None:
            db.execute("UPDATE uniqueExercises SET rating = ?, reviewcount = ? WHERE id = ?", 0, 0, session['ex_id'])
        else:
            reviewnum = db.execute("SELECT COUNT (rating) FROM userRatings WHERE exercise_id = ?", session['ex_id'])[0]['COUNT (rating)']
            db.execute("UPDATE uniqueExercises SET rating = ?, reviewcount = ? WHERE id = ?", avg, reviewnum, session['ex_id'])
        return redirect("/delete")
    return redirect("/afterInteraction")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

         # Query database for username and ensure it is not already taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 0:
            return apology("username already taken", 400)

        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Log the new user in
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        exercises = db.execute("SELECT * FROM uniqueExercises")
        for exercise in exercises:
            id = exercise['id']
            db.execute("INSERT INTO userFavorites (user_id, exercise_id, favState) VALUES (?, ?, 'false')", rows[0]["id"], id)
        session["user_id"] = rows[0]["id"]
        session["username"] = username

        # Redirect user to home page
        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = request.form.get("username")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/pwdchange", methods=["GET", "POST"])
@login_required
def pwdchange():
    """Change password"""
    if request.method == "POST":

        oldpasswordhash = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])[0]["hash"]

        # Ensure form was submitted correctly
        if (not request.form.get("oldpassword")) or (not request.form.get("newpassword")) or (not request.form.get("confirmnewpassword")):
            return apology("must fill all boxes", 403)

        # Ensure passwords match
        elif request.form.get("newpassword") != request.form.get("confirmnewpassword"):
            return apology("new passwords must match", 403)

        elif not check_password_hash(oldpasswordhash, request.form.get("oldpassword")):
            return apology("enter old password correctly", 403)

        hash = generate_password_hash(request.form.get("newpassword"), method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])

        # Redirect user to home page
        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("pwdchange.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")