from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

# -------------------- Core Users / Check-ins / Chat --------------------

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    plan = Column(String, default="free", nullable=False)  # "free" | "premium"
    deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    checkins = relationship("AICheckIn", back_populates="user")
    sessions = relationship("ChatSession", back_populates="user")
    bookings = relationship("Booking", back_populates="user")


class AICheckIn(Base):
    __tablename__ = "ai_checkins"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood = Column(String, nullable=False)
    stress_level = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="checkins")
    sessions = relationship("ChatSession", back_populates="checkin")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, default="New session", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    checkin_id = Column(Integer, ForeignKey("ai_checkins.id"), nullable=True)

    mood_at_start = Column(String, nullable=True)
    stress_at_start = Column(Integer, nullable=True)

    user = relationship("User", back_populates="sessions")
    checkin = relationship("AICheckIn", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatRole:
    user = "user"
    assistant = "assistant"


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' | 'assistant'
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    url = Column(String, nullable=False)
    deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# -------------------- Therapist Booking (NEW) --------------------

class BookingStatus:
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class Counselor(Base):
    __tablename__ = "counselors"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    specialties = Column(String, nullable=True)  # comma-separated keywords
    price_cents = Column(Integer, default=0, nullable=False)
    currency = Column(String, default="BND", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    slots = relationship("AvailabilitySlot", back_populates="counselor", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="counselor")


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    id = Column(Integer, primary_key=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)  # store in UTC
    end_time = Column(DateTime, nullable=False)
    is_booked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    counselor = relationship("Counselor", back_populates="slots")
    booking = relationship("Booking", back_populates="slot", uselist=False)


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("availability_slots.id"), unique=True, nullable=False)
    status = Column(String, default=BookingStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    counselor = relationship("Counselor", back_populates="bookings")
    slot = relationship("AvailabilitySlot", back_populates="booking")
