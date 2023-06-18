from elasticsearch import Elasticsearch

def assemble_es_url(host, port):
    return 'https://{}:{}'.format(host, port)

def verify_elasticsearch_connection():
    pass
