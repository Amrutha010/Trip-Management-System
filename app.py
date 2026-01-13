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
        role = request.form.get("role")

        if username == "admin":
            role = "admin"

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

        if role == "admin":
            return redirect("/admin")
        elif role == "agent":
            return redirect("/agent")
        else:
            return redirect("/customer")

    return render_template("login.html")


@app.route("/customer")
def customer_dashboard():
    if session.get("role") != "customer":
        return redirect("/login")

    conn = get_db()
    packages = conn.execute("""
        SELECT Package.package_id, Package.name, Package.price, Trip.destination
        FROM Package
        JOIN Trip ON Package.trip_id = Trip.trip_id
    """).fetchall()

    bookings = conn.execute("""
        SELECT Package.name, Booking.status
        FROM Booking
        JOIN Package ON Booking.package_id = Package.package_id
        WHERE Booking.user_id=?
    """, (session["user_id"],)).fetchall()

    wishlist = conn.execute("""
        SELECT Package.name
        FROM Wishlist
        JOIN Package ON Wishlist.package_id = Package.package_id
        WHERE Wishlist.user_id=?
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "customer.html",
        packages=packages,
        bookings=bookings,
        wishlist=wishlist
    )


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
    trips = conn.execute(
        "SELECT * FROM Trip WHERE agent_id=?",
        (session["user_id"],)
    ).fetchall()

    packages = conn.execute("""
        SELECT Package.package_id, Package.name, Package.price
        FROM Package
        JOIN Trip ON Package.trip_id = Trip.trip_id
        WHERE Trip.agent_id=?
    """, (session["user_id"],)).fetchall()

    bookings = conn.execute("""
        SELECT User.username, Package.name, Booking.status
        FROM Booking
        JOIN User ON Booking.user_id = User.user_id
        JOIN Package ON Booking.package_id = Package.package_id
        JOIN Trip ON Package.trip_id = Trip.trip_id
        WHERE Trip.agent_id=?
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "agent.html",
        trips=trips,
        packages=packages,
        bookings=bookings
    )

@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/login")

    conn = get_db()
    agents = conn.execute("SELECT * FROM User WHERE role='agent'").fetchall()
    trips = conn.execute("SELECT * FROM Trip").fetchall()
    packages = conn.execute("SELECT * FROM Package").fetchall()
    bookings = conn.execute("""
        SELECT Booking.booking_id, User.username, Package.name, Booking.status
        FROM Booking
        JOIN User ON Booking.user_id = User.user_id
        JOIN Package ON Booking.package_id = Package.package_id
    """).fetchall()
    conn.close()

    return render_template(
        "admin.html",
        agents=agents,
        trips=trips,
        packages=packages,
        bookings=bookings
    )

@app.route("/admin/create-agent", methods=["POST"])
def create_agent():
    if session.get("role") != "admin":
        return redirect("/login")

    username = request.form["username"]

    conn = get_db()
    conn.execute(
        "INSERT INTO User(username, role) VALUES (?, ?)",
        (username, "agent")
    )
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/book/<int:package_id>")
def book_package(package_id):
    conn = get_db()
    conn.execute(
        "INSERT INTO Booking(user_id, package_id, status) VALUES (?, ?, ?)",
        (session["user_id"], package_id, "Booked")
    )
    conn.commit()
    conn.close()
    return redirect("/customer")

@app.route("/wishlist/<int:package_id>")
def wishlist_package(package_id):
    conn = get_db()
    conn.execute(
        "INSERT INTO Wishlist(user_id, package_id) VALUES (?, ?)",
        (session["user_id"], package_id)
    )
    conn.commit()
    conn.close()
    return redirect("/customer")


if __name__ == "__main__":
    app.run(debug=True)
