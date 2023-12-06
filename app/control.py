import datetime
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from . import app
from . import db
from .models import Post, Comment


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


def get_post(id):
    with app.app_context():
        post = db.session.execute(
            select(Post)
            .options(joinedload(Post.comments))
            .where(Post.id == id)
        ).scalar()
    if not post:
        return None
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
