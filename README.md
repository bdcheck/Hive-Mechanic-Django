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

At this point, you should set up Hive Mechanic to work with your local web server to access the web interface (Apache directions are below). To launch Django's built-in server:

    ./manage.py runserver
    
Note the port number and access the administration interface with the superuseer account created earlier:

    https://my-site.example.com:8000/admin/

After setting up your web server, new cards will be installed into the system:

    https://my-site.example.com/admin/builder/interactioncard/

Enable each of the cards that you wish to use in your activities.

After enabling cards, you will likely want to create an activity to test the system. First, navigate to the `Activities` page and add a new activity by clicking the floating action button with a `+` icon in the bottom-right of the screen.

Please enter a name at the prompt and add enough cards to implement your activity.

Once the activity has been created, you can test it from the command line:

    ./manage.py cli_run_activity activity-slug

where `activity-slug` is the identifier created when you named the activity. If you named your activity "Test Activity 123", then the `activity-slug` will be `test-activity-123`. You can also retrieve this identifier from the URL when you are editing it in the builder. It will be the final path component of the URL in your browser.

The system will execute the game from the command line. Feel free to type your responses as if you were texting the system.

Once the activity is running as expected, you are now ready to open it up to the world and integrate it with Twilio and other services.

## Twilio integration

*Coming Soon.*

## Apache integration

To configure Apache to serve Hive Mechanic content, verify that the `mod-wsgi` module is installed and activated.

In your Apache configuration file, enable Hive Mechanic by including the following configuration directives:

    Alias /media /var/www/django/hive/hive/media
    Alias /static /var/www/django/hive/hive/static

The ab ove options instruct Apache to serve static files directly, bypassing the WSGI module for increased performance.

    WSGIDaemonProcess hive python-path=/var/www/django/hive/venv/lib/python3.8/site-packages:/var/www/django/hive/hive
    WSGIProcessGroup hive

The above directives set up the necessary Python paths that enable Hive Mechanic to run, including all the required dependencies.

    WSGIScriptAlias / /var/www/django/hive/hive/hivemechanic/wsgi.py
    
This directive is the main Python script that the WSGI module will enable Apache to route all other non-static/non-media requests through your Hive installation

### Recommendation: Enable SSL

With the availability of free SSL certificates through projects like [Let's Encrypt](https://letsencrypt.org/), you should secure your Hive Mechanic installation with HTTPS to prevent the compromise of any traffic or passwords to resources such as your Twilio account. 

After your set up your SSL certificate, the following Apache configuration will redirect traffic from unencrypted ports to safer encrypted ports, and set up Hive Mechanic to run alongside Apache's SSL module:

	<VirtualHost *:80>
		ServerName my-site.example.com
		
		ServerAdmin me@example.com
		DocumentRoot /var/www/html/my-site.example.com
		
		ErrorLog ${APACHE_LOG_DIR}/my-site.example.com_error.log
		CustomLog ${APACHE_LOG_DIR}/my-site.example.com_access.log combined
		
		RewriteEngine on
		RewriteRule    ^(.*)$    https://my-site.example.com$1    [R=301,L]
		
		RewriteCond %{SERVER_NAME} =my-site.example.com
		RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
	</VirtualHost>
    
	<VirtualHost *:443>
		ServerAdmin me@example.com
		ServerName my-site.example.com
		
		DocumentRoot /var/www/html/my-site.example.com
		
		<Directory />
			Options FollowSymLinks
			AllowOverride None
		</Directory>
		<Directory /var/www/html/my-site.example.com>
			Options FollowSymLinks MultiViews
			AllowOverride All
			Order allow,deny
			allow from all
		</Directory>
		
		<Directory /var/www/django/hive/hive/static>
			Header set Cache-Control "no-cache, no-store, must-revalidate"
			Header set Pragma "no-cache"
			Header set Expires -1
		</Directory>
		
		ErrorLog ${APACHE_LOG_DIR}/my-site.example.com_error.log
		CustomLog ${APACHE_LOG_DIR}/my-site.example.com_access.log combined
		
		SSLEngine on
		SSLProtocol All -SSLv2 -SSLv3
		
		BrowserMatch "MSIE [2-6]"nokeepalive ssl-unclean-shutdown downgrade-1.0 force-response-1.0
		
		BrowserMatch "MSIE [17-9]"ssl-unclean-shutdown
		
		Alias /media /var/www/django/hive/hive/media
		Alias /static /var/www/django/hive/hive/static
		
		WSGIDaemonProcess hive python-path=/var/www/django/hive/venv/lib/python3.8/site-packages:/var/www/django/hive/hive
		WSGIProcessGroup hive
		
		WSGIScriptAlias / /var/www/django/hive/hive/hivemechanic/wsgi.py
		
		SSLCertificateFile      /etc/letsencrypt/live/my-site.example.com/fullchain.pem
		SSLCertificateKeyFile /etc/letsencrypt/live/my-site.example.com/privkey.pem
		Include /etc/letsencrypt/options-ssl-apache.conf
	</VirtualHost>

