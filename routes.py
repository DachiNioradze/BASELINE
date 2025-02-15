from flask import render_template, redirect, flash
from flask_login import login_user, logout_user, current_user, login_required
from forms import RegisterForm, LoginForm, AddPost, CommentForm, RatingForm, AddReadPost, AddReview
from models import Post, User, Comment, Rating, Like, Dislike, ReadPost, ReadLike, ReadDislike, ReadComment, Review, Event
from ext import app, db
from werkzeug.security import generate_password_hash

from sqlalchemy.sql import func
import humanize
from datetime import datetime
import re
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = AddPost()
    if form.validate_on_submit():
        if form.target.data == "This drill targets...":
            flash("Please select a valid target!", "danger")
            return redirect("/upload")

        if form.image.data:
            image = form.image.data
            image_path = f"{app.root_path}\static\{image.filename}"
            image.save(image_path)

            author_profile = current_user.path


            new_post = Post(image_path=image.filename, title=form.title.data, description=form.description.data, target=form.target.data, author=current_user.username, author_profile=author_profile)
            db.session.add(new_post)
            db.session.commit()

        return redirect("/view_content")



    return render_template("upload.html", form=form)

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(User.username == form.username.data).first()
        if existing_user is None:
            if form.profile_image.data:
                profile_image = form.profile_image.data
                path = f"{app.root_path}\static\{profile_image.filename}"
                profile_image.save(path)
                new_user = User(path=profile_image.filename, username=form.username.data, first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=form.password.data)
                db.session.add(new_user)
                db.session.commit()

                return redirect("/login")
        else:
            form.username.errors.append("Username already exists. Please choose a different one.")
        """
        if form.profile_image.data:
            image = form.profile_image.data
            image.save(f"{app.root_path}\static\{image.filename}")
            new_user['profile_image'] = image.filename
        """
    return render_template("register.html", form=form)


@app.route("/registered_users")
@login_required
def users():
    registered_users = User.query.all()
    return render_template("registered_users.html", registered_users=registered_users)


@app.route("/edit_users/<int:user_id>", methods=["GET", "POST"])
def edit_users(user_id):
    user = User.query.get(user_id)
    form = RegisterForm(username=user.username, first_name=user.first_name, last_name=user.last_name, email=user.email)
    if form.validate_on_submit():
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.password = generate_password_hash(form.password.data)

        if form.profile_image.data:
            profile_image = form.profile_image.data
            path = f"{app.root_path}\static\{profile_image.filename}"
            profile_image.save(path)
            user.path = profile_image.filename
        db.session.commit()
        return redirect("/registered_users")

    return render_template("edit_user.html", form=form)

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    user = User.query.get(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/registered_users")

@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get(post_id)
    form = AddPost(title=post.title, description=post.description, target=post.target)
    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        post.target = form.target.data

        if form.image.data:
            image = form.image.data
            image_path = f"{app.root_path}\static\{image.filename}"
            image.save(image_path)
            post.image_path = image.filename

        post.edited_at = datetime.utcnow()
        db.session.commit()
        return redirect("/view_content")



    return render_template("edit_post.html", form=form)

@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    post = Post.query.get(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect("/view_content")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/content")

    return render_template("login.html", form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

@app.route("/content")
@login_required
def content():
    return render_template("content.html")

@app.route("/view_content")
@login_required
def view_content():
    posts = Post.query.all()

    for post in posts:
        post.time_ago = humanize.naturaltime(datetime.utcnow() - post.created_at)
        post.edited_time_ago = humanize.naturaltime(datetime.utcnow() - post.edited_at) if post.edited_at else 'Not Edited'
    return render_template("view_content.html", posts=posts)

@app.route("/post/<int:post_id>", methods = ["GET", "POST"])
@login_required
def post(post_id):
    def split_into_paragraphs(text, sentences_per_paragraph=6):
        if not text:
            return []

        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        paragraphs = [
            " ".join(sentences[i:i + sentences_per_paragraph])
            for i in range(0, len(sentences), sentences_per_paragraph)
        ]

        return paragraphs

    post = Post.query.get(post_id)

    formatted_paragraphs = split_into_paragraphs(post.description)

    rating_form = RatingForm()
    if rating_form.validate_on_submit():
        existing_rating = Rating.query.filter_by(post_id=post.id, user_id=current_user.id).first()

        if existing_rating:
            flash("You have already rated this post!", "warning")
        else:
            rating = Rating(post_id=post.id, user_id=current_user.id, rating=rating_form.rating.data)
            db.session.add(rating)
            db.session.commit()
            flash("Your rating has been submitted!", "success")

        return redirect(f"/post/{post.id}")

    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment_author_profile = current_user.path

        comment = Comment(post_id=post.id, comment=comment_form.comment.data, author=current_user.username, comment_author_profile=comment_author_profile)
        db.session.add(comment)
        db.session.commit()

        return redirect(f"/post/{post.id}")

    comments = Comment.query.filter_by(post_id=post_id).all()
    comment_count = Comment.query.filter_by(post_id=post_id).count()
    rating_count = Rating.query.filter_by(post_id=post_id).count()
    like_count = Like.query.filter_by(post_id=post_id).count()
    dislike_count = Dislike.query.filter_by(post_id=post_id).count()

    helpful_ratings = Rating.query.filter(Rating.post_id == post_id, Rating.rating >= 3).count()
    helpful_percentage = (helpful_ratings/rating_count) * 100 if rating_count > 0 else 0

    avg_rating = db.session.query(func.avg(Rating.rating)).filter(Rating.post_id == post_id).scalar()
    avg_rating = round(avg_rating, 2) if avg_rating else 'N/A'

    time_ago = humanize.naturaltime(datetime.utcnow() - post.created_at)
    edited_time_ago = humanize.naturaltime(datetime.utcnow() - post.edited_at)

    if comments:
        for comment in comments:
            comment_time_ago = humanize.naturaltime(datetime.utcnow() - comment.created_at)
            comment_edited_time_ago = humanize.naturaltime(datetime.utcnow() - comment.edited_at)
    else:
        comment_time_ago = ""
        comment_edited_time_ago = ""

    return render_template("post.html", post=post, formatted_paragraphs=formatted_paragraphs, helpful_percentage=helpful_percentage, rating_form=rating_form, comment_form=comment_form, avg_rating=avg_rating, comments=comments, comment_count=comment_count, rating_count=rating_count, like_count=like_count, dislike_count=dislike_count, time_ago=time_ago, edited_time_ago=edited_time_ago, comment_time_ago=comment_time_ago, comment_edited_time_ago=comment_edited_time_ago)






@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if existing_like is None:
        like = Like(post_id=post_id, user_id=current_user.id)
        db.session.add(like)

        existing_dislike = Dislike.query.filter_by(post_id=post_id, user_id=current_user.id).first()
        if existing_dislike:
            db.session.delete(existing_dislike)
        db.session.commit()
    else:
        db.session.delete(existing_like)
        db.session.commit()
    return redirect(f"/post/{post_id}")


@app.route('/dislike/<int:post_id>', methods=['POST'])
def dislike_post(post_id):
    existing_dislike = Dislike.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if existing_dislike is None:
        dislike = Dislike(post_id=post_id, user_id=current_user.id)
        db.session.add(dislike)

        existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
        if existing_like:
            db.session.delete(existing_like)
        db.session.commit()

    else:
        db.session.delete(existing_dislike)
        db.session.commit()
    return redirect(f"/post/{post_id}")




@app.route("/filter")
def filter():
    return render_template("filter.html")

@app.route("/filter/<goal>")
def filtered_products(goal):
    posts = Post.query.filter_by(target=goal).all()
    for post in posts:
        post.time_ago = humanize.naturaltime(datetime.utcnow() - post.created_at)
        post.edited_time_ago = humanize.naturaltime(datetime.utcnow() - post.edited_at) if post.edited_at else 'Not Edited'
    return render_template("filtered_posts.html", posts=posts, goal=goal)

@app.route("/filter_text_posts")
def filter_text_posts():
    return render_template("filter_text_posts.html")

@app.route("/filter_text_posts/<about>")
def filtered_text_posts(about):
    read_posts = ReadPost.query.filter_by(target=about).all()
    for read_post in read_posts:
        read_post.comment_count = ReadComment.query.filter_by(read_post_id=read_post.id).count()
        read_post.like_count = ReadLike.query.filter_by(read_post_id=read_post.id).count()
        read_post.formatted_time = read_post.created_at.strftime("%I:%M %p, %b %d %Y")
        read_post.formatted_edited_at = read_post.edited_at.strftime("%I:%M %p, %b %d %Y")
    return render_template("filtered_text_posts.html", read_posts=read_posts, about=about)



@app.route("/delete_comment/<int:comment_id>")
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()

    return redirect(f"/post/{post_id}")

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comments(comment_id):
    comment = Comment.query.get(comment_id)
    post_id = comment.post_id
    form = CommentForm(comment=comment.comment)
    if form.validate_on_submit():
        comment.comment = form.comment.data
        comment.edited_at = datetime.utcnow()
        db.session.commit()
        return redirect(f"/post/{post_id}")

    return render_template("edit_comment.html", comment_form=form)





@app.route("/upload_text_post", methods=["GET", "POST"])
def upload_text_post():
    form = AddReadPost()
    if form.validate_on_submit():
        if form.target.data == "This post is about...":
            flash("Please select a valid target!", "danger")
            return redirect("/upload_text_post")
        author_profile = current_user.path

        new_read_post = ReadPost(title=form.title.data, text=form.text.data, target=form.target.data, author_username=current_user.username, author_first_name=current_user.first_name, author_last_name=current_user.last_name, author_profile=author_profile)
        db.session.add(new_read_post)
        db.session.commit()

        return redirect("/read_content")

    return render_template("upload_text_post.html", form=form)

@app.route("/read_content")
def read_content():
    read_posts = ReadPost.query.all()

    for read_post in read_posts:
        read_post.comment_count = ReadComment.query.filter_by(read_post_id=read_post.id).count()
        read_post.like_count = ReadLike.query.filter_by(read_post_id=read_post.id).count()
        read_post.formatted_time = read_post.created_at.strftime("%I:%M %p, %b %d %Y")
        read_post.formatted_edited_at = read_post.edited_at.strftime("%I:%M %p, %b %d %Y")

    return render_template("read_content.html", read_posts=read_posts)


@app.route("/read_post/<int:read_post_id>", methods=["GET", "POST"])
def read_post(read_post_id):
    def split_into_paragraphs(text, sentences_per_paragraph=5):
        if not text:
            return []

        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        paragraphs = [
            " ".join(sentences[i:i + sentences_per_paragraph])
            for i in range(0, len(sentences), sentences_per_paragraph)
        ]

        return paragraphs

    read_post = ReadPost.query.get(read_post_id)

    formatted_paragraphs = split_into_paragraphs(read_post.text)

    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        read_comment_author_profile = current_user.path

        read_comment = ReadComment(read_post_id=read_post.id, read_comment=comment_form.comment.data, read_author=current_user.username,
                          read_comment_author_profile=read_comment_author_profile)
        db.session.add(read_comment)
        db.session.commit()

        return redirect(f"/read_post/{read_post.id}")

    read_comments = ReadComment.query.filter_by(read_post_id=read_post_id).all()
    comment_count = ReadComment.query.filter_by(read_post_id=read_post_id).count()

    like_count = ReadLike.query.filter_by(read_post_id=read_post_id).count()
    dislike_count = ReadDislike.query.filter_by(read_post_id=read_post_id).count()

    formatted_time = read_post.created_at.strftime("%I:%M %p, %b %d %Y")
    formatted_edited_at = read_post.edited_at.strftime("%I:%M %p, %b %d %Y")

    if read_comments:
        for read_comment in read_comments:
            read_comment_time_ago = humanize.naturaltime(datetime.utcnow() - read_comment.created_at)
            read_comment_edited_time_ago = humanize.naturaltime(datetime.utcnow() - read_comment.edited_at)
    else:
        read_comment_time_ago = ""
        read_comment_edited_time_ago = ""


    return render_template("read_post.html", read_post=read_post,formatted_paragraphs=formatted_paragraphs,
                           comment_form=comment_form,comments=read_comments,
                           comment_count=comment_count, like_count=like_count,
                           dislike_count=dislike_count, formatted_time=formatted_time,formatted_edited_at=formatted_edited_at, read_comment_time_ago=read_comment_time_ago, read_comment_edited_time_ago=read_comment_edited_time_ago)

@app.route("/like_read_post/<int:read_post_id>", methods=['POST'])
def like_read_post(read_post_id):
    existing_like = ReadLike.query.filter_by(read_post_id=read_post_id, user_id=current_user.id).first()
    if existing_like is None:
        read_like = ReadLike(read_post_id=read_post_id, user_id=current_user.id)
        db.session.add(read_like)

        existing_dislike = ReadDislike.query.filter_by(read_post_id=read_post_id, user_id=current_user.id).first()
        if existing_dislike:
            db.session.delete(existing_dislike)
        db.session.commit()
    else:
        db.session.delete(existing_like)
        db.session.commit()
    return redirect(f"/read_post/{read_post_id}")

@app.route('/dislike_read_post/<int:read_post_id>', methods=['POST'])
def dislike_read_post(read_post_id):
    existing_dislike = ReadDislike.query.filter_by(read_post_id=read_post_id, user_id=current_user.id).first()
    if existing_dislike is None:
        read_dislike = ReadDislike(read_post_id=read_post_id, user_id=current_user.id)
        db.session.add(read_dislike)

        existing_like = ReadLike.query.filter_by(read_post_id=read_post_id, user_id=current_user.id).first()
        if existing_like:
            db.session.delete(existing_like)
        db.session.commit()

    else:
        db.session.delete(existing_dislike)
        db.session.commit()
    return redirect(f"/read_post/{read_post_id}")







@app.route('/edit_read_comment/<int:read_comment_id>', methods=['GET','POST'])
def edit_read_comment(read_comment_id):
    read_comment = ReadComment.query.get(read_comment_id)
    post_id = read_comment.read_post_id
    form = CommentForm(comment=read_comment.read_comment)
    if form.validate_on_submit():
        read_comment.read_comment = form.comment.data
        read_comment.edited_at = datetime.utcnow()
        db.session.commit()
        return redirect(f"/read_post/{post_id}")

    return render_template("edit_comment.html", comment_form=form)


@app.route('/delete_read_comment/<int:read_comment_id>')
def delete_read_comment(read_comment_id):
    comment = ReadComment.query.get(read_comment_id)
    post_id = comment.read_post_id
    db.session.delete(comment)
    db.session.commit()

    return redirect(f"/read_post/{post_id}")


@app.route("/delete_read_post/<int:read_post_id>")
def delete_read_post(read_post_id):
    read_post = ReadPost.query.get(read_post_id)

    db.session.delete(read_post)
    db.session.commit()

    return redirect("/read_content")

@app.route("/edit_read_post/<int:read_post_id>", methods=['GET', 'POST'])
def edit_read_post(read_post_id):
    read_post = ReadPost.query.get(read_post_id)
    form = AddReadPost(title=read_post.title, text=read_post.text)
    if form.validate_on_submit():
        read_post.title = form.title.data
        read_post.text = form.text.data
        read_post.edited_at = datetime.utcnow()

        db.session.commit()
        return redirect("/read_content")

    return render_template("upload_text_post.html", form=form)




@app.route("/choose_upload")
def choose_upload():
    return render_template("choose_upload.html")





@app.route("/reviews")
def reviews():
    reviews = Review.query.all()

    for review in reviews:
        review.formatted_time = review.created_at.strftime("%I:%M %p, %b %d %Y")
        review.formatted_edited_at = review.edited_at.strftime("%I:%M %p, %b %d %Y")

    return render_template("reviews.html", reviews=reviews)






@app.route("/upload_review", methods=['GET', 'POST'])
def upload_review():
    form = AddReview()
    if form.validate_on_submit():
        author_profile = current_user.path

        new_review = Review(review=form.review.data, author_username=current_user.username,
                                 author_first_name=current_user.first_name, author_last_name=current_user.last_name,
                                 author_profile=author_profile)
        db.session.add(new_review)
        db.session.commit()

        return redirect("/reviews")

    return render_template("upload_review.html", form=form)


@app.route("/delete_review/<int:review_id>")
def delete_review(review_id):
    review = Review.query.get(review_id)

    db.session.delete(review)
    db.session.commit()

    return redirect("/reviews")

@app.route("/edit_review/<int:review_id>", methods=['GET','POST'])
def edit_review(review_id):
    review = Review.query.get(review_id)

    form = AddReview(review=review.review)
    if form.validate_on_submit():
        review.review = form.review.data
        review.edited_at = datetime.utcnow()
        db.session.commit()

        return redirect("/reviews")

    return render_template("upload_review.html", form=form)




@app.route("/timeline")
def timeline():
    events = Event.query.order_by(Event.year).all()
    return render_template("timeline.html", events=events)

@app.route("/event/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event.html', event=event)