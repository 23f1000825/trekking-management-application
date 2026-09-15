import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    if not os.path.exists(SQLITE_DB_DIR):
        try:
            os.makedirs(SQLITE_DB_DIR, exist_ok=True)
        except Exception:
            SQLITE_DB_DIR = os.getenv("TMPDIR", "/tmp")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "trekking.sqlite3")
    DEBUG = True


class ProductionConfig(Config):
    SQLITE_DB_DIR = os.getenv("TMPDIR", "/tmp")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "trekking.sqlite3")
    DEBUG = False