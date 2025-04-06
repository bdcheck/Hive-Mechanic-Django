#!/bin/bash

echo Hive Mechanic: Starting Hive Mechanic server...
source /app/venv/bin/activate

cd /app/hivemechanic

echo Hive Mechanic: Initializing database and static resources...

mkdir -p /app/media/simple_data_export_uploads
mkdir -p /app/media/incoming_message_media
mkdir -p /app/media/outgoing_message_media

echo Hive Mechanic: Creating/updating database...
python manage.py migrate filer --skip-checks
python3 manage.py migrate --skip-checks

echo Hive Mechanic: Creating/updating superuser...
python3 manage.py docker_update_data docker/data/users.json --skip-checks

echo Hive Mechanic: Creating/updating Quicksilver tasks...
python3 manage.py install_quicksilver_tasks --skip-checks

echo Hive Mechanic: Clearing any left-over ongoing executions from past runs...
python3 manage.py clear_ongoing_executions --before_minutes 0 --skip-checks

echo Hive Mechanic: Creating/updating groups...
python3 manage.py loaddata fixtures/groups.json --skip-checks

echo Hive Mechanic: Initializing permissions...
python3 manage.py initialize_permissions --skip-checks

echo Hive Mechanic: Initializing default site settings...
python3 manage.py initialize_default_site_settings --skip-checks

echo Hive Mechanic: Initializing default repository...
python3 manage.py install_default_repository --skip-checks

echo Hive Mechanic: Creating/updating default activity...
python3 manage.py docker_update_data docker/data/activities.json --skip-checks

echo Hive Mechanic: Creating/updating channels...
python3 manage.py docker_update_data docker/data/channels.json --skip-checks

echo Hive Mechanic: Creating/updating default activity...
python3 manage.py enable_referenced_cards --skip-checks

echo Hive Mechanic: Gathering static files...
python3 manage.py collectstatic --no-input

echo Hive Mechanic: Validating installation...
python3 manage.py check

echo Installing and starting gunicorn...
pip install gunicorn
gunicorn hivemechanic.wsgi --log-file - --capture-output --enable-stdio-inheritance --bind="0.0.0.0:$DJANGO_WEB_PORT"

# Uncomment the line below if running on a local machine, and not a server container host.
# echo Hive Mechanic: Starting built-in Django web server on port $DJANGO_WEB_PORT...

# python3 manage.py runserver 0.0.0.0:$DJANGO_WEB_PORT
