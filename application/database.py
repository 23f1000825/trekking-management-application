from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

engine = None
Base = declarative_base()
db = SQLAlchemy()

login_manager = LoginManager()

login_manager.login_view = "login"
login_manager.login_message = "Please login to continue."