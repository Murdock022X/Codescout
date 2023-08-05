from flask_login import UserMixin

from website import db, login_manager

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password_hash = db.Column(db.String(100))

    first_name = db.Column(db.String(50))

    last_name = db.Column(db.String(50))

    admin_status = db.Column(db.Boolean, default=False)

    # Status code 1 is approved, 0 is pending, 2 is denied.
    org_status = db.Column(db.Integer, default=0)

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

class Clusters(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    es_host = db.Column(db.String(200))

    es_port = db.Column(db.String(5))

    es_user = db.Column(db.String(100))

    es_password = db.Column(db.String(300))

    org_id = db.Column(db.Integer, unique=True)

class SoftwareTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(50))

    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

class Languages(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50))

    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

class Organizations(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True)

    users = db.relationship('Users', backref='organizations')

    cluster_id = db.Column(db.Integer, unique=True)

    software_types = db.relationship('SoftwareTypes', backref='organizations')

    languages = db.relationship('Languages', backref='organizations')

    enrollment_token = db.Column(db.String(64), unique=True)
