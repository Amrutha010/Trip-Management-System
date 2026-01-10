from database import create_tables
from models import Trip
from service import add_trip, view_trips, update_trip_budget, delete_trip,add_expense, view_expenses

create_tables()

while True:
    print("\n--- Trip Management System ---")
    print("1. Add Trip")
    print("2. View Trips")
    print("3. Update Trip Budget")
    print("4. Delete Trip")
    print("5. Add Expense")
    print("6. View Expenses")
    print("7. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        dest = input("Destination: ")
        start = input("Start Date: ")
        end = input("End Date: ")
        budget = float(input("Budget: "))
        trip = Trip(dest, start, end, budget)
        add_trip(trip)

    elif choice == "2":
        view_trips()

    elif choice == "3":
        trip_id = int(input("Trip ID: "))
        budget = float(input("New Budget: "))
        update_trip_budget(trip_id, budget)

    elif choice == "4":
        trip_id = int(input("Trip ID: "))
        delete_trip(trip_id)

    elif choice == "5":
        trip_id = int(input("Trip ID: "))
        category = input("Expense Category: ")
        amount = float(input("Amount: "))
        expense = Expense(trip_id, category, amount)
        add_expense(expense)

    elif choice == "6":
        trip_id = int(input("Trip ID: "))
        view_expenses(trip_id)

    elif choice == "7":
        print("Exiting...")
        break

    else:
        print("Invalid choice")
