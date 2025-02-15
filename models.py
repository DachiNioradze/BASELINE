from ext import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
class Post(db.Model):

    __tablename__ = "posts"

    id = db.Column(db.Integer(), primary_key=True)
    image_path = db.Column(db.String())
    title = db.Column(db.String())
    description = db.Column(db.String())
    target = db.Column(db.String())

    author = db.Column(db.String())
    author_profile = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReadPost(db.Model):

    __tablename__ = "read_posts"
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    text = db.Column(db.String())
    target = db.Column(db.String())
    author_username = db.Column(db.String())
    author_first_name = db.Column(db.String())
    author_last_name = db.Column(db.String())
    author_profile = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String())
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String())
    path = db.Column(db.String())
    role = db.Column(db.String())

    def __init__(self, path, username, first_name, last_name, email, password, role="Guest"):
        self.path = path
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



class Rating(db.Model):

    __tablename__ = "ratings"

    id = db.Column(db.Integer(), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer(), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_rating'),)



class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer(), primary_key=True)
    post_id = db.Column(db.Integer(), nullable=False)
    comment = db.Column(db.String(), nullable=False)
    author = db.Column(db.String())
    comment_author_profile = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer(), db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

class Dislike(db.Model):
    __tablename__ = "dislikes"

    id = db.Column(db.Integer(), primary_key=True)
    post_id = db.Column(db.Integer(), db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))





class ReadComment(db.Model):

    __tablename__ = "read_comments"

    id = db.Column(db.Integer, primary_key=True)
    read_post_id = db.Column(db.Integer(), nullable=False)
    read_comment = db.Column(db.String(), nullable=False)
    read_author = db.Column(db.String())
    read_comment_author_profile = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReadLike(db.Model):

    __tablename__ = "read_likes"

    id = db.Column(db.Integer, primary_key=True)
    read_post_id = db.Column(db.Integer(), db.ForeignKey('read_posts.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

class ReadDislike(db.Model):

    __tablename__ = "read_dislikes"

    id = db.Column(db.Integer, primary_key=True)
    read_post_id = db.Column(db.Integer(), db.ForeignKey('read_posts.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))


class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(db.Integer(), primary_key=True)
    review = db.Column(db.String())
    author_username = db.Column(db.String())
    author_first_name = db.Column(db.String())
    author_last_name = db.Column(db.String())
    author_profile = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class Event(db.Model):

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    title_one = db.Column(db.Text, nullable=False)
    text_one = db.Column(db.Text, nullable=False)
    title_two = db.Column(db.Text, nullable=False)
    text_two = db.Column(db.Text, nullable=False)
    title_three = db.Column(db.Text, nullable=False)
    text_three = db.Column(db.Text, nullable=False)
    title_four = db.Column(db.Text, nullable=False)
    text_four = db.Column(db.Text, nullable=False)
    read_more = db.Column(db.Text, nullable=False)

