from flask import Blueprint, render_template, redirect, url_for
from .forms import LoginForm, SignUpForm
from .models import User
from sqlalchemy import select
from . import db

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(select(User).filter_by(email=form.email.data))
        if user.check_password(form.password.data):
            return redirect(url_for("views.home"))
    return render_template("auth/login.html", form=form)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        new_user = User(email=form.email.data, username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return render_template("auth/signup.html", form=form)