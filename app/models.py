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

    #TODO add comments
    def to_dict(self):
        result = {
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "subtitle": self.subtitle,
            "body": self.body,
            "date": self.date,
            "img_url": self.img_url,
        }
        return result

class Comment(db.Model):
    __tablename__ = "comments"

    id = mapped_column(Integer, primary_key=True, unique=True)
    post_id = mapped_column(Integer, ForeignKey("posts.id"))

    author = mapped_column(String(100), nullable=False)
    body = mapped_column(String(250), nullable=False)
    date = mapped_column(DateTime, nullable=False)


    def to_dict(self):
        result = {
            "id": self.id,
            "post_id": self.post_id,
            "author": self.author,
            "body": self.body,
            "date": self.date,
        }
        return result
