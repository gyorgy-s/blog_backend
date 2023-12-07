from flask import Blueprint, request, jsonify, make_response
from werkzeug.exceptions import BadRequest
from requests.exceptions import MissingSchema
from sqlalchemy.exc import IntegrityError

from . import control

routes = Blueprint("routes", __name__)


@routes.route("/")
def home():
    return "Home is where the heart is."


@routes.route("/get-posts", methods=["GET"])
def get_posts():
    necessary = ["num", "page", "comments"]
    errors = []

    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}))
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}))
    for param in necessary:
        if param not in req.keys():
            errors.append(f"Missing param: '{param}'")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    if not isinstance(req["comments"], bool):
        errors.append("'comments' must be boolean.")
    if not isinstance(req["num"], int):
        errors.append("'num' must be int.")
    if not isinstance(req["page"], int):
        errors.append("'page' must be int.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    if not req["num"] >= 0:
        errors.append(f"'num' must be >= 0")
    if not req["page"] >= 1:
        errors.append(f"'page' must be >= 1")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    posts = control.get_posts(num=req["num"], page=req["page"], comments=req["comments"])
    if not posts:
        if req["num"] != 0 and req["page"] != 1:
            return make_response(
                jsonify({"error": [f"There are no posts in the range of num: {req['num']}, page: {req['page']}"]}), 404
            )
        return make_response(jsonify({"error": [f"There are no posts."]}), 404)
    return make_response(jsonify(posts), 200)


@routes.route("/get-post")
def get_post():
    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}))
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}))
    if "id" not in req.keys():
        return make_response(jsonify({"error": ["Missing param: 'id'"]}), 400)
    if not isinstance(req["id"], int):
        return make_response(jsonify({"error": ["'id' must be int."]}), 400)
    post = control.get_post(req["id"])
    if not post:
        return make_response(jsonify({"error": [f"There are no posts with the id of {req['id']}."]}), 404)
    return make_response(jsonify(post), 200)


@routes.route("/get-posts-by-user")
def get_posts_by_user():
    necessary = ["user", "num", "page"]
    errors = []

    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}))
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}))
    for param in necessary:
        if param not in req.keys():
            errors.append(f"Missing param: '{param}'")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    if not isinstance(req["user"], str):
        errors.append("'user' must be str.")
    if not isinstance(req["num"], int):
        errors.append("'num' must be int.")
    if not isinstance(req["page"], int):
        errors.append("'page' must be int.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    req["user"] = req["user"].strip()
    if not len(req["user"]) >= 2:
        errors.append("'user' must be at least 2 characters.")
    if not req["num"] >= 0:
        errors.append("'num' must be >= 0")
    if not req["page"] >= 1:
        errors.append("'page' must be >= 1")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    posts = control.get_posts_by_user(user=req["user"], num=req["num"], page=req["page"])
    if not posts:
        if req["num"] != 0 and req["page"] != 1:
            return make_response(
                jsonify(
                    {
                        "error": [
                            f"There is no post made by {req['user']} in the range of num: {req['num']}, page: {req['page']}"
                        ]
                    }
                ),
                404,
            )
        return make_response(jsonify({"error": [f"There is no post made by {req['user']}."]}), 404)
    return make_response(jsonify(posts), 200)


@routes.route("/contact", methods=["POST"])
def contact():
    necessary = ["name", "email", "message"]
    errors = []

    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}))
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}))
    for param in necessary:
        if param not in req.keys():
            errors.append(f"Missing param: '{param}'")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    if not isinstance(req["name"], str):
        errors.append("'name' must be str.")
    if not isinstance(req["email"], str):
        errors.append("'email' must be str.")
    if not isinstance(req["message"], str):
        errors.append("'message' must be str.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    req["name"] = req["name"].strip()
    req["email"] = req["email"].strip()
    req["message"] = req["message"].strip()

    if not len(req["name"]) >= 2:
        errors.append("'name' must be at least 2 characters.")
    if not len(req["message"]) >= 2:
        errors.append("'message' must be at least 2 characters.")
    email = control.validate_email(req["email"].strip())
    if not email:
        errors.append("'email' is not a valid email address.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)
    control.send_contact_email(name=req["name"], email=email, message=req["message"])

    return make_response({"success": ["Email successfully sent."]})


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
