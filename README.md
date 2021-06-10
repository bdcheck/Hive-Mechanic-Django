# Hive Mechanic

Hive Mechanic is an extensible system for implementing interactive activities via SMS and other communication media.

## Basic installation instructions

Hive Mechanic assumes a Linux or Unix-like environment with a local Python installation capable of supporting virtual environments as well as a compatible web server (Apache configuration directives are provided below). It requires a local Postgres 9.5 or higher installation that includes the PostGIS extensions.

To get started, create a directory for Hive Mechanic files and initialize its virtual environment:

    mkdir /var/www/django/hive
    cd /var/www/django/hive
    python3 -m venv /var/www/django/hive/venv
    source /var/www/django/hive/venv/bin/activate

Check out Hive Mechanic from GitHub:

    git clone https://github.com/bdcheck/Hive-Mechanic-Django.git /var/www/django/hive/hive

Initialize the git submodules:

    cd /var/www/django/hive/hive
    git submodule init
    git submodule update

Install the Python dependencies:

    pip install -r requirements.txt

Note that you may need to install some system dependencies (such as `gdal`) in order to build and install the Python dependencies. If interrupted, install those dependencies, and re-run the command above until all Python packages are successfully installed.

If you have not already, create an empty Postgres database and be sure to initialize it with the PostGIS extension.

Once the database is created, copy the `local_settings.py` template and begin customizing it for your local installation:

    cp hivemechanic/local_settings.py-template hivemechanic/local_settings.py

Edit the new configuration file, updating the database configuration and local hostname.

After the database is ready, create the tables and schemas for the system:

    ./manage.py migrate

Initialize the static resources:

    ./manage.py collectstatic

Create a local superuser:

    ./manage.py createsuperuser

Install the local card repository:

    ./manage.py install_default_card_repository

At this point, you should set up Hive Mechanic to work with your local web server to access the web interface (Apache directions are below). 

After setting up your web server, new cards will be installed into the system:

    https://dev.hivemechanic.org/admin/builder/interactioncard/

Enable each of the cards that you wish to use in your activities.

After enabling cards, you will likely want to create an activity to test the system. First, navigate to the `Activities` page and add a new activity by clicking the floating action button with a `+` icon in the bottom-right of the screen.

Please enter a name at the prompt and add enough cards to implement your activity.

Once the activity has been created, you can test it from the command line:

    ./manage.py cli_run_activity activity-slug

where `activity-slug` is the identifier you gave the game while creating it.

The system will execute the game from the command line. Feel free to type your responses as if you were texting the system.

Once the activity is running as expected, you are now ready to open it up to the world and integrate it with Twilio and other services.

## Twilio integration

*Coming Soon.*

## Apache integration

*Coming Soon.*

