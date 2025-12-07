from datetime import datetime
from db import db

class Blog(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(128), unique=True, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta = db.relationship('BlogMeta', backref='blog', uselist=False)


class BlogMeta(db.Model):
    __tablename__ = 'blog_meta'
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('post.id'), unique=True, nullable=False)
    logo = db.Column(db.String(256), nullable=True)


class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=True)
    direction = db.Column(db.String(256), nullable=True)
    message = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    awards = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

