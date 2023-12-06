import datetime
import json
from sqlalchemy import select

from . import app
from . import db
from .models import Post, Comment


def get_posts(num: int=0, page: int=1):
    with app.app_context():
        posts = db.session.execute(
            select(Post)
            .order_by(Post.date.desc())
            .limit(None)
            .offset((page - 1) * num),
            execution_options={"prebuffer_rows": True}
        ).scalars().all()
    return _posts_to_list(posts)


def _posts_to_list(posts: Post):
    result = []
    for post in posts:
        result.append(post.to_dict())
    return result


def get_post(id):
    with app.app_context():
        post = db.session.execute(
            select(Post)
            .where(Post.id == id)
        ).scalar()
    return post.to_dict()


def add_post(
    author,
    title,
    subtitle,
    body,
    img_url
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
