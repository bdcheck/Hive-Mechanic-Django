FROM ubuntu:24.04

# Add crontab file in the cron directory
ADD ./docker/cron/crontab /etc/cron.d/django

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/django

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Install Ubuntu packages

RUN apt-get update
RUN apt-get install -y gettext apt-utils curl git build-essential python3-dev python3-venv libldap2-dev libsasl2-dev slapd ldap-utils cron gdal-bin ssmtp mailutils moreutils libsqlite3-mod-spatialite
WORKDIR /app

RUN python3 -m venv /app/venv
RUN . /app/venv/bin/activate && pip install -U wheel pip

ADD . hivemechanic

RUN . /app/venv/bin/activate && pip install -r /app/hivemechanic/requirements.txt

WORKDIR /app/hivemechanic

ADD ./docker/django/docker_settings.py /app/hivemechanic/hivemechanic/local_settings.py
ADD ./docker/django/wsgi.py /app/hivemechanic/hivemechanic/docker_wsgi.py

RUN mv /etc/environment /etc/environment.old
ADD ./docker/.env /etc/environment
RUN cat /etc/environment.old >> /etc/environment

ADD ./docker/cron/run.sh /app/run.sh
