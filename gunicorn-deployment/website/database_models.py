from flask_login import UserMixin

from . import db, login_manager


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(50), unique=True)

    password_hash = db.Column(db.String(32))

    first_name = db.Column(db.String(50))

    last_name = db.Column(db.String(50))
