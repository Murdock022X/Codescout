from elasticsearch import Elasticsearch
from pathlib import Path
from werkzeug.utils import secure_filename
from website.models import Clusters
from cryptography.fernet import Fernet

def assemble_es_url(host, port):
    """
    Convert host and port into http url.
    :param host: The ip/dns.
    :param port: The port to connect to.
    :return: The http unsecure url for the host + port.
    """
    return 'http://{}:{}'.format(host, port)

def get_es_connection(host: str, port: str, username: str, password: str, enc_key: str) -> Elasticsearch:
    """
    Generate an Elasticsearch connection using supplied parameters.

    :param host: The host ip/dns.
    :param port: The host port to connect on.
    :param username: The Elasticsearch username to use for connection.
    :param password: The encrypted password info.
    :param enc_key: The encryption key which can decrypt the password.
    :return: The Elasticsearch connection.
    """

    # Fernet instance allows us to decrypt the encrypted password.
    f = Fernet(enc_key.encode(encoding="utf8"))

    # Assemble the URL for the elasticsearch cluster.
    url = assemble_es_url(host=host, port=port)

    # Assemble the authorization for the cluster into a tuple while decrypting the password.
    auth = (username, f.decrypt(password.encode(encoding="utf8")).decode(encoding="utf8"))

    # Generate connection to Elasticsearch.
    conn = Elasticsearch(url, basic_auth=auth, verify_certs=False)

    return conn

# Deprecated
"""
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
