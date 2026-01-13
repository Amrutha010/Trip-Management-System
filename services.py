from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Trip, Booking, Expense, User

class ServiceBase:
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

class TripService(ServiceBase):
    def list(self) -> List[Trip]:
        return self.db.query(Trip).order_by(Trip.id.desc()).all()

    def get(self, id: int) -> Optional[Trip]:
        return self.db.query(Trip).get(id)

    def create(self, **data) -> Trip:
        trip = Trip(**data)
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        return trip

    def update(self, id: int, **data) -> Optional[Trip]:
        trip = self.get(id)
        if not trip:
            return None
        for k, v in data.items():
            setattr(trip, k, v)
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        return trip

    def delete(self, id: int) -> bool:
        trip = self.get(id)
        if not trip:
            return False
        self.db.delete(trip)
        self.db.commit()
        return True

class BookingService(ServiceBase):
    def list_for_trip(self, trip_id: int) -> List[Booking]:
        return self.db.query(Booking).filter(Booking.trip_id == trip_id).order_by(Booking.created_at.desc()).all()

    def list_all(self) -> List[Booking]:
        return self.db.query(Booking).order_by(Booking.created_at.desc()).all()

    def list_for_user(self, user_id: int) -> List[Booking]:
        return self.db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.created_at.desc()).all()

    def get(self, id: int) -> Optional[Booking]:
        return self.db.query(Booking).get(id)

    def create(self, trip_id: int, user_id: Optional[int] = None, **data) -> Booking:
        booking = Booking(trip_id=trip_id, user_id=user_id, **data)
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update(self, id: int, **data) -> Optional[Booking]:
        booking = self.get(id)
        if not booking:
            return None
        for k, v in data.items():
            setattr(booking, k, v)
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def delete(self, id: int) -> bool:
        booking = self.get(id)
        if not booking:
            return False
        self.db.delete(booking)
        self.db.commit()
        return True

class ExpenseService(ServiceBase):
    def list_for_trip(self, trip_id: int):
        return self.db.query(Expense).filter(Expense.trip_id == trip_id).order_by(Expense.created_at.desc()).all()

    def list_for_booking(self, booking_id: int):
        return self.db.query(Expense).filter(Expense.booking_id == booking_id).order_by(Expense.created_at.desc()).all()

    def get(self, id: int) -> Optional[Expense]:
        return self.db.query(Expense).get(id)

    def create(self, **data) -> Expense:
        expense = Expense(**data)
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def update(self, id: int, **data) -> Optional[Expense]:
        expense = self.get(id)
        if not expense:
            return None
        for k, v in data.items():
            setattr(expense, k, v)
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def delete(self, id: int) -> bool:
        expense = self.get(id)
        if not expense:
            return False
        self.db.delete(expense)
        self.db.commit()
        return True

class AuthService(ServiceBase):
    def create_user(self, username: str, password: str, role: str = "customer", agent_approved: bool = False) -> Optional[User]:
        # Enforce unique usernames: if user exists, do not overwrite password/role
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            return None
        user = User(username=username, role=role, agent_approved=agent_approved)
        user.set_password(password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if user.check_password(password):
            return user
        return None

    def get_user_by_id(self, id: int) -> Optional[User]:
        return self.db.query(User).get(id)

    def list_pending_agents(self) -> List[User]:
        return self.db.query(User).filter(User.role == "agent", User.agent_approved == False).order_by(User.created_at.asc()).all()

    def approve_agent(self, id: int) -> bool:
        u = self.get_user_by_id(id)
        if not u or u.role != "agent":
            return False
        u.agent_approved = True
        self.db.add(u)
        self.db.commit()
        return True

    def reject_agent(self, id: int) -> bool:
        u = self.get_user_by_id(id)
        if not u or u.role != "agent":
            return False
        self.db.delete(u)
        self.db.commit()
        return True

    def list_users(self) -> List[User]:
        return self.db.query(User).order_by(User.created_at.desc()).all()

    def list_agents(self) -> List[User]:
        return self.db.query(User).filter(User.role == "agent").order_by(User.created_at.desc()).all()