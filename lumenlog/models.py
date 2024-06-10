from . import db
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import List
from hashlib import md5

    
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(120))
    timestamp: Mapped[str] = mapped_column(DateTime, default=datetime.utcnow)
    about_me: Mapped[str] = mapped_column(String(70), nullable=True)  # Allow NULL values
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="author")

    # function for automatically hashing and storing user password
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_user_posts(self):
        return db.session.query(Post).filter(Post.author.has(username=self.username)).all()
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(140))
    timestamp: Mapped[str] = mapped_column(DateTime, default=datetime.utcnow)
    author_id: Mapped[int] = mapped_column(Integer(), ForeignKey("user.id"))
    author: Mapped['User'] = relationship("User", back_populates="posts")
    
    
