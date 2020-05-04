FROM python:3.7.3
LABEL version='0.0.1'

# Software version management
ENV NGINX_VERSION=1.13.8-1~jessie
ENV SUPERVISOR_VERSION=3.3.5-1
ENV GUNICORN_VERSION=19.7.1
ENV GEVENT_VERSION=1.2.2


# Flask demo application
COPY ./app /app
RUN pip install -r /app/requirements.txt

# System packages installation
RUN echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list
RUN wget https://nginx.org/keys/nginx_signing.key -O - | apt-key add -
RUN apt-get update && apt-get install -y nginx=$NGINX_VERSION \
                                         supervisor=$SUPERVISOR_VERSION \
&& rm -rf /var/lib/apt/lists/*

# Nginx configuration
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/nginx.conf

# Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf

# Gunicorn installation
RUN pip install gunicorn gevent

# Gunicorn default configuration
COPY gunicorn.config.py /app/gunicorn.config.py

WORKDIR /app

EXPOSE 80 443 6000 8000

CMD ["/usr/bin/supervisord"]