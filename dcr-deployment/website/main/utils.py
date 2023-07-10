from elasticsearch import Elasticsearch
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import g, request, redirect, url_for, flash
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

def get_es_connection(host: str, port: str, secure: bool, org_name: str, app, username: str, password: str) -> Elasticsearch:
    url = assemble_es_url(host=host, port=port, secure=secure)
    cert_path = assemble_cert_path(host=host, org_name=org_name, app=app) / Path('http_ca.crt')
    auth = (username, password)

    conn = Elasticsearch(url, ca_certs=cert_path, basic_auth=auth)

    return conn

def get_search_page_data(data: list[dict], page_idx: int, page_len: int):
    offset = page_idx * page_len
    return data[offset:offset + page_len]

class PageData:
    def __init__(self, response, cluster_id):
        self.es_id = response['_id']
        self.cluster_id = cluster_id
        self.item = response['_source']
