from elasticsearch import Elasticsearch
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import g, request, redirect, url_for, flash
from website.models import Organizations, Clusters
import json

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

def check_es_cluster_validity(es_cluster: Clusters) -> bool:
    if es_cluster.status == 1:
        return True
    return False

def get_from_and_size(page, page_len):
    return page * page_len, page_len

def url_serialize(langs):
    return '+'.join(langs)

def url_deserialize(langs_str):
    return langs_str.split('+')   

"""
class ResponseData:
    def __init__(self, resp):
        self.es_id = resp['_id']
        self.cluster_id = resp['cluster_id']
        self.item = resp['_source']

    def toJSON(self):
        return {'_id': self.es_id, 'cluster_id': self.cluster_id, '_source': self.item}

class SearchData:
    def __init__(self, responses: list[dict] = [], page_len: int = 20):
        self.resp_data = [ResponseData(resp) for resp in responses]
        self.page_len = page_len

    def __getitem__(self, index):
        return self.get_page_data(index)

    def __len__(self):
        return len(self.resp_data)

    def total_pages(self):
        pages = len(self.resp_data) // self.page_len

        if len(self.resp_data) % self.page_len > 0:
            pages += 1

        return pages

    def append(self, data):
        self.resp_data.append(ResponseData(data))

    def get_page_data(self, page_no):
        offset = page_no * self.page_len
        return self.resp_data[offset:offset + self.page_len]

    def toJSON(self):
        return {'page_len': self.page_len, 'responses': [resp.toJSON() for resp in self.resp_data]}
"""
