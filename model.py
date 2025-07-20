from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    # One-to-many relationship: a user can have multiple URLs
    urls = db.relationship('URL', backref='owner', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class URL(db.Model):
    __tablename__ = 'url'

    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    visit_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ForeignKey connects URL to its owner
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<URL slug={self.slug} visits={self.visit_count}>"
