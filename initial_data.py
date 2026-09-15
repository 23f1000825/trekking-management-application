# -*- coding: utf-8 -*-
from main import app
from application.database import db
from application.models import User, Trek, Booking, StaffProfile
from datetime import date, datetime, timedelta


def seed():
    with app.app_context():

        db.create_all()

        # ──────────────────────────────────────────────
        # 1. ADMIN
        # ──────────────────────────────────────────────
        admin = User.query.filter_by(email="admin@trek.com").first()
        if admin is None:
            admin = User(
                name="Admin",
                email="admin@trek.com",
                password="admin123",
                role="Admin",
                is_approved=True,
                is_blacklisted=False,
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("[+] Admin created")
        else:
            print("[-] Admin already exists")

        # ──────────────────────────────────────────────
        # 2. TREK STAFF  (4 members)
        # ──────────────────────────────────────────────
        staff_data = [
            {
                "name": "Rajan Sharma",
                "email": "rajan@trek.com",
                "password": "staff123",
                "contact": "+977-9841001122",
                "experience": 8
            },
            {
                "name": "Priya Nair",
                "email": "priya@trek.com",
                "password": "staff123",
                "contact": "+91-9876543210",
                "experience": 5
            },
            {
                "name": "Thomas Mueller",
                "email": "thomas@trek.com",
                "password": "staff123",
                "contact": "+49-15112345678",
                "experience": 12
            },
            {
                "name": "Sofia Moreno",
                "email": "sofia@trek.com",
                "password": "staff123",
                "contact": "+34-612345678",
                "experience": 3
            },
        ]

        staff_users = []
        for s in staff_data:
            existing = User.query.filter_by(email=s["email"]).first()
            if existing is None:
                user = User(
                    name=s["name"],
                    email=s["email"],
                    password=s["password"],
                    role="Trek Staff",
                    is_approved=True,
                    is_blacklisted=False,
                    is_active=True
                )
                db.session.add(user)
                db.session.flush()  # get the user_id

                profile = StaffProfile(
                    user_id=user.user_id,
                    contact_number=s["contact"],
                    experience=s["experience"],
                    status="Approved"
                )
                db.session.add(profile)
                staff_users.append(user)
                print(f"[+] Staff created: {s['name']}")
            else:
                staff_users.append(existing)
                print(f"[-] Staff exists: {s['name']}")

        db.session.commit()

        # ──────────────────────────────────────────────
        # 3. TREKKER USERS  (6 users)
        # ──────────────────────────────────────────────
        user_data = [
            {"name": "Alice Johnson",   "email": "alice@gmail.com",   "password": "user123"},
            {"name": "Bob Martinez",    "email": "bob@gmail.com",     "password": "user123"},
            {"name": "Chloe Thompson",  "email": "chloe@gmail.com",   "password": "user123"},
            {"name": "David Kim",       "email": "david@gmail.com",   "password": "user123"},
            {"name": "Emma Wilson",     "email": "emma@gmail.com",    "password": "user123"},
            {"name": "Faisal Al-Amin",  "email": "faisal@gmail.com",  "password": "user123"},
        ]

        trekker_users = []
        for u in user_data:
            existing = User.query.filter_by(email=u["email"]).first()
            if existing is None:
                user = User(
                    name=u["name"],
                    email=u["email"],
                    password=u["password"],
                    role="User",
                    is_approved=True,
                    is_blacklisted=False,
                    is_active=True
                )
                db.session.add(user)
                trekker_users.append(user)
                print(f"[+] User created: {u['name']}")
            else:
                trekker_users.append(existing)
                print(f"[-] User exists: {u['name']}")

        db.session.commit()

        # ──────────────────────────────────────────────
        # 4. TREKS  (8 treks across statuses)
        # ──────────────────────────────────────────────
        today = date.today()

        trek_data = [
            {
                "trek_name":       "Annapurna Base Camp",
                "location":        "Nepal",
                "difficulty":      "Hard",
                "duration":        14,
                "available_slots": 12,
                "status":          "Open",
                "start_offset":    30,   # days from today
                "staff_index":     0,    # rajan
            },
            {
                "trek_name":       "Everest Panorama Trail",
                "location":        "Nepal",
                "difficulty":      "Moderate",
                "duration":        10,
                "available_slots": 8,
                "status":          "Open",
                "start_offset":    20,
                "staff_index":     0,
            },
            {
                "trek_name":       "Swiss Alpine Circuit",
                "location":        "Switzerland",
                "difficulty":      "Moderate",
                "duration":        8,
                "available_slots": 15,
                "status":          "Open",
                "start_offset":    45,
                "staff_index":     2,    # thomas
            },
            {
                "trek_name":       "Mont Blanc Express",
                "location":        "France",
                "difficulty":      "Hard",
                "duration":        7,
                "available_slots": 10,
                "status":          "Open",
                "start_offset":    60,
                "staff_index":     3,    # sofia
            },
            {
                "trek_name":       "Kerala Western Ghats",
                "location":        "India",
                "difficulty":      "Easy",
                "duration":        5,
                "available_slots": 20,
                "status":          "Open",
                "start_offset":    15,
                "staff_index":     1,    # priya
            },
            {
                "trek_name":       "Patagonia Ridge Walk",
                "location":        "Argentina",
                "difficulty":      "Hard",
                "duration":        12,
                "available_slots": 0,
                "status":          "Closed",
                "start_offset":    5,
                "staff_index":     2,
            },
            {
                "trek_name":       "Langtang Valley Trek",
                "location":        "Nepal",
                "difficulty":      "Moderate",
                "duration":        9,
                "available_slots": 4,
                "status":          "Ongoing",
                "start_offset":    -5,   # started 5 days ago
                "staff_index":     0,
            },
            {
                "trek_name":       "Scottish Highlands Traverse",
                "location":        "Scotland",
                "difficulty":      "Easy",
                "duration":        6,
                "available_slots": 0,
                "status":          "Completed",
                "start_offset":    -30,
                "staff_index":     3,
            },
        ]

        treks = []
        for t in trek_data:
            existing = Trek.query.filter(
                db.func.lower(Trek.trek_name) == t["trek_name"].lower()
            ).first()

            if existing is None:
                start = today + timedelta(days=t["start_offset"])
                end   = start + timedelta(days=t["duration"])

                staff_user = staff_users[t["staff_index"]] if t["staff_index"] < len(staff_users) else None

                trek = Trek(
                    trek_name=t["trek_name"],
                    location=t["location"],
                    difficulty=t["difficulty"],
                    duration=t["duration"],
                    available_slots=t["available_slots"],
                    status=t["status"],
                    start_date=start,
                    end_date=end,
                    assigned_staff_id=staff_user.user_id if staff_user else None
                )
                db.session.add(trek)
                treks.append(trek)
                print(f"[+] Trek created: {t['trek_name']}")
            else:
                treks.append(existing)
                print(f"[-] Trek exists: {t['trek_name']}")

        db.session.commit()

        # ──────────────────────────────────────────────
        # 5. BOOKINGS  (12 bookings, varied statuses)
        # ──────────────────────────────────────────────
        bookings_data = [
            # (user_index, trek_index, booking_status, days_ago_booked)
            (0, 0, "Booked",    7),
            (1, 0, "Booked",    5),
            (2, 0, "Booked",    3),
            (3, 1, "Booked",    10),
            (4, 1, "Booked",    8),
            (5, 2, "Booked",    12),
            (0, 2, "Booked",    6),
            (1, 4, "Booked",    2),
            (2, 4, "Booked",    1),
            (3, 6, "Booked",    14),  # Ongoing trek
            (4, 6, "Booked",    14),  # Ongoing trek
            (5, 7, "Completed", 40),  # Completed trek
            (0, 7, "Completed", 38),  # Completed trek
            (1, 5, "Cancelled", 20),  # Cancelled on closed trek
        ]

        for (ui, ti, status, days_ago) in bookings_data:
            if ui >= len(trekker_users) or ti >= len(treks):
                continue

            user  = trekker_users[ui]
            trek  = treks[ti]

            # Avoid duplicates
            exists = Booking.query.filter_by(
                user_id=user.user_id,
                trek_id=trek.trek_id
            ).first()

            if exists is None:
                booking = Booking(
                    user_id=user.user_id,
                    trek_id=trek.trek_id,
                    booking_date=datetime.now() - timedelta(days=days_ago),
                    booking_status=status,
                    payment_status="Paid" if status in ("Completed", "Booked") else "Refunded"
                )
                db.session.add(booking)
                print(f"[+] Booking: {user.name} -> {trek.trek_name} [{status}]")
            else:
                print(f"[-] Booking exists: {user.name} -> {trek.trek_name}")

        db.session.commit()

        print("\nSeeding complete!")
        print("---------------------------------")
        print("  Admin    : admin@trek.com / admin123")
        print("  Staff    : rajan@trek.com / staff123  (and 3 more)")
        print("  Trekkers : alice@gmail.com / user123  (and 5 more)")
        print("---------------------------------")


if __name__ == "__main__":
    seed()