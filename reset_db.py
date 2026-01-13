import os
from database import create_tables
from services import TripService, BookingService, ExpenseService, AuthService

DB_FILE = "trip.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("Deleted existing trip.db")

create_tables()
trip_svc = TripService()
booking_svc = BookingService()
expense_svc = ExpenseService()
auth_svc = AuthService()

def seed():
    admin = auth_svc.create_user("admin", "password", role="admin", agent_approved=True)
    jane = auth_svc.create_user("jane", "secret", role="customer")
    john = auth_svc.create_user("john", "secret", role="customer")
    agent_approved = auth_svc.create_user("agentjohn", "agentpass", role="agent", agent_approved=True)
    agent_pending = auth_svc.create_user("newagent", "pending123", role="agent", agent_approved=False)

    trips = [
        trip_svc.create(title="Weekend in Bali", destination="Bali, Indonesia", date="2026-03-20",
                        description="Relaxing weekend with beach time and temple visits.", price=299.00),
        trip_svc.create(title="City Break — Lisbon", destination="Lisbon, Portugal", date="2026-04-10",
                        description="Historic trams, pastel de nata and riverfront walks.", price=199.50),
        trip_svc.create(title="Northern Lights Adventure", destination="Reykjavik, Iceland", date="2026-12-05",
                        description="Chase the aurora, soak in hot springs and explore glaciers.", price=1299.00),
    ]

    booking_svc.create(trip_id=trips[0].id, user_id=jane.id, customer_name="Jane Doe", seats=2, contact="jane@example.com")
    booking_svc.create(trip_id=trips[1].id, user_id=john.id, customer_name="John Roe", seats=1, contact="john@example.com")
    booking_svc.create(trip_id=trips[2].id, user_id=None, customer_name="Walk-in Customer", seats=1, contact="walkin@example.com")

    expense_svc.create(trip_id=trips[0].id, title="Hotel deposit", amount=120.00, note="Non-refundable")
    expense_svc.create(trip_id=trips[1].id, title="City tour tickets", amount=60.00, note="Group discount")
    expense_svc.create(trip_id=trips[2].id, title="Guided glacier tour", amount=250.00, note="Optional activity")

    print("DB reset and seeded:")
    print("  Users: admin,jane,john,agentjohn,newagent")
    print(f"  Trips: {len(trips)}")
    print("  Bookings: 3")
    print("  Expenses: 3")

if __name__ == "__main__":
    seed()