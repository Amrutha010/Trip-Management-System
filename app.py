from flask import Flask, render_template, request, redirect, url_for
from flask import session
from database import create_tables

import sqlite3

app = Flask(__name__)
app.secret_key = "college-project-secret"
create_tables()


def get_db():
    return sqlite3.connect("trip.db")



@app.route("/")
def index():
    conn = get_db()
    trips = conn.execute("SELECT * FROM Trip").fetchall()
    conn.close()
    return render_template("index.html", trips=trips)

@app.route("/add", methods=["GET", "POST"])
def add_trip():
    if request.method == "POST":
        dest = request.form["destination"]
        start = request.form["start_date"]
        end = request.form["end_date"]
        budget = request.form["budget"]

        conn = get_db()
        conn.execute(
            "INSERT INTO Trip(destination, start_date, end_date, budget) VALUES (?, ?, ?, ?)",
            (dest, start, end, budget)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add_trip.html")

@app.route("/delete/<int:trip_id>")
def delete_trip(trip_id):
    conn = get_db()
    conn.execute("DELETE FROM Trip WHERE trip_id = ?", (trip_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/expenses/<int:trip_id>", methods=["GET", "POST"])
def expenses(trip_id):
    conn = get_db()

    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]
        amount = request.form["amount"]

        conn.execute(
            "INSERT INTO Expense(trip_id, category, description, amount) VALUES (?, ?, ?, ?)",
            (trip_id, category, description, amount)
        )
        conn.commit()

    trip = conn.execute("SELECT * FROM Trip WHERE trip_id=?", (trip_id,)).fetchone()
    expenses = conn.execute("SELECT * FROM Expense WHERE trip_id=?", (trip_id,)).fetchall()
    total = sum(e[4] for e in expenses)
    conn.close()

    return render_template(
        "expenses.html",
        trip=trip,
        expenses=expenses,
        total=total
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM User WHERE username=? AND role=?",
            (username, role)
        ).fetchone()

        if not user:
            conn.execute(
                "INSERT INTO User(username, role) VALUES (?, ?)",
                (username, role)
            )
            conn.commit()
            user = conn.execute(
                "SELECT * FROM User WHERE username=? AND role=?",
                (username, role)
            ).fetchone()

        session["user_id"] = user[0]
        session["role"] = role
        conn.close()

        if role == "agent":
            return redirect("/agent")
        else:
            return redirect("/customer")

    return render_template("login.html")

@app.route("/customer")
def customer_dashboard():
    if session.get("role") != "customer":
        return redirect("/login")

    conn = get_db()
    trips = conn.execute("SELECT * FROM Trip").fetchall()
    conn.close()

    return render_template("customer.html", trips=trips)

@app.route("/apply/<int:trip_id>")
def apply_trip(trip_id):
    if session.get("role") != "customer":
        return redirect("/login")

    conn = get_db()
    conn.execute(
        "INSERT INTO Booking(trip_id, user_id, status) VALUES (?, ?, ?)",
        (trip_id, session["user_id"], "Applied")
    )
    conn.commit()
    conn.close()

    return redirect("/customer")

@app.route("/agent")
def agent_dashboard():
    if session.get("role") != "agent":
        return redirect("/login")

    conn = get_db()
    trips = conn.execute("SELECT * FROM Trip").fetchall()
    bookings = conn.execute("""
        SELECT Booking.booking_id, User.username, Trip.destination, Booking.status
        FROM Booking
        JOIN User ON Booking.user_id = User.user_id
        JOIN Trip ON Booking.trip_id = Trip.trip_id
    """).fetchall()
    conn.close()

    return render_template("agent.html", trips=trips, bookings=bookings)


if __name__ == "__main__":
    app.run(debug=True)
