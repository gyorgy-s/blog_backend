"""
Module for the db models of the blog app.
Define the db tables and relations within to store the blog posts and comments.
"""
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from . import db


class Post(db.Model):
    """Db table for posts. Defines the desired columns of the table and relations."""
    __tablename__ = "posts"

    id = mapped_column(Integer, primary_key=True, unique=True)

    author = mapped_column(String(100), nullable=False)
    title = mapped_column(String(250), unique=True, nullable=False)
    subtitle = mapped_column(String(250), nullable=False)
    body = mapped_column(String(10000), nullable=False)
    date = mapped_column(DateTime(timezone=True), nullable=False)
    img_url = mapped_column(String(250), nullable=True)

    comments = relationship("Comment", cascade="all, delete-orphan")


    def to_dict(self, comm: bool=False):
        """Convert a Post object to a dict for representation.
        If 'comm' param is True the dict will contain all the comments
        belonging to the post in a [{},{}] format."""
        if comm:
            comments = []
            if self.comments:
                for comment in self.comments:
                    comments.append(comment.to_dict())
            result = {
                "id": self.id,
                "author": self.author,
                "title": self.title,
                "subtitle": self.subtitle,
                "body": self.body,
                "date": self.date,
                "img_url": self.img_url,
                "comments": comments,
            }
        else:
            result = {
                "id": self.id,
                "author": self.author,
                "title": self.title,
                "subtitle": self.subtitle,
                "body": self.body,
                "date": self.date,
                "img_url": self.img_url,
                "comments": [],
            }
        return result

class Comment(db.Model):
    """Db table for comments. Defines the desired columns of the table and relations."""
    __tablename__ = "comments"

    id = mapped_column(Integer, primary_key=True, unique=True)
    post_id = mapped_column(Integer, ForeignKey("posts.id"))

    author = mapped_column(String(100), nullable=False)
    body = mapped_column(String(250), nullable=False)
    date = mapped_column(DateTime, nullable=False)


    def to_dict(self):
        """Convert Comment object to a dict for representation."""
        result = {
            "id": self.id,
            "post_id": self.post_id,
            "author": self.author,
            "body": self.body,
            "date": self.date,
        }
        return result
