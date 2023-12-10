import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy()

def get_app_key():
    with open(os.path.join("", "app", ".config",  "app.key")) as f:
        key = f.readline().strip()
    print("<SERVER><LOG> App key loaded.")
    return key

def get_db():
    with open(os.path.join("", "app", ".config",  "db.key")) as f:
        db = f.readline().strip()
    print("<SERVER><LOG> Db config loaded.")
    return db

def get_email_config():
    with open(os.path.join("", "app", ".config",  "email.key")) as f:
        email = f.readline().strip()
        email_key = f.readline().strip()
        to_email = f.readline().strip()
    print("<SERVER><LOG> Email config loaded.")
    return email, email_key, to_email

EMAIL, EMAIL_KEY, TO_EMAIL = get_email_config()

def init_app():
    app.config.update(
        SECRET_KEY=get_app_key(),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{get_db()}"
    )
    db.init_app(app)

    from .routes import routes
    app.register_blueprint(routes, url_prefix="/")

    with app.app_context():
        db.create_all()

    return app
