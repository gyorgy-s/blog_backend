from flask import Blueprint, jsonify

from . import control

routes = Blueprint("routes", __name__)


@routes.route("/")
def home():
    return "This is home"


@routes.route("/get-posts")
def get_posts():
    posts = control.get_posts()
    return jsonify(posts)


@routes.route("/get-post")
def get_post():
    return "get-post"


@routes.route("/get-posts-by-user")
def get_posts_by_user():
    return "get-posts-by-user"


@routes.route("/contact")
def contact():
    return "contact"


@routes.route("/about")
def about():
    return "about"


@routes.route("/create-post")
def create_post():
    return "create-post"


@routes.route("/update-post")
def update_post():
    return "update-post"


@routes.route("/delete-post")
def delete_post():
    return "delete-post"
