from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime

class EventCategory(enum.Enum):
    SPOR = "spor"
    EGITIM = "egitim"
    KULTUR = "kultur"
    SANAT = "sanat"
    SINAV = "sinav"
    DIGER = "diger"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    interest = Column(String)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    agendas = relationship("Agenda", back_populates="user")
    def __repr__(self):
        return f"<User {self.name}>"

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(Enum(EventCategory), nullable=False)
    date = Column(DateTime, nullable=False)
    start_time = Column(String, nullable=False)
    duration = Column(Integer, default=60)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    organizer = Column(String, nullable=True)
    popularity = Column(Integer, default=0)
    max_participants = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    agendas = relationship("Agenda", back_populates="event")
    def __repr__(self):
        return f"<Event {self.name} at {self.date}>"
    @property
    def is_full(self):
        if self.max_participants:
            return len(self.agendas) >= self.max_participants
        return False

class Agenda(Base):
    __tablename__ = "agenda"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    reminder_sent = Column(Boolean, default=False)
    user = relationship("User", back_populates="agendas")
    event = relationship("Event", back_populates="agendas")
    def __repr__(self):
        return f"<Agenda User:{self.user_id} Event:{self.event_id}>"
    class Config:
        orm_mode = True
