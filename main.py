import os
from flask import Flask

from application.config import LocalDevelopmentConfig, ProductionConfig
from application.database import db
from application.database import login_manager
from application.models import User
from sqlalchemy import or_
app = None


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )

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


import application.controllers

with app.app_context():
    try:
        db.create_all()
        if User.query.count() == 0:
            from initial_data import seed
            seed(app)
    except Exception as e:
        print("Database init exception:", e)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )