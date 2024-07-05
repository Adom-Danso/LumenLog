from flask import Blueprint, current_app as app, render_template, redirect, url_for, request, abort, flash
from flask_login import login_required, current_user
from .forms import PostForm, EditProfileForm, Follow_Or_Unfollow, SearchForm
from .models import Post, User
from . import db
from sqlalchemy import select
from langdetect import detect, LangDetectException
from werkzeug.utils import secure_filename
import uuid as uuid
import os

views = Blueprint("views", __name__)


@views.app_context_processor
def base():
    searchForm = SearchForm()
    user = current_user
    return dict(searchForm=searchForm, user=user)

@views.route('/')
@login_required
def home():
    PAGE_NUMBER = request.args.get('page', 1, type=int)
    POSTS_PER_PAGE = 20
    query =  current_user.following_posts()
    pagination = db.paginate(query, page=PAGE_NUMBER, per_page=POSTS_PER_PAGE, error_out=False)
    posts = pagination.items
    next_url = url_for('views.home', page=pagination.next_num)\
        if pagination.has_next else None
    prev_url = url_for('views.home', page=pagination.prev_num)\
        if pagination.has_next else None
    return render_template("views/home.html", current_user=current_user, posts=posts, pagination=pagination, next_url=next_url, prev_url=prev_url)

@views.route('/explore')
@login_required
def explore():
    PAGE_NUMBER = request.args.get('page', 1, type=int)
    POSTS_PER_PAGE = 20
    query =  Post.query.where(Post.author != current_user).order_by(Post.timestamp.desc())
    pagination = query.paginate(page=PAGE_NUMBER, per_page=POSTS_PER_PAGE)
    posts = pagination.items
    next_url = url_for('views.explore', page=pagination.next_num)
    prev_url = url_for('views.explore', page=pagination.prev_num)
    return render_template("views/home.html", current_user=current_user, posts=posts, pagination=pagination, next_url=next_url, prev_url=prev_url)

@views.route('/user/<username>', methods=["POST", "GET"])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.get_user_posts()
    form = Follow_Or_Unfollow()
    return render_template("views/user.html", username=username, user=user, posts=posts, form=form)

@views.route('/user/<username>/edit-profile', methods=["POST", "GET"])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first()
    if user == current_user:
        form = EditProfileForm(username=username, about_me=user.about_me)
        if form.validate_on_submit():
            user.username = form.username.data
            user.about_me = form.about_me.data
            f = form.profile_pic.data
            if f:
                filename = secure_filename(f.filename)
                uuid_filename = str(uuid.uuid1()) +'_'+ filename
                user.profile_pic = uuid_filename
                f.save(os.path.join(app.config['IMAGE_FOLDER'], uuid_filename))
            db.session.commit()
            return redirect(url_for("views.user", username=username))
        return render_template('views/edit_profile.html', form=form, username=username, user=current_user)
    return redirect(url_for('views.home'))

@views.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = Follow_Or_Unfollow()
    if form.validate_on_submit():
        user = db.session.scalar(
            select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.', category="error")
            return redirect(url_for('views.home'))
        if user == current_user:
            flash('You cannot follow yourself!', category="error")
            return redirect(url_for('views.user', username=username))
        current_user.follow(user)
        db.session.commit()
        return redirect(url_for('views.user', username=username))
    else:
        return redirect(url_for('views.home'))


@views.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = Follow_Or_Unfollow()
    if form.validate_on_submit():
        user = db.session.scalar(
            select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.', category="error")
            return redirect(url_for('views.home'))
        if user == current_user:
            flash('You cannot unfollow yourself!', category="error")
            return redirect(url_for('views.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        return redirect(url_for('views.user', username=username))
    else:
        return redirect(url_for('views.home'))

@views.route("/post/<int:id>", methods=["GET", "POST"])
@login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return render_template('views/post.html', post=post)


@views.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.content.data)
        except LangDetectException:
            language = ''
        f = form.cover.data
        filename = secure_filename(f.filename)
        uuid_filename = str(uuid.uuid1()) +'_'+ filename
        f.save(os.path.join(app.config['IMAGE_FOLDER'], uuid_filename))
        new_post = Post(title=form.title.data, cover=uuid_filename, content=form.content.data, author=current_user, language=language)
        db.session.add(new_post)
        db.session.commit()
        flash("Post has been created successfully.", category="success")
        return redirect(url_for("views.user", username=current_user.username))
    return render_template('views/create_post.html', form=form)


@views.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    try:
        if post.author.id == current_user.id:
            db.session.delete(post)
            db.session.commit()
            flash("Post has been deleted successfully.", category="success")
            return redirect(url_for('views.user', username=current_user.username))
        flash("There was a problem problem deleting post.", category="error")
        return redirect(url_for('views.user', username=current_user.username))
    except:
        flash("There was a problem problem deleting post.", category="error")
        return redirect(url_for('views.user', username=current_user.username))

@views.route('/search', methods=['POST'])
@login_required
def search():
    PAGE_NUMBER = request.args.get('page', 1, type=int)
    POSTS_PER_PAGE = 70
    searchForm = SearchForm()
    if searchForm.validate_on_submit():
        search = searchForm.search.data
        query = Post.query.filter(Post.content.like(f'%{search}%'))
        
        pagination = query.paginate(page=PAGE_NUMBER, per_page=POSTS_PER_PAGE)
        posts = pagination.items
        next_url = url_for('views.search', page=pagination.next_num)
        prev_url = url_for('views.search', page=pagination.prev_num)
        return render_template('views/search.html', posts=posts, pagination=pagination, next_url=next_url, prev_url=prev_url)
    
