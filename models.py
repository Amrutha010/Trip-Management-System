from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import Base

class BaseRecord:
    """Behaviour/methods common to domain records (example of encapsulation)."""
    def to_dict(self):
        result = {}
        for col in self.__table__.columns:
            v = getattr(self, col.name)
            if isinstance(v, datetime):
                v = v.isoformat()
            result[col.name] = v
        return result

class User(Base, BaseRecord):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="customer")  # customer | agent | admin
    agent_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

class Trip(Base, BaseRecord):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=True)
    date = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)

    bookings = relationship("Booking", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="trip", cascade="all, delete-orphan")

    def summary(self):
        return f"{self.title} — {self.destination or 'TBA'}"

class Booking(Base, BaseRecord):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)   # link booking to logged-in user (customer)
    customer_name = Column(String(200), nullable=False)
    seats = Column(Integer, nullable=False, default=1)
    contact = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="bookings")
    user = relationship("User", backref="bookings")
    expenses = relationship("Expense", back_populates="booking", cascade="all, delete-orphan")

    def total_cost_hint(self, trip_price: float):
        if trip_price:
            return (trip_price or 0.0) * (self.seats or 1)
        return None

class Expense(Base, BaseRecord):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    title = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="expenses")
    booking = relationship("Booking", back_populates="expenses")
