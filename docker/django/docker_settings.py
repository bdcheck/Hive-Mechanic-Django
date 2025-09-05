# pylint: disable=line-too-long

import json
import os
import tempfile

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = (os.getenv('DJANGO_DEBUG', 'False').lower() == 'true')

ALLOWED_HOSTS = [ os.getenv('DJANGO_ALLOWED_HOST', 'localhost'), 'localhost' ]
CSRF_TRUSTED_ORIGINS = [ 'https://%s' % os.getenv('DJANGO_ALLOWED_HOST', 'localhost') ]

ADMINS = [(os.getenv('DJANGO_ADMIN_NAME', 'Hive Mechanic Admin'), os.getenv('DJANGO_ADMIN_EMAIL', 'hive-user@example.com'),)]

DATABASES = {}

pg_database = os.getenv('PG_DB', '')

if pg_database != '':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME':     os.getenv('PG_DB'),
        'USER':     os.getenv('PG_USER'),
        'PASSWORD': os.getenv('PG_PASSWORD'),
        'HOST':     'db',
    }
else:
    DATABASES['default'] = {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME':   '/app/database/small_steps.db',
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'medium',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
    },
    'formatters': {
        'medium': {
            'format': '[{name} / {levelname}] {asctime}: {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('CRON_MAIL_SERVER', 'mail.example.com')
EMAIL_HOST_USER = os.getenv('CRON_MAIL_USERNAME', 'postmaster')
EMAIL_HOST_PASSWORD = os.getenv('CRON_MAIL_PASSWORD', 'CHANGE-ME')

TIME_ZONE = os.getenv('DJANGO_TIME_ZONE', 'America/Chicago')

SITE_URL = 'https://%s' % ALLOWED_HOSTS[0]

QUICKSILVER_LOCK_DIR = '/app/tmp'

SIMPLE_DATA_EXPORTER_SITE_NAME = os.getenv('SIMPLE_DATA_EXPORTER_SITE_NAME', 'Hive Mechanic')
SIMPLE_DATA_EXPORTER_OBFUSCATE_IDENTIFIERS = True
SIMPLE_DATA_EXPORT_FROM_ADDRESS = '%s <%s>' % (os.getenv('DJANGO_ADMIN_NAME', 'Hive Mechanic Admin'), os.getenv('DJANGO_ADMIN_EMAIL', 'hive-user@example.com'))

SIMPLE_DASHBOARD_SITE_NAME = SIMPLE_DATA_EXPORTER_SITE_NAME

if os.getenv('SIMPLE_DATA_EXPORTER_OBFUSCATE_IDENTIFIERS', 'true').lower() == 'false':
    SIMPLE_DATA_EXPORTER_OBFUSCATE_IDENTIFIERS = False

SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'
STATIC_ROOT = '/app/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media/'

PHONE_REGION = os.getenv('PHONE_REGION', 'US')

SILENCED_SYSTEM_CHECKS = [
    'security.W005',
    'security.W008',
    'security.W021',
    'simple_backup.W001',
    'simple_backup.W002',
    'simple_messaging_twilio.E001',
    'simple_messaging_twilio.E002',
    'simple_messaging_twilio.E003',
    'simple_messaging.E001',
    'simple_messaging.W002',

]

if os.getenv('DJANGO_DEBUG', '') != '':
    DEBUG = True

    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    SILENCED_SYSTEM_CHECKS.append('security.W012')
    SILENCED_SYSTEM_CHECKS.append('security.W016')
    SILENCED_SYSTEM_CHECKS.append('security.W018')

if os.getenv('SIMPLE_MESSAGING_SECRET_KEY', '') != '':
    SIMPLE_MESSAGING_SECRET_KEY = os.getenv('SIMPLE_MESSAGING_SECRET_KEY', None)
else:
    SILENCED_SYSTEM_CHECKS.append('simple_messaging.E002')

PDK_DASHBOARD_ENABLED = True

SITE_URL = 'https://' + ALLOWED_HOSTS[0]

HIVE_API_URL = 'https://' + ALLOWED_HOSTS[0] + '/http/'

HIVE_CLIENT_TOKEN = 'abc12345' # nosec

TEST_RUNNER = 'hivemechanic.no_db_test_runner.NoDbTestRunner'

DEFAULT_FROM_MAIL_ADDRESS = 'Hive Mechanic <noreply@hivemechanic.net>'

ADDITIONAL_APPS = [
    'simple_messaging_twilio',
]
