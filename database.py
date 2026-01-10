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
        budget REAL,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Expense (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER,
        category TEXT,
        description TEXT,
        amount REAL,
        FOREIGN KEY(trip_id) REFERENCES Trip(trip_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Booking (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER,
        user_id INTEGER,
        status TEXT,
        FOREIGN KEY(trip_id) REFERENCES Trip(trip_id),
        FOREIGN KEY(user_id) REFERENCES User(user_id)
    )
    """)

    conn.commit()
    conn.close()

