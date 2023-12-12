"""
Initialize the backend:
get the app secret key, database name and email configuration from the designed
files when called.
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy()

def get_app_key():
    """Get the app key from file, the key is loaded from the first line of the file.
    Returns the key."""
    with open(os.path.join("", "app", ".config",  "app.key")) as f:
        key = f.readline().strip()
    print("<SERVER><LOG> App key loaded.")
    return key

def get_db():
    """Get the db name from file, the name is loaded from the first line of the file.
    Returns the db."""
    with open(os.path.join("", "app", ".config",  "db.key")) as f:
        db = f.readline().strip()
    print("<SERVER><LOG> Db config loaded.")
    return db

def get_email_config():
    """Get the email config from file, reads the email, email password and recipient
    each as a line form the file in this order.
    Returns a tuple of (emial, email password, recipient email)."""
    with open(os.path.join("", "app", ".config",  "email.key")) as f:
        email = f.readline().strip()
        email_key = f.readline().strip()
        to_email = f.readline().strip()
    print("<SERVER><LOG> Email config loaded.")
    return email, email_key, to_email

# Stored email config for other modules.
EMAIL, EMAIL_KEY, TO_EMAIL = get_email_config()

def init_app():
    """Initialize the app, load the blueprints for the routes and create the db.
    The db is created only if it does not exist.
    Returns the app."""
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
