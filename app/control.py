"""
Module to interact with the db of the for the blog app.
Contains the implementation of the CRUD for the models,
and helper functions for validation and sending an email.
Format and data validation is handled in the routes module.
"""
import datetime

import re

from html import escape

import smtplib
from email.message import EmailMessage

import imghdr
import requests

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from . import app
from . import db
from . import EMAIL, EMAIL_KEY, TO_EMAIL
from .models import Post, Comment


def validate_bool(param):
    """Check if the given param is in the specified list of acceptable values for True or False.
    Returns bool according the evaluation of the param.
    Raises ValueError if the given param is not in the accepted lists."""
    is_true = [
        True,
        1,
        "true",
        "True",
        "t",
        "T"
    ]
    is_false = [
        False,
        0,
        "false",
        "False",
        "f",
        "F"
    ]
    if param in is_false:
        return False
    elif param in is_true:
        return True
    else:
        raise ValueError


def validate_email(email):
    """Check if the given email corresponds to the regex specified as a valid email format.
    Returns the email address or None if not a valid email address."""
    exp = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    email = re.fullmatch(exp, email)
    if not email:
        return None
    return email.string


def validate_img_url(img_url):
    """Check if the given url corresponds to an image.
    Returns the type of the image if any, None if not an image.
    Raises MissingSchema if the given url is not a valid url format."""
    img_type = imghdr.what("", requests.get(img_url, timeout=10).content)
    return img_type


def get_posts(num: int=0, page: int=1, comments: bool=False):
    """Get the posts from the db, depending on the given args as a list.
    num: the desired number of post to retrieve (if 0, get all posts). (>=0)
    page: pagination for the set of posts (if num not 0). Gives the offset for the querry. (>=1)
    comment: determines if the comments should be loaded for the posts, as a list.
    Returns a list of post object representet as a dict or none if there are no posts."""
    with app.app_context():
        if not num:
            if not comments:
                posts = db.session.execute(
                    select(Post)
                    .order_by(Post.date.desc()),
                    execution_options={"prebuffer_rows": True}
                ).scalars().all()
            else:
                posts = db.session.execute(
                    select(Post)
                    .options(joinedload(Post.comments))
                    .order_by(Post.date.desc()),
                    execution_options={"prebuffer_rows": True}
                ).scalars().unique()
        else:
            if not comments:
                posts = db.session.execute(
                    select(Post)
                    .order_by(Post.date.desc())
                    .limit(num)
                    .offset((page - 1) * num),
                    execution_options={"prebuffer_rows": True}
                ).scalars().all()
            else:
                posts = db.session.execute(
                    select(Post)
                    .options(joinedload(Post.comments))
                    .order_by(Post.date.desc())
                    .limit(num)
                    .offset((page - 1) * num),
                    execution_options={"prebuffer_rows": True}
                ).scalars().unique()
    if not posts:
        return None
    return _posts_to_list(posts, comments)


def _posts_to_list(posts: Post, comments: bool=False):
    """Helper to convert an iterable set of Post objects to a dict and collect them in a list.
    Returns a list of dict, empty list if there are no Posts."""
    result = []
    for post in posts:
        result.append(post.to_dict(comments))
    return result


#TODO decision, body {{img}} tag handling in backed or frontend
def get_post(id):
    """Get a single post from the db based on the id.
    When getting a specific post, the comments are loaded automatically.
    Returns a dict or None if there is no post by the given id."""
    with app.app_context():
        post = db.session.execute(
            select(Post)
            .options(joinedload(Post.comments))
            .where(Post.id == id)
        ).scalar()
    if not post:
        return None
    return post.to_dict(comm=True)


def get_posts_by_user(user, num: int=0, page: int=1):
    """Get all posts made by a specif user as a list.
    num: the desired number of post to retrieve (if 0, get all posts). (>=0)
    page: pagination for the set of posts (if num not 0). Gives the offset for the querry. (>=1)
    Returns a list of post object representet as a dict or none if there are no posts."""
    with app.app_context():
        if not num:
            posts = db.session.execute(
                select(Post)
                .where(Post.author == user)
                .order_by(Post.date.desc()),
                execution_options={"prebuffer_rows": True}
            ).scalars()
        else:
            posts = db.session.execute(
                select(Post)
                .where(Post.author == user)
                .order_by(Post.date.desc())
                .limit(num)
                .offset((page - 1) * num),
                execution_options={"prebuffer_rows": True}
            ).scalars()
    if not posts:
        return None
    return _posts_to_list(posts=posts, comments=False)


def send_contact_email(name, email, message):
    """Send an email to according to the email config, with the given contents."""
    msg = EmailMessage()
    msg["Subject"] = "TEST Our Blog message"
    msg["From"] = "me"
    msg["To"] = "Our Blog"
    msg.set_content(
        f"""
Dear Our Blog,

you have received a mail from {name} {email} !

"
{message}
"
"""
    )

    # TODO the sending of the mail has been commented out, no email will be sent
    # with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
    #     smtp.starttls()
    #     smtp.login(EMAIL, EMAIL_KEY)
    #     smtp.sendmail(EMAIL, TO_EMAIL, msg.as_string())


def add_post(
    author,
    title,
    subtitle,
    body,
    img_url=None
):
    """Create a new record for a post in the db, with the given params.
    Date is determined by the time of execution."""
    with app.app_context():
        post = Post(
            author=author,
            title=title,
            subtitle=subtitle,
            body=body,
            date=datetime.datetime.now(),
            img_url=img_url
        )
        db.session.add(post)
        db.session.commit()


def update_post(
        id:int,
        title:str,
        subtitle:str,
        body:str,
        img_url:str=None
):
    """Update an existing post with the given params based on the id.
    Date is updated to the time of execution."""
    if img_url:
        img_url = escape(img_url)
    with app.app_context():
        db.session.execute(
            update(Post),[{
                "id": id,
                "title": escape(title),
                "subtitle": escape(subtitle),
                "body": escape(body),
                "date":datetime.datetime.now(),
                "img_url": img_url,
            }]
        )
        db.session.commit()


def delete_post(id):
    """Delete a post from the db based on id."""
    with app.app_context():
        to_delete = db.session.execute(
            select(Post)
            .where(Post.id == id)
        ).scalar()
        db.session.delete(to_delete)
        db.session.commit()


def add_comment(
        author:str,
        body:str,
        post_id:int
):
    """Create a new record for a comment in the db, with the given params.
    Date is determined by the time of execution."""
    with app.app_context():
        comment = Comment(
            post_id=post_id,
            author=escape(author),
            body=escape(body),
            date=datetime.datetime.now()
        )
        db.session.add(comment)
        db.session.commit()


def delete_comment(comment_id):
    """Delete a comment from the db based on id."""
    with app.app_context():
        to_delete = db.session.execute(
            select(Comment)
            .where(Comment.id == comment_id)
        ).scalar()
        db.session.delete(to_delete)
        db.session.commit()


def edit_comment(comment_id, body):
    """Update an existing comment with the given params based on the id.
    Date is updated to the time of execution."""
    with app.app_context():
        db.session.execute(
            update(Comment),[{
                "id": comment_id,
                "body": escape(body),
                "date":datetime.datetime.now()
            }]
        )
        db.session.commit()
