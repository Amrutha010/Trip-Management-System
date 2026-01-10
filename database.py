import sqlite3

def get_connection():
    return sqlite3.connect("trip.db")

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Trip (
        trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination TEXT,
        start_date TEXT,
        end_date TEXT,
        budget REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Expense (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER,
        category TEXT,
        amount REAL,
        FOREIGN KEY(trip_id) REFERENCES Trip(trip_id)
    )
    """)

    conn.commit()
    conn.close()
