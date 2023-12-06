import os
from flask import Flask


def get_app_key():
    with open(os.path.join("", "app", "app.key")) as f:
        key = f.readline()
    return key


def init_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=get_app_key(),
        SQLALCHEMY_DATABAS_URI="sqlite:///blog.db"
    )

    return app
