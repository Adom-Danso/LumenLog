from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from .forms import PostForm, EditProfileForm
from .models import Post, User
from . import db

views = Blueprint("views", __name__)

@views.route('/', methods=["GET", "POST"])
@login_required
def home():
    form = PostForm()
    page_number = request.args.get('page', 1, type=int)
    post_per_page = 70
    if form.validate_on_submit():
        new_post = Post(content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("views.home"))
    query =  Post.query.order_by(Post.timestamp.desc()) # Query to get all post in descending order 
    pagination = query.paginate(page=page_number, per_page=post_per_page)
    posts = pagination.items
    # current_page = url_for('views.home', page=page_num)
    next_url = url_for('views.home', page=pagination.next_num)
    prev_url = url_for('views.home', page=pagination.prev_num)
    return render_template("views/home.html", current_user=current_user, form=form, posts=posts, pagination=pagination, next_url=next_url, prev_url=prev_url)

@views.route('/user/<username>', methods=["POST", "GET"])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.get_user_posts()
    return render_template("views/user.html", username=username, user=user, posts=posts)

@views.route('/user/<username>/edit-profile', methods=["POST", "GET"])
@login_required
def edit_profile(username):
    form = EditProfileForm(username=username)
    # form.username.default = username
    # form.process()
    user = User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        user.username = form.username.data
        user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for("views.user", username=username))
    return render_template('views/edit_profile.html', form=form, username=username)

@views.route('/explore', methods=["GET", "POST"])
@login_required
def explore():
    page_number = request.args.get('page', 1, type=int)
    post_per_page = 2
    query =  Post.query.order_by(Post.timestamp.desc()) 
    pagination = query.paginate(page=page_number, per_page=post_per_page)
    posts = pagination.items
    next_url = url_for('views.explore', page=pagination.next_num)
    prev_url = url_for('views.explore', page=pagination.prev_num)
    return render_template("views/home.html", current_user=current_user, posts=posts, pagination=pagination, next_url=next_url, prev_url=prev_url)
    