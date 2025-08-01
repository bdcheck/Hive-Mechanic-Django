"""
Django settings for hivemechanic project.

Generated by 'django-admin startproject' using Django 1.11.15.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import logging
import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django_db_logger',
    'prettyjson',
    'django_filters',
    'quicksilver',
    'passive_data_kit',
    'django_dialog_engine',
    'nagios_monitor',
    'simple_backup',
    'simple_messaging',
    'simple_messaging_hive',
    'simple_messaging_switchboard',
    'simple_messaging_loopback',
    'docker_utils',
    'user_creation',
    'builder',
    'simple_dashboard',
    'activity_logger',
    'integrations',
    'twilio_support',
    'http_support',
    'cli_support',
    'easy_thumbnails',
    'filer',
    'django.contrib.admin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hivemechanic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,
            'libraries' : {
                'staticfiles': 'django.templatetags.static',
            }
        },
    },
]

WSGI_APPLICATION = 'hivemechanic.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'DEBUG'
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PHONE_NUMBER_REGION = 'US'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

def FETCH_LOGGER(level=logging.DEBUG):
    global SETTINGS_LOGGER

    try:
        if SETTINGS_LOGGER is not None:
            pass

    except NameError:
        SETTINGS_LOGGER = None

    if SETTINGS_LOGGER is None:
        SETTINGS_LOGGER = logging.getLogger('db')

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = logging.Formatter('[%(levelname)s] %(asctime)s: %(message)s')
        handler.setFormatter(formatter)

        SETTINGS_LOGGER.addHandler(handler)

    return SETTINGS_LOGGER

def DDE_BOTIUM_EXTRAS(player):
    return {
        'player': player
    }

SILENCED_SYSTEM_CHECKS = ['fields.W904', 'security.W005', 'security.W021']

SECURE_HSTS_SECONDS = 300
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

TEXT_MESSAGE_WARNING_FILE_SIZE = 5 * 1024 * 1024

QUICKSILVER_MIN_CYCLE_SLEEP_SECONDS = 2.5

from .local_settings import *

for app in ADDITIONAL_APPS:
    INSTALLED_APPS.append(app)

# Suppress pygame notifications...
#
# from os import environ
# environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
#
# import pygame  # it is important to import pygame after that
