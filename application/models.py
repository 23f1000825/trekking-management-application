from .database import db


class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    bookings = db.relationship("Booking", backref="user", lazy=True)
    staff_profile = db.relationship("StaffProfile", backref="user", uselist=False)


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

    status = db.Column(db.String(20), nullable=False)

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    bookings = db.relationship("Booking", backref="trek", lazy=True)


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

    booking_date = db.Column(db.Date)

    booking_status = db.Column(
        db.String(20),
        default="Booked"
    )

    payment_status = db.Column(
        db.String(20),
        default="Pending"
    )


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