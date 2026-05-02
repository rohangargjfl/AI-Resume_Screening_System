from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True) # Nullable for SSO-only users
    name = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(256), nullable=True)
    sso_provider = db.Column(db.String(50), nullable=True) # e.g. 'google'
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def initials(self):
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.name[:2].upper()

    def __repr__(self):
        return f'<User {self.email}>'
