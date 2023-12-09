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
    exp = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    email = re.fullmatch(exp, email)
    if not email:
        return None
    return email.string

def validate_img_url(img_url):
    img_type = imghdr.what("", requests.get(img_url, timeout=10).content)
    return img_type


def get_posts(num: int=0, page: int=1, comments: bool=False):
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
    result = []
    for post in posts:
        result.append(post.to_dict(comments))
    return result


#TODO decision, body {{img}} tag handling in backed or frontend
def get_post(id):
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
    with app.app_context():
        comment = Comment(
            post_id=post_id,
            author=escape(author),
            body=escape(body),
            date=datetime.datetime.now()
        )
        db.session.add(comment)
        db.session.commit()
