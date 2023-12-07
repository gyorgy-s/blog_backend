from flask import Blueprint, request, jsonify, make_response

from . import control

routes = Blueprint("routes", __name__)


@routes.route("/")
def home():
    return "Home is where the heart is."


@routes.route("/get-posts")
def get_posts():
    num = 0
    page = 1
    comments = True
    try:
        if request.args.get("num"):
            num = int(request.args.get("num"))
    except ValueError:
        response = make_response({"error": ["Value given for 'num' is not accepted, expecting: int."]}, 400)
    else:
        try:
            if request.args.get("page"):
                page = int(request.args.get("page"))
                if page < 1:
                    page = 1
        except ValueError:
            response = make_response({"error": ["Value given for 'page' is not accepted, expecting: int."]}, 400)
        else:
            try:
                if request.args.get("comments"):
                    comments = control.validate_bool(request.args.get("comments"))
            except ValueError:
                response = make_response(
                    {"error": ["Value given for 'comments' is not accepted, expecting: boolean."]}, 400
                )

            else:
                posts = control.get_posts(num=num, page=page, comments=comments)
                if not posts:
                    response = make_response(
                        {"error": [f"There are no post in the range of num:{num}, page: {page}."]}, 404
                    )
                else:
                    response = make_response(jsonify(posts), 200)
    return response


@routes.route("/get-post")
def get_post():
    if not request.args.get("id"):
        response = make_response({"error": ["Missing parameter 'id'."]}, 400)
    else:
        try:
            id = int(request.args.get("id"))
        except ValueError:
            make_response({"error": ["Value given for 'id' is not accepted."]}, 400)
        else:
            post = control.get_post(id)
            if not post:
                response = make_response({"error": [f"There is no post with the 'id': {id}."]}, 404)
            else:
                response = make_response(jsonify(post), 200)
    return response


@routes.route("/get-posts-by-user")
def get_posts_by_user():
    num = 0
    page = 1
    if not request.args.get("user"):
        response = make_response({"error": ["Missing parameter 'user'."]}, 400)
    else:
        user = request.args.get("user")
        try:
            if request.args.get("num"):
                num = int(request.args.get("num"))
        except ValueError:
            response = make_response({"error": ["Value given for 'num' is not accepted, expecting: int."]}, 400)
        else:
            try:
                if request.args.get("page"):
                    page = int(request.args.get("page"))
                    if page < 1:
                        page = 1
            except ValueError:
                response = make_response({"error": ["Value given for 'page' is not accepted, expecting: int."]}, 400)
            else:
                posts = control.get_posts_by_user(user=user, num=num, page=page)
                if not posts:
                    if page == 1:
                        response = make_response({"error": [f"There is no post made by {user}."]}, 404)
                    else:
                        response = make_response(
                            {"error": [f"There is no post made by {user} in the range of num:{num}, page: {page}."]},
                            404,
                        )

                else:
                    response = make_response(jsonify(posts), 200)
    return response


@routes.route("/contact", methods=["POST"])
def contact():
    name = request.args.get("name")
    email = request.args.get("email")
    message = request.args.get("message")

    if not name:
        return make_response({"error": ["Missing param 'name'."]}, 400)
    name = name.strip()
    if not email:
        return make_response({"error": ["Missing param 'email'."]}, 400)
    email = email.strip()
    if not message:
        return make_response({"error": ["Missing param 'message'."]}, 400)
    email = control.validate_email(email.strip())
    if not email:
        return make_response({"error": ["This is not a valid email address."]}, 400)

    control.send_contact_email(name=name, email=email, message=message)

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
