FROM ubuntu:24.04

WORKDIR /app

RUN apt-get update
RUN apt-get install -y gettext apt-utils curl git build-essential python3-dev python3-venv libldap2-dev libsasl2-dev slapd ldap-utils cron gdal-bin ssmtp mailutils moreutils libsqlite3-mod-spatialite nodejs
WORKDIR /app

RUN python3 -m venv /app/venv
RUN . /app/venv/bin/activate && pip install -U wheel pip

ADD . hivemechanic

RUN . /app/venv/bin/activate && pip install -r /app/hivemechanic/requirements.txt

WORKDIR /app/hivemechanic

ADD ./docker/django/docker_settings.py /app/hivemechanic/hivemechanic/local_settings.py
ADD ./docker/django/wsgi.py /app/hivemechanic/hivemechanic/docker_wsgi.py

ADD ./docker/django/django.sh /app/django.sh

EXPOSE ${DJANGO_WEB_PORT}