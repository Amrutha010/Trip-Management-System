from database import get_connection
from models import Trip, Expense

def add_trip(trip):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Trip(destination, start_date, end_date, budget) VALUES (?, ?, ?, ?)",
        (trip.destination, trip.start_date, trip.end_date, trip.budget)
    )
    conn.commit()
    conn.close()
    print("Trip added successfully")

def view_trips():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Trip")
    trips = cursor.fetchall()
    conn.close()

    if not trips:
        print("No trips found")
    else:
        for t in trips:
            print(t)

def update_trip_budget(trip_id, budget):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Trip SET budget = ? WHERE trip_id = ?", (budget, trip_id))
    conn.commit()
    conn.close()
    print("Trip updated successfully")

def delete_trip(trip_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Trip WHERE trip_id = ?", (trip_id,))
    conn.commit()
    conn.close()
    print("Trip deleted successfully")

def add_expense(expense):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Expense(trip_id, category, amount) VALUES (?, ?, ?)",
        (expense.trip_id, expense.category, expense.amount)
    )
    conn.commit()
    conn.close()
    print("Expense added successfully")

def view_expenses(trip_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Expense WHERE trip_id = ?", (trip_id,))
    expenses = cursor.fetchall()
    conn.close()

    if not expenses:
        print("No expenses found")
    else:
        for e in expenses:
            print(e)
