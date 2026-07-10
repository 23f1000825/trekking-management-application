from main import app
from application.database import db
from application.models import User


with app.app_context():

    db.create_all()

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

        print("Admin created successfully.")

    else:
        print("Admin already exists.")