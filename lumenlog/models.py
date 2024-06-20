from lumenlog import db
from sqlalchemy import String, DateTime, Text, ForeignKey, Integer, Table, Column, func, select, or_
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped, aliased
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import List, Optional
from hashlib import md5
from flask import current_app as app


followers = Table(
    'followers',
    db.metadata,
    Column('follower_id', Integer, ForeignKey('user.id'),
              primary_key=True),
    Column('followed_id', Integer, ForeignKey('user.id'),
              primary_key=True)
)
    
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(120))
    timestamp: Mapped[str] = mapped_column(DateTime, default=datetime.utcnow)
    about_me: Mapped[str] = mapped_column(String(70), nullable=True)
    profile_pic: Mapped[str] = mapped_column(String(), nullable=True)
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="author")
    following: WriteOnlyMapped['User'] = relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: WriteOnlyMapped['User'] = relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')
    
    last_message_read_time: Mapped[Optional[datetime]]

    # ...
    messages_sent: WriteOnlyMapped['Message'] = relationship(
        foreign_keys='Message.sender_id', back_populates='sender')
    messages_received: WriteOnlyMapped['Message'] = relationship(
        foreign_keys='Message.recipient_id', back_populates='recipient')

    # ...

    def unread_message_count(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        query = select(Message).where(Message.recipient == self,
                                         Message.timestamp > last_read_time)
        return db.session.scalar(select(func.count()).select_from(
            query.subquery()))
    
    # function for automatically hashing and storing user password
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_user_posts(self):
        return db.session.query(Post).filter(Post.author.has(username=self.username)).order_by(Post.timestamp.desc()).all()
    
    def avatar(self, size):
        if self.profile_pic is None:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = select(func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = select(func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    
    def following_posts(self):
        Author = aliased(User)
        Follower = aliased(User)
        return (
            select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(or_(
                Follower.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(5000))
    cover: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[str] = mapped_column(DateTime, default=datetime.utcnow)
    language: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    author_id: Mapped[int] = mapped_column(Integer(), ForeignKey("user.id"))
    author: Mapped['User'] = relationship("User", back_populates="posts")
    
class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)
    body: Mapped[str] = mapped_column(String(150))
    timestamp: Mapped[str] = mapped_column(DateTime, default=datetime.utcnow)
    sender: Mapped[User] = relationship(
        foreign_keys='Message.sender_id',
        back_populates='messages_sent')
    recipient: Mapped[User] = relationship(
        foreign_keys='Message.recipient_id',
        back_populates='messages_received')
    
    
    def __repr__(self) -> str:
        return '<Message {}'.format(self.body)
