from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from . import db

class Post(db.Model):
    __tablename__ = "posts"

    id = mapped_column(Integer, primary_key=True, unique=True)

    author = mapped_column(String(100), nullable=False)
    title = mapped_column(String(250), unique=True, nullable=False)
    subtitle = mapped_column(String(250), nullable=False)
    body = mapped_column(String(10000), nullable=False)
    date = mapped_column(DateTime(timezone=True), nullable=False)
    img_url = mapped_column(String(250), nullable=True)

    comments = relationship("Comment")

class Comment(db.Model):
    __tablename__ = "comments"

    id = mapped_column(Integer, primary_key=True, unique=True)
    post_id = mapped_column(Integer, ForeignKey("posts.id"))

    author = mapped_column(String(100), nullable=False)
    body = mapped_column(String(250), nullable=False)
    date = mapped_column(DateTime, nullable=False)
