from flask_login import UserMixin

from website import db, login_manager

# Users table and loader to facilitate login for flask site.
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

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), default=None)

# Clusters table to keep track of the cluster that belongs to every organization.
class Clusters(db.Model):
    
    # Id primary key.
    id = db.Column(db.Integer, primary_key=True)

    # Name your cluster.
    name = db.Column(db.String(100))

    # Elasticsearch details, password is encrypted
    es_host = db.Column(db.String(200))
    es_port = db.Column(db.String(5))
    es_user = db.Column(db.String(100))
    es_password = db.Column(db.String(300))

    # Keep track of which organization the cluster belongs to.
    org_id = db.Column(db.Integer, unique=True)

# SoftwareTypes table keeps track of what Software Types have been added and 
# can be used for filter options when searching.
class SoftwareTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(50))

    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

# Languages table keeps track of what languages have been added and 
# can be used for filter options when searching.
class Languages(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50))

    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

# Organizations have a set cluster and many users, the user who creates the 
# organization will be the admin and be able to set the cluster configuration 
# and view and remove users from the organization. Users will be able to add 
# and search data from the cluster for the organization.
class Organizations(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Name the organization.
    name = db.Column(db.String(100), unique=True)

    # Relationship allows software to easily identify users who belong to the 
    # organization.
    users = db.relationship('Users', backref='organizations')

    # The database key for the cluster related to this organization.
    cluster_id = db.Column(db.Integer, unique=True)

    # A relationship that keeps track of all the different software types 
    # being used by this organization.
    software_types = db.relationship('SoftwareTypes', backref='organizations')

    # A relationship that keeps track of all the different software languages
    # being used by this organization.
    languages = db.relationship('Languages', backref='organizations')

    # An enrollment token that can be distributed by the organization admin 
    # to users who want to join the organization.
    enrollment_token = db.Column(db.String(64), unique=True)
