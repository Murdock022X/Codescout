# Config file for gunicorn

# Ip and port to bind gunicorn to.
bind = '127.0.0.1:8080'

# Number of workers to create.
workers = 2

# Where to send logs to. TODO: add volume that records logs from container.
accesslog = '/home/kaiser/package-search/gunicorn-deployment/logs/gunicorn.access.log'
errorlog = '/home/kaiser/package-search/gunicorn-deployment/logs/gunicorn.error.log'
