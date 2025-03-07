import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'CHANGEMECHANGEMECHANGEMECHANGEMECHANGEMECHANGEMECHANGEMECHANGEMECHANGEMECHANGEME' # nosec

DEBUG = False

ALLOWED_HOSTS = [
	'dev.hivemechanic.org'
]

ADMINS = [
	('Chris Karr', 'chris@audacious-software.com')
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME':     'circle_test',
        'USER':     'root',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR + '/media/'

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

SILENCED_SYSTEM_CHECKS = [
    'security.W019',
    'security.W005',
    'security.W021',
    'fields.W904',
    'simple_backup.W001',
    'simple_backup.W002',
    'builder.W002',
    'simple_messaging.E001',
    'simple_messaging.E002',
    'simple_messaging.E003',
]

PDK_DASHBOARD_ENABLED = True

SITE_URL = 'https://' + ALLOWED_HOSTS[0]

HIVE_API_URL = 'https://' + ALLOWED_HOSTS[0] + '/http/'

HIVE_CLIENT_TOKEN = 'abc12345' # nosec

# TEST_RUNNER = 'hivemechanic.no_db_test_runner.NoDbTestRunner'

DEFAULT_FROM_MAIL_ADDRESS = 'Hive Mechanic <noreply@hivemechanic.net>'

ADDITIONAL_APPS = []

SIMPLE_DASHBOARD_SITE_NAME = "Hive Mechanic Circle CI"
