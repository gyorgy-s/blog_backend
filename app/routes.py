from flask import Blueprint, request, jsonify, make_response

from . import control

routes = Blueprint("routes", __name__)


@routes.route("/")
def home():
    return "This is home"


@routes.route("/get-posts")
def get_posts():
    num = 0
    page = 1
    try:
        if request.args.get("num"):
            num = int(request.args.get("num"))
        if request.args.get("page"):
            page = int(request.args.get("page"))
    except ValueError:
        response = make_response({
            "error": "Value given for 'num' or 'page' is not accepted."
        }, 400)
    else:
        posts = control.get_posts(num=num, page=page)
        if not posts:
            response = make_response({
                "error": [
                    f"There are no post in the range of num:{num}, page: {page}."
                ]
            }, 404)
        else:
            response = make_response(jsonify(posts), 200)
    return response


@routes.route("/get-post")
def get_post():
    if not request.args.get("id"):
        response = make_response({
            "error":[
                "Missing parameter 'id'."
            ]
        }, 400)
    else:
        try:
            id = int(request.args.get("id"))
        except ValueError:
            make_response({
                "error":[
                    "Value given for 'id' is not accepted."
                ]
            }, 400)
        else:
            post = control.get_post(id)
            if not post:
                response = make_response({
                    "error":[
                        f"There is no post with the 'id': {id}."
                    ]
                }, 404)
            else:
                response = make_response(jsonify(post), 200)
    return response


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
