from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    phone = Column(String(11), unique=True, nullable=True, index=True)   
    org = Column(String, nullable=True)                                  
    email = Column(String, unique=True, nullable=True, index=True)       
    work_address = Column(String, nullable=True) 
    role = Column(String(20), nullable=False, default="admin", index=True)                        

class Visitor(Base):
    __tablename__ = "visitor"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False, index=True)
    org = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reservations = relationship("Reservation", back_populates="visitor", cascade="all, delete-orphan")


class Reservation(Base):
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitor.id"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)


    location = Column(String, nullable=False, index=True)


    location_id = Column(Integer, ForeignKey("location.id"), nullable=True, index=True)

    purpose = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
    is_driving = Column(Integer, default=0, nullable=False)
    plate_number = Column(String(6), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    visitor = relationship("Visitor", back_populates="reservations")
    location_obj = relationship("Location", back_populates="reservations", lazy="joined", foreign_keys=[location_id])

class CampusEnum(str, enum.Enum):
    LOWER = "LOWER"
    MIDDLE = "MIDDLE"
    UPPER = "UPPER"


class Location(Base):
    __tablename__ = "location"
    id = Column(Integer, primary_key=True, index=True)
    campus = Column(String, nullable=False, index=True)  
    name = Column(String, nullable=False, index=True)    
    is_active = Column(Integer, default=1)
    reservations = relationship("Reservation", back_populates="location_obj", cascade="all, delete-orphan")

    __table_args__ = (
        Index("uq_location_campus_name", "campus", "name", unique=True),
    )

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visitor_id = Column(Integer, ForeignKey("visitor.id", ondelete="CASCADE"), index=True, nullable=False)
    type = Column(String(50), nullable=False)  
    reservation_id = Column(Integer, ForeignKey("reservation.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    body = Column(String, nullable=True)

    is_read = Column(Integer, default=0, nullable=False)  
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    visitor = relationship("Visitor", backref="notifications")

Index("ix_resv_loc_time", Reservation.location, Reservation.start_time, Reservation.end_time)
Index("ix_resv_status_date", Reservation.status, Reservation.start_time)