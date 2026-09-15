import os
from flask import Flask

from application.config import LocalDevelopmentConfig, ProductionConfig
from application.database import db
from application.database import login_manager
from application.models import User
from sqlalchemy import or_
app = None


def create_app():
    app = Flask(__name__, template_folder="templates")

    app.secret_key = "trekking_management_secret_key"

    if os.getenv("ENV") == "production" or os.getenv("VERCEL"):
        print("Starting Production Environment")
        app.config.from_object(ProductionConfig)
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)
    login_manager.init_app(app)
    app.app_context().push()

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from application.controllers import *

with app.app_context():
    db.create_all()
    try:
        if User.query.count() == 0:
            from initial_data import seed
            seed()
    except Exception as e:
        print("Seeding exception:", e)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )