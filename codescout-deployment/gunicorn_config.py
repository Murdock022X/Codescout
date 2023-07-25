# Config file for gunicorn

# Ip and port to bind gunicorn to.
bind = '0.0.0.0:8080'

# Number of workers to create.
workers = 2

# Where to send logs to. TODO: add volume that records logs from container.
accesslog = '/opt/codescout/logs/gunicorn.access.log'
errorlog = '/opt/codescout/logs/gunicorn.error.log'
