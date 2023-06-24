from elasticsearch import Elasticsearch

from pathlib import Path

from flask_login import current_user

from werkzeug.utils import secure_filename

def assemble_es_url(host, port, secure):
    if not secure:
        return 'http://{}:{}'.format(host, port)

    return 'https://{}:{}'.format(host, port)

def assemble_cert_path(app, es_host, dcr_user_id):
    """
    Returns the directory for the certifications to be stored in via Path object.
    """
    return Path(app.root_path) / Path(app.config['UPLOAD_FOLDER']) / Path(str(dcr_user_id)) / Path(es_host)

def save_certs(es_certs_file, app, es_host, dcr_user_id):
    certs_pth = assemble_cert_path(app=app, es_host=es_host, dcr_user_id=dcr_user_id)

    certs_pth.mkdir(parents=True, exist_ok=True)

    es_certs_file.data.save(str(certs_pth / Path(secure_filename('http_ca.crt'))))

def verify_elasticsearch_connection(host, port, secure, dcr_user_id, es_user, password):

    cli = None

    if secure:
        cli = Elasticsearch(assemble_es_url(host, port, secure), )
    else:
        cli = Elasticsearch(assemble_es_url(host, port, secure), verify_certs=False, basic_auth=(es_user, password))