# Trip Management System

The Trip Management System is an Object-Oriented Flask application designed to manage travel-related information efficiently. The system enables users to create, view, update, and delete trip details, bookings, and expenses through a user-friendly interface. It demonstrates OOP principles (encapsulation, inheritance, polymorphism) with a clear service layer and domain models.

Features
- Trips: create/read/update/delete trips (title, destination, date, description, price).
- Bookings: add bookings per trip (customer name, seats, contact).
- Expenses: record expenses linked to trips or bookings (title, amount, note).
- Simple auth for admin (session-based).
- Small JSON API for programmatic access (/api/trips, /api/trip/<id>).
- OOP design: SQLAlchemy models with shared behaviour and a service layer (TripService, BookingService, ExpenseService) that encapsulates DB operations.

Quick start (Windows)
1. Create & activate venv (PowerShell):
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install deps:
   ```
   pip install -r requirements.txt
   ```
3. Run:
   ```
   python app.py
   ```
4. Admin: username `admin`, password `password` (change in app.py).
