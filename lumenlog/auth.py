from flask import Blueprint, flash, render_template, redirect, url_for, request
from .forms import LoginForm, SignUpForm
from .models import User
from sqlalchemy import select
from . import db
from flask_login import login_user, current_user, logout_user, login_required

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        # if the user is already signed in, redirect him to the homepage
        return redirect(url_for('views.home'))
    if form.validate_on_submit():
        # search the database for user that matches the email submitted
        user = db.session.execute(select(User).filter_by(email=form.email.data)).scalar()
        if user.check_password(form.password.data):
            next = request.args.get('next')
            login_user(user, remember=True)
            return redirect(url_for("views.home") or next)
        flash("Incorrect email or password.", "error")
    return render_template("auth/login.html", form=form)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        # if the user is already signed in, redirect him to the homepage
        return redirect(url_for('views.home'))
    form = SignUpForm()
    if form.validate_on_submit():
        new_user = User(email=form.email.data, username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return render_template("auth/signup.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))