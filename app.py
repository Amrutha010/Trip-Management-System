from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from database import create_tables
from services import TripService, BookingService, ExpenseService, AuthService
from functools import wraps
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
import notifications
import os

create_tables()

app = Flask(__name__)
app.secret_key = "dev-secret-change-this"
csrf = CSRFProtect(app)

trip_svc = TripService()
booking_svc = BookingService()
expense_svc = ExpenseService()
auth_svc = AuthService()

# expose current_user and csrf_token to templates
@app.context_processor
def inject_user():
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = auth_svc.get_user_by_id(user_id)
    return dict(current_user=user, csrf_token=generate_csrf)

def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_id = session.get("user_id")
            user = auth_svc.get_user_by_id(user_id) if user_id else None
            if not user:
                flash("Login required.")
                return redirect(url_for("login"))
            if user.role not in allowed_roles:
                flash("Access denied.")
                return redirect(url_for("index"))
            if user.role == "agent" and not user.agent_approved:
                flash("Agent account pending approval.")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route("/")
def index():
    trips = trip_svc.list()
    return render_template("index.html", trips=trips)

# Auth
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Username and password required.")
            return redirect(url_for("signup"))
        user = auth_svc.create_user(username=username, password=password, role="customer")
        if not user:
            flash("Username already exists. Choose a different username.")
            return redirect(url_for("signup"))
        session["user_id"] = user.id
        flash("Account created. You are signed in.")
        return redirect(url_for("index"))
    return render_template("signup_customer.html")

@app.route("/agent/signup", methods=["GET", "POST"])
def agent_signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Username and password required.")
            return redirect(url_for("agent_signup"))
        user = auth_svc.create_user(username=username, password=password, role="agent", agent_approved=False)
        if not user:
            flash("Username already exists. Choose a different username.")
            return redirect(url_for("agent_signup"))
        flash("Agent account created and pending admin approval.")
        return redirect(url_for("index"))
    return render_template("signup_agent.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = auth_svc.authenticate(username, password)
        if user:
            session["user_id"] = user.id
            flash(f"Welcome, {user.username}.")
            if user.role == "admin":
                return redirect(url_for("admin"))
            if user.role == "agent" and user.agent_approved:
                return redirect(url_for("agent"))
            return redirect(url_for("index"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Signed out.")
    return redirect(url_for("index"))

# Trips (agent/admin only to create/edit/delete)
@app.route("/trip/add", methods=["GET", "POST"])
@require_role(["agent", "admin"])
def add_trip():
    if request.method == "POST":
        data = {
            "title": request.form.get("title", "").strip(),
            "destination": request.form.get("destination", "").strip(),
            "date": request.form.get("date", "").strip(),
            "description": request.form.get("description", "").strip(),
            "price": float(request.form.get("price")) if request.form.get("price") else None
        }
        if not data["title"]:
            flash("Title required.")
            return redirect(url_for("add_trip"))
        trip = trip_svc.create(**data)
        flash("Trip created.")
        return redirect(url_for("view_trip", id=trip.id))
    return render_template("add_trip.html", trip=None)

@app.route("/trip/<int:id>")
def view_trip(id):
    trip = trip_svc.get(id)
    if not trip:
        flash("Trip not found.")
        return redirect(url_for("index"))
    bookings = booking_svc.list_for_trip(id)
    expenses = expense_svc.list_for_trip(id)
    return render_template("view_trip.html", trip=trip, bookings=bookings, expenses=expenses)

@app.route("/trip/<int:id>/edit", methods=["GET", "POST"])
@require_role(["agent", "admin"])
def edit_trip(id):
    trip = trip_svc.get(id)
    if not trip:
        flash("Trip not found.")
        return redirect(url_for("index"))
    if request.method == "POST":
        data = {
            "title": request.form.get("title", trip.title).strip(),
            "destination": request.form.get("destination", trip.destination).strip(),
            "date": request.form.get("date", trip.date).strip(),
            "description": request.form.get("description", trip.description).strip(),
            "price": float(request.form.get("price")) if request.form.get("price") else None
        }
        trip_svc.update(id, **data)
        flash("Trip updated.")
        return redirect(url_for("view_trip", id=id))
    return render_template("add_trip.html", trip=trip)

@app.route("/trip/<int:id>/delete", methods=["POST"])
@require_role(["agent", "admin"])
def delete_trip(id):
    trip_svc.delete(id)
    flash("Trip deleted.")
    return redirect(url_for("index"))

# Bookings listing (role-aware)
@app.route("/bookings")
def all_bookings():
    user = session.get("user_id") and auth_svc.get_user_by_id(session.get("user_id"))
    if not user:
        flash("Login required to view bookings.")
        return redirect(url_for("login"))
    if user.role == "customer":
        bookings = booking_svc.list_for_user(user.id)
    else:
        bookings = booking_svc.list_all()
    return render_template("bookings_list.html", bookings=bookings)

# Booking flow: modal posts to checkout, then complete
@app.route("/booking/checkout", methods=["POST"])
def booking_checkout():
    trip_id = request.form.get("trip_id")
    if not trip_id:
        flash("Trip not specified.")
        return redirect(url_for("index"))
    try:
        trip_id = int(trip_id)
    except ValueError:
        flash("Invalid trip.")
        return redirect(url_for("index"))
    trip = trip_svc.get(trip_id)
    if not trip:
        flash("Trip not found.")
        return redirect(url_for("index"))
    customer_name = request.form.get("customer_name", "").strip() or "Guest"
    seats = int(request.form.get("seats") or 1)
    contact = request.form.get("contact", "").strip()
    # store pending booking in session for payment step
    session["pending_booking"] = {"trip_id": trip_id, "customer_name": customer_name, "seats": seats, "contact": contact}
    return render_template("payment.html", trip=trip, booking=session["pending_booking"])

@app.route("/booking/complete", methods=["POST"])
def booking_complete():
    # CSRFProtect enforces token automatically for POST requests when enabled.
    pending = session.pop("pending_booking", None)
    if not pending:
        flash("No pending booking.")
        return redirect(url_for("index"))
    user_id = session.get("user_id")
    booking = booking_svc.create(trip_id=pending["trip_id"],
                                 user_id=user_id,
                                 customer_name=pending["customer_name"],
                                 seats=pending["seats"],
                                 contact=pending["contact"])
    # render confirmation page with booking and trip info
    trip = trip_svc.get(booking.trip_id)
    return render_template("booking_confirmation.html", booking=booking, trip=trip)

# Classic add-booking page (optional) - kept but unique name
@app.route("/trip/<int:trip_id>/booking/add", methods=["GET"], endpoint="add_booking_page")
def add_booking_page(trip_id):
    trip = trip_svc.get(trip_id)
    if not trip:
        flash("Trip not found.")
        return redirect(url_for("index"))
    return render_template("add_booking.html", trip=trip, booking=None)

@app.route("/booking/<int:id>")
def view_booking(id):
    booking = booking_svc.get(id)
    if not booking:
        flash("Booking not found.")
        return redirect(url_for("index"))
    return render_template("view_booking.html", booking=booking, expenses=expense_svc.list_for_booking(id))

@app.route("/booking/<int:id>/edit", methods=["GET", "POST"])
@require_role(["agent", "admin"])
def edit_booking(id):
    booking = booking_svc.get(id)
    if not booking:
        flash("Booking not found.")
        return redirect(url_for("index"))
    if request.method == "POST":
        data = {
            "customer_name": request.form.get("customer_name", booking.customer_name).strip(),
            "seats": int(request.form.get("seats") or booking.seats),
            "contact": request.form.get("contact", booking.contact).strip()
        }
        booking_svc.update(id, **data)
        flash("Booking updated.")
        return redirect(url_for("view_booking", id=id))
    return render_template("add_booking.html", trip=booking.trip, booking=booking)

@app.route("/booking/<int:id>/delete", methods=["POST"])
@require_role(["agent", "admin"])
def delete_booking(id):
    b = booking_svc.get(id)
    trip_id = b.trip_id if b else None
    booking_svc.delete(id)
    flash("Booking deleted.")
    return redirect(url_for("bookings_for_trip", trip_id=trip_id) if trip_id else url_for("all_bookings"))

@app.route("/trip/<int:trip_id>/bookings")
@require_role(["agent", "admin"])
def bookings_for_trip(trip_id):
    trip = trip_svc.get(trip_id)
    if not trip:
        flash("Trip not found.")
        return redirect(url_for("index"))
    bookings = booking_svc.list_for_trip(trip_id)
    return render_template("bookings.html", trip=trip, bookings=bookings)

# Admin
@app.route("/admin")
@require_role(["admin"])
def admin():
    trips = trip_svc.list()
    pending_agents = auth_svc.list_pending_agents()
    return render_template("admin.html", trips=trips, pending_agents=pending_agents)

@app.route("/customer")
@require_role(["customer"])
def customer():
    """Customer area: show current customer's bookings."""
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in.")
        return redirect(url_for("login"))
    user = auth_svc.get_user_by_id(user_id)
    if not user or user.role != "customer":
        flash("Customer access only.")
        return redirect(url_for("index"))
    bookings = booking_svc.list_for_user(user.id)
    return render_template("customer.html", bookings=bookings, current_user=user)

@app.route("/admin/users")
@require_role(["admin"])
def admin_users():
    users = auth_svc.list_users()
    return render_template("admin_users.html", users=users)

@app.route("/admin/agents")
@require_role(["admin"])
def admin_agents():
    agents = auth_svc.list_agents()
    return render_template("admin_agents.html", agents=agents)

@app.route("/admin/agent/<int:agent_id>/approve", methods=["POST"])
@require_role(["admin"])
def approve_agent(agent_id):
    ok = auth_svc.approve_agent(agent_id)
    if ok:
        user = auth_svc.get_user_by_id(agent_id)
        try:
            notifications.notify_agent_approval(user, approved=True)
        except Exception:
            pass
        flash("Agent approved.")
    else:
        flash("Could not approve agent.")
    return redirect(url_for("admin_agents"))

@app.route("/admin/agent/<int:agent_id>/reject", methods=["POST"])
@require_role(["admin"])
def reject_agent(agent_id):
    u = auth_svc.get_user_by_id(agent_id)
    ok = auth_svc.reject_agent(agent_id)
    if ok:
        try:
            notifications.notify_agent_approval(u, approved=False)
        except Exception:
            pass
        flash("Agent request rejected and account removed.")
    else:
        flash("Could not reject agent.")
    return redirect(url_for("admin_agents"))

# Simple JSON API endpoints
@app.route("/api/trips")
def api_trips():
    items = [t.to_dict() for t in trip_svc.list()]
    return jsonify(items)

@app.route("/api/trip/<int:id>")
def api_trip(id):
    t = trip_svc.get(id)
    if not t:
        return jsonify({"error": "not found"}), 404
    return jsonify(t.to_dict())

@app.route("/agent")
@require_role(["agent"])
def agent():
    """Agent dashboard — approved agents only (decorator enforces approval)."""
    trips = trip_svc.list()
    return render_template("agent.html", trips=trips)

@app.route("/agent/onboard/<token>", methods=["GET", "POST"])
def agent_onboard(token):
    """Agent onboarding page reachable only with the secret onboarding token in the URL."""
    expected = os.environ.get("ONBOARD_TOKEN", "onboard-secret")
    if token != expected:
        # hide the endpoint if token doesn't match
        abort(404)
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Username and password required.")
            return redirect(url_for("agent_onboard", token=token))
        user = auth_svc.create_user(username=username, password=password, role="agent", agent_approved=False)
        if not user:
            flash("Username already exists. Choose a different username.")
            return redirect(url_for("agent_onboard", token=token))
        flash("Agent account created and pending admin approval.")
        return redirect(url_for("index"))
    return render_template("signup_agent.html", token=token)

if __name__ == "__main__":
    app.run(debug=True)
