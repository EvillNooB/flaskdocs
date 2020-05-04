"""Gunicorn configuration."""

bind = '127.0.0.1:8000'

workers = 5
worker_class = 'gevent'

accesslog = '-'