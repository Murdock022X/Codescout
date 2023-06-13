from flask_login import UserMixin

from website import db, login_manager

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(254), unique=True)

    password_hash = db.Column(db.String(88))

    first_name = db.Column(db.String(50))

    last_name = db.Column(db.String(50))

    clusters = db.relationship('Clusters', backref='user', lazy=True)

class Clusters(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(254))

    cluster_ip = db.Column(db.String(40))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
