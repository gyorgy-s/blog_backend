from flask import Blueprint, request, jsonify, make_response
from werkzeug.exceptions import BadRequest
from requests.exceptions import MissingSchema
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import UnmappedInstanceError

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
        return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
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
        return make_response(jsonify({"error": ["There are no posts."]}), 404)
    return make_response(jsonify(posts), 200)


@routes.route("/get-post")
def get_post():
    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
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
        return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
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
        return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
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

    return make_response({"success": ["Email successfully sent."]}, 200)


@routes.route("/about")
def about():
    return "about"


@routes.route("/create-post", methods=["POST"])
def create_post():
    necessary = ["author", "title", "subtitle", "body", "img_url"]
    errors = []

    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
    for param in necessary:
        if param not in req.keys():
            errors.append(f"Missing param: '{param}'")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    if not isinstance(req["author"], str):
        errors.append("'author' must be str.")
    if not isinstance(req["title"], str):
        errors.append("'title' must be str.")
    if not isinstance(req["subtitle"], str):
        errors.append("'subtitle' must be str.")
    if not isinstance(req["body"], str):
        errors.append("'body' must be str.")
    if not isinstance(req["img_url"], str):
        errors.append("'img_url' must be str.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    req["author"] = req["author"].strip()
    req["title"] = req["title"].strip()
    req["subtitle"] = req["subtitle"].strip()
    req["body"] = req["body"].strip()
    req["img_url"] = req["img_url"].strip()

    if not len(req["author"]) >= 2:
        errors.append("'author' must be at least 2 characters.")
    if not len(req["title"]) >= 5:
        errors.append("'title' must be at least 5 characters.")
    if not len(req["subtitle"]) >= 5:
        errors.append("'subtitle' must be at least 5 characters.")
    if not len(req["body"]) >= 5:
        errors.append("'body' must be at least 5 characters.")
    if not len(req["img_url"]) >= 2:
        errors.append("'img_url' must be at least 2 characters.")
    try:
        if not control.validate_img_url(req["img_url"]):
            errors.append("'img_url' is not a valid url for an image.")
    except MissingSchema:
        errors.append("'img_url' is not a valid url.")

    if errors:
        return make_response(jsonify({"error": errors}), 400)

    try:
        control.add_post(
            author=req["author"], title=req["title"], subtitle=req["subtitle"], body=req["body"], img_url=req["img_url"]
        )
    except IntegrityError as err:
        return make_response(jsonify({"error": err.args}))

    return make_response(jsonify({"success": ["Post has been added sucessfully."]}), 200)


@routes.route("/update-post", methods=["GET", "PATCH"])
def update_post():
    if request.method == "GET":
        if not request.is_json:
            return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
        try:
            req = request.get_json()
        except BadRequest:
            return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
        if "id" not in req.keys():
            return make_response(jsonify({"error": ["Missing param: 'id'"]}), 400)
        if not isinstance(req["id"], int):
            return make_response(jsonify({"error": ["'id' must be int."]}), 400)
        post = control.get_post(req["id"])
        if not post:
            return make_response(jsonify({"error": [f"There are no posts with the id of {req['id']}."]}), 404)
        return make_response(jsonify(post), 200)

    if request.method == "PATCH":
        necessary = ["id", "title", "subtitle", "body", "img_url"]
        errors = []

        if not request.is_json:
            return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
        try:
            req = request.get_json()
        except BadRequest:
            return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
        for param in necessary:
            if param not in req.keys():
                errors.append(f"Missing param: '{param}'")
        if errors:
            return make_response(jsonify({"error": errors}), 400)

        if not isinstance(req["id"], int):
            errors.append("'id' must be int.")
        if not isinstance(req["title"], str):
            errors.append("'title' must be str.")
        if not isinstance(req["subtitle"], str):
            errors.append("'subtitle' must be str.")
        if not isinstance(req["body"], str):
            errors.append("'body' must be str.")
        if req["img_url"]:
            if not isinstance(req["img_url"], str):
                errors.append("'img_url' must be str.")
        if errors:
            return make_response(jsonify({"error": errors}), 400)

        req["title"] = req["title"].strip()
        req["subtitle"] = req["subtitle"].strip()
        req["body"] = req["body"].strip()

        if not len(req["title"]) >= 5:
            errors.append("'title' must be at least 5 characters.")
        if not len(req["subtitle"]) >= 5:
            errors.append("'subtitle' must be at least 5 characters.")
        if not len(req["body"]) >= 5:
            errors.append("'body' must be at least 5 characters.")
        if req["img_url"]:
            req["img_url"] = req["img_url"].strip()
            if not len(req["img_url"]) >= 2:
                errors.append("'img_url' must be at least 2 characters.")
            try:
                if not control.validate_img_url(req["img_url"]):
                    errors.append("'img_url' is not a valid url for an image.")
            except MissingSchema:
                errors.append("'img_url' is not a valid url.")

        if errors:
            return make_response(jsonify({"error": errors}), 400)

        try:
            control.update_post(
                id=req["id"],
                title=req["title"],
                subtitle=req["subtitle"],
                body=req["body"],
                img_url=req["img_url"]
            )
        except IntegrityError as err:
            return make_response(jsonify({"error": err.args}))

        return make_response(jsonify({"success": ["Post has been updated sucessfully."]}), 200)


@routes.route("/delete-post", methods=["DELETE"])
def delete_post():
    if not request.is_json:
            return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
    if "id" not in req.keys():
        return make_response(jsonify({"error": ["Missing param: 'id'"]}), 400)
    if not isinstance(req["id"], int):
        return make_response(jsonify({"error": ["'id' must be int."]}), 400)
    try:
        control.delete_post(req["id"])
    except UnmappedInstanceError:
        return make_response(jsonify({"error":[f"There is no post with the 'id' of {req['id']}."]}), 404)
    return make_response(jsonify({"success": [f"Post with id: {req['id']} has been deleted sucessfully."]}), 200)


@routes.route("/add-comment", methods=["POST"])
def add_comment():
    necessary = ["author", "body", "post_id"]
    errors = []

    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
    for param in necessary:
        if param not in req.keys():
            errors.append(f"Missing param: '{param}'")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    if not isinstance(req["author"], str):
        errors.append("'author' must be str.")
    if not isinstance(req["body"], str):
        errors.append("'body' must be str.")
    if not isinstance(req["post_id"], int):
        errors.append("'post_id' must be int.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    req["author"] = req["author"].strip()
    req["body"] = req["body"].strip()

    if not len(req["author"]) >= 2:
        errors.append("'author' must be at least 2 characters.")
    if not len(req["body"]) >= 1:
        errors.append("'body' must be at least 1 characters.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)
    try:
        control.add_comment(req["author"], req["body"], req["post_id"])
    except SQLAlchemyError as err:
        return make_response(jsonify({"error": err.args}))
    return make_response(jsonify({"success": "Comment added successfully."}), 200)


@routes.route("/delete-comment", methods=["DELETE"])
def delete_comment():
    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
    if "comment_id" not in req.keys():
        return make_response(jsonify({"error": ["Missing param: 'comment_id'"]}), 400)

    if not isinstance(req["comment_id"], int):
        return make_response(jsonify({"error": "'comment_id' must be int."}), 400)
    try:
        control.delete_comment(req["comment_id"])
    except SQLAlchemyError as err:
        return make_response(jsonify({"error": err.args}))
    return make_response(jsonify({"success": "Comment deleted successfully."}), 200)


@routes.route("/edit-comment", methods=["PATCH"])
def edit_comment():
    necessary = ["comment_id", "body"]
    errors = []

    if not request.is_json:
        return make_response(jsonify({"error": ["Request must be in JSON format."]}), 400)
    try:
        req = request.get_json()
    except BadRequest:
        return make_response(jsonify({"error": ["Invalid JSON format."]}), 400)
    for param in necessary:
        if param not in req.keys():
            errors.append(f"Missing param: '{param}'")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    if not isinstance(req["comment_id"], int):
        errors.append("'comment_id' must be int.")
    if not isinstance(req["body"], str):
        errors.append("'body' must be str.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    req["body"] = req["body"].strip()

    if not len(req["body"]) >= 1:
        errors.append("'body' must be at least 1 characters.")
    if errors:
        return make_response(jsonify({"error": errors}), 400)

    try:
        control.edit_comment(comment_id=req["comment_id"], body=req["body"])
    except SQLAlchemyError as err:
        return make_response(jsonify({"error": err.args}), 404)
    return make_response(jsonify({"success": "Comment edited successfully."}), 200)
