import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

def get_app_key():
    with open(os.path.join("", "app", ".config",  "app.key")) as f:
        key = f.readline().strip()
    return key

def get_db():
    with open(os.path.join("", "app", ".config",  "db.key")) as f:
        db = f.readline().strip()
    return db


def init_app():
    app.config.update(
        SECRET_KEY=get_app_key(),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{get_db()}"
    )
    db.init_app(app)

    from .routes import routes
    app.register_blueprint(routes, url_prefix="/")

    from .models import Post, Comment
    with app.app_context():
        db.create_all()


    return app
