from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, EmailField, SubmitField, SelectField, IntegerField

from wtforms.validators import DataRequired, Length, equal_to, NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed


class RegisterForm(FlaskForm):
    profile_image = FileField("Upload a Profile Picture", validators=[DataRequired()])
    username = StringField("Enter Username", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Enter Email Address", validators=[DataRequired()])
    password = PasswordField("Enter Password", validators=[DataRequired(), Length(min=8, max=64)])
    repeat_password = PasswordField("Repeat Password", validators=[DataRequired(), equal_to("password")])
    register = SubmitField("Sign Up")
    edit = SubmitField("Edit User")

class LoginForm(FlaskForm):
    username = StringField("Enter username", validators=[DataRequired()])
    password = PasswordField("Enter password", validators=[DataRequired(), Length(min=8, max=64)])

    login = SubmitField("Log in")


class AddPost(FlaskForm):
    image = FileField("Upload a picture/video", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'], 'Images and videos only!'), DataRequired()])
    title = StringField("Title of the post", validators=[DataRequired()])
    description = StringField("Enter the description", validators=[DataRequired()])
    target = SelectField(choices=["This drill targets...","Skills & Performance", "Shooting", "Defense & Strategy", "Game Situations & Tactics", "Health, Nutritioning & Recovery", "Equipment & Analysis", "Other"], validators=[DataRequired()])
    add = SubmitField("Create Post")
    edit = SubmitField("Edit Post")


class RatingForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Rate')


class CommentForm(FlaskForm):
    comment = StringField("Add a comment", validators=[DataRequired()])
    submit = SubmitField('Comment')

class AddReadPost(FlaskForm):
    title = StringField("Enter the title of the post", validators=[DataRequired()])
    text = StringField("Enter the text/advice you want to share", validators=[DataRequired()])
    target = SelectField(choices=["This post is about...", "Player Mindset & Motivation", "Training & Improvement", "Game Experience & Situational Awareness","Coaching & Team Dynamics", "Nutritioning, Recovery & Physical Health","Career & Growth Advice", "Other"], validators=[DataRequired()])
    add = SubmitField("Create Post")


class AddReview(FlaskForm):
    review = StringField("Add a review or report a problem", validators=[DataRequired()])
    add = SubmitField("Add")