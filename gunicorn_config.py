import os


bind = os.getenv('GUNICORN_BIND', default='127.0.0.1:8000')
workers = 4
timeout = 120

# If GUNICORN_BIND exists, then specify log files
if os.getenv('GUNICORN_BIND'):
    accesslog = "./logs/access.log"
    errorlog = "./logs/error.log"
