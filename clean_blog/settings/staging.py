import sys

from .base import *

DEBUG = False

ALLOWED_HOSTS = []

# Database settings
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'staging_clean_blog',
            'USER': '',
            'PASSWORD': get_secrets('DATABASE_PASS_STAGING'),
            'HOST': 'localhost',
        }
    }