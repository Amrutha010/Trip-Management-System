from database import create_tables
from services import TripService, BookingService, ExpenseService, AuthService

create_tables()

trip_svc = TripService()
booking_svc = BookingService()
expense_svc = ExpenseService()
auth_svc = AuthService()

def seed():
    existing = trip_svc.list()
    if existing:
        print(f"Database already has data ({len(existing)} trips). Remove trip.db to reseed or run manually.")
        return

    # Create users
    admin = auth_svc.create_user("admin", "password", role="admin", agent_approved=True)
    customer = auth_svc.create_user("jane", "secret", role="customer", agent_approved=False)
    agent_approved = auth_svc.create_user("agentjohn", "agentpass", role="agent", agent_approved=True)
    agent_pending = auth_svc.create_user("newagent", "pending123", role="agent", agent_approved=False)

    # Create many sample trips
    trips = []
    trips.append(trip_svc.create(title="Weekend in Bali", destination="Bali, Indonesia", date="2026-03-20",
                                 description="Relaxing weekend with beach time and temple visits.", price=299.00))
    trips.append(trip_svc.create(title="City Break — Lisbon", destination="Lisbon, Portugal", date="2026-04-10",
                                 description="Historic trams, pastel de nata and riverfront walks.", price=199.50))
    trips.append(trip_svc.create(title="Northern Lights Adventure", destination="Reykjavik, Iceland", date="2026-12-05",
                                 description="Chase the aurora, soak in hot springs and explore glaciers.", price=1299.00))
    trips.append(trip_svc.create(title="Safari — Kenya", destination="Maasai Mara, Kenya", date="2026-08-15",
                                 description="Big five safari and cultural village visits.", price=1899.00))
    trips.append(trip_svc.create(title="Ski Weekend — Alps", destination="Chamonix, France", date="2026-02-14",
                                 description="Skiing, mountain huts and hot cocoa.", price=499.99))
    trips.append(trip_svc.create(title="Roadtrip — California", destination="San Francisco to LA, USA", date="2026-06-01",
                                 description="Scenic drives, vineyards and coastal towns.", price=899.00))

    # Create bookings spread across trips
    booking_svc.create(trip_id=trips[0].id, customer_name="Alice Johnson", seats=2, contact="alice@example.com")
    booking_svc.create(trip_id=trips[0].id, customer_name="Bob Smith", seats=1, contact="bob@example.com")
    booking_svc.create(trip_id=trips[1].id, customer_name="Carlos Mendes", seats=3, contact="carlos@example.com")
    booking_svc.create(trip_id=trips[2].id, customer_name="Emma Liu", seats=2, contact="emma@example.com")
    booking_svc.create(trip_id=trips[3].id, customer_name="Farah Khan", seats=4, contact="farah@example.com")
    booking_svc.create(trip_id=trips[4].id, customer_name="George Brown", seats=1, contact="george@example.com")
    booking_svc.create(trip_id=trips[5].id, customer_name="Hiro Tanaka", seats=2, contact="hiro@example.com")

    # Create various expenses
    expense_svc.create(trip_id=trips[0].id, title="Hotel deposit", amount=120.00, note="Non-refundable")
    expense_svc.create(trip_id=trips[0].id, title="Airport transfer", amount=35.00, note="Round trip taxi")
    expense_svc.create(trip_id=trips[1].id, title="City tour tickets", amount=60.00, note="Group discount")
    expense_svc.create(trip_id=trips[2].id, title="Guided glacier tour", amount=250.00, note="Optional activity")
    expense_svc.create(trip_id=trips[3].id, title="Park entrance fee", amount=40.00)
    expense_svc.create(trip_id=trips[4].id, title="Lift pass", amount=80.00)
    expense_svc.create(trip_id=trips[5].id, title="Car hire deposit", amount=200.00)

    # Expenses attached to bookings
    # find one booking to attach
    sample_booking = booking_svc.list_for_trip(trips[1].id)[0]
    expense_svc.create(trip_id=trips[1].id, booking_id=sample_booking.id, title="Extra luggage fee", amount=45.00, note="Prepaid")

    print("Seed data created:")
    print(f"  Trips: {len(trips)}")
    print("  Bookings: 7")
    print("  Expenses: 8")
    print("  Users: admin, jane (customer), agentjohn (approved agent), newagent (pending agent)")
    print("Run the app (python app.py) and open the UI to view the sample data.")

if __name__ == "__main__":
    seed()