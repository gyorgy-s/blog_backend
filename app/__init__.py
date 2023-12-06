import os
from flask import Flask


def get_app_key():
    with open(os.path.join("", "app", ".config",  "app.key")) as f:
        key = f.readline().strip()
    return key

def get_db():
    with open(os.path.join("", "app", ".config",  "db.key")) as f:
        db = f.readline().strip()
    return db


def init_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=get_app_key(),
        SQLALCHEMY_DATABAS_URI=f"sqlite:///{get_db()}"
    )

    from .routes import routes

    app.register_blueprint(routes, url_prefix="/")

    return app
