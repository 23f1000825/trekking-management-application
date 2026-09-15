from flask_login import UserMixin
from .database import db
from datetime import date,datetime


class User(UserMixin, db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    is_approved = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    bookings = db.relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    staff_profile = db.relationship("StaffProfile", uselist=False)

    def get_id(self):
        return str(self.user_id)


class Trek(db.Model):
    __tablename__ = "trek"

    trek_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    available_slots = db.Column(db.Integer, nullable=False)

    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id")
    )

    assigned_staff = db.relationship(
    "User",
    foreign_keys=[assigned_staff_id]
)

    status = db.Column(db.String(20), nullable=False)

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    bookings = db.relationship("Booking", back_populates="trek",cascade="all, delete-orphan")


class Booking(db.Model):
    __tablename__ = "booking"

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("trek.trek_id"),
        nullable=False
    )

    booking_date = db.Column(db.DateTime, nullable=False)

    booking_status = db.Column(
        db.String(20),
        nullable=False,
        default="Booked"
    )

    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")


class StaffProfile(db.Model):
    __tablename__ = "staff_profile"

    staff_profile_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
        nullable=False,
        unique=True
    )

    contact_number = db.Column(db.String(15))

    experience = db.Column(db.Integer)

    status = db.Column(
        db.String(20),
        default="Pending"
    )