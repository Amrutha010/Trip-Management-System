import sqlite3

def get_connection():
    return sqlite3.connect("trip.db")

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT
    )
    """)

    # TRIPS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Trip (
        trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination TEXT,
        start_date TEXT,
        end_date TEXT,
        budget REAL,
        agent_id INTEGER,
        FOREIGN KEY(agent_id) REFERENCES User(user_id)
    )
    """)

    # PACKAGES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Package (
        package_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER,
        name TEXT,
        price REAL,
        description TEXT,
        FOREIGN KEY(trip_id) REFERENCES Trip(trip_id)
    )
    """)

    # BOOKINGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Booking (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        package_id INTEGER,
        status TEXT,
        FOREIGN KEY(user_id) REFERENCES User(user_id),
        FOREIGN KEY(package_id) REFERENCES Package(package_id)
    )
    """)

    # WISHLIST
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Wishlist (
        wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        package_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES User(user_id),
        FOREIGN KEY(package_id) REFERENCES Package(package_id)
    )
    """)

    # EXPENSES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Expense (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER,
        description TEXT,
        amount REAL,
        FOREIGN KEY(trip_id) REFERENCES Trip(trip_id)
    )
    """)

    conn.commit()
    conn.close()
