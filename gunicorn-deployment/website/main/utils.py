from elasticsearch import Elasticsearch
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import g, request, redirect, url_for, flash
from flask_login import current_user
from functools import wraps
from website.models import Organizations

def assemble_es_url(host, port, secure):
    if not secure:
        return 'http://{}:{}'.format(host, port)

    return 'https://{}:{}'.format(host, port)

def assemble_cert_path(host, org_name, app):
    """
    Returns the directory for the certifications to be stored in via Path object.
    """
    return Path(app.root_path) / Path(app.config['UPLOAD_FOLDER']) / Path(org_name) / Path(host)

def save_certs(certs_file, host, org_name, app):
    certs_pth = assemble_cert_path(host=host, org_name=org_name, app=app)

    certs_pth.mkdir(parents=True, exist_ok=True)

    certs_file.data.save(str(certs_pth / Path(secure_filename('http_ca.crt'))))

def get_es_connection(host, port, secure, org_name, app, username, password):
    url = assemble_es_url(host=host, port=port, secure=secure)
    cert_path = assemble_cert_path(host=host, org_name=org_name, app=app) / Path('http_ca.crt')
    auth = (username, password)

    conn = Elasticsearch(url, ca_certs=cert_path, basic_auth=auth)

    return conn

def org_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.organization_id:
            flash('You need to join an organization to use that.', category='danger')
            return redirect(url_for('main.join_organization', next=request.url))
        return f(*args, **kwargs)
    return decorated_func