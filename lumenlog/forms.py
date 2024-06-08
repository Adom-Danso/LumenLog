from . import db
import email_validator
from .models import User
from sqlalchemy import select
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# class login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Please provide a username.'), Email()])
    password = PasswordField('Password', validators=[DataRequired('Please enter your password.')])
    submit = SubmitField('Login')
    
    def validate_email(self, email):
        if email.errors:
            return
        user = db.session.execute(select(User).filter_by(email=email.data)).scalar()
        if user is None:
            raise ValidationError("Account does not exist.")
        

# class signup form    
class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Please provide an email.'), Email()])
    username = StringField('Username', validators=[DataRequired('Please enter a username.'), Email()])
    password = PasswordField('Password', validators=[DataRequired('Please provide a password'), Length(min=8, max=20)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired('Please confirm your password.'), Length(min=8, max=20), EqualTo('password', "Passwords do not match")])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        if username.errors:
            return
        user = db.session.execute(select(User).filter_by(username=username.data)).scalar()
        if user:
            raise ValidationError("Username already in use.")
    
    def validate_email(self, email):
        if email.errors:
            return
        user = db.session.execute(select(User).filter_by(email=email.data)).scalar()
        if user:
            raise ValidationError("Email address already in use.")