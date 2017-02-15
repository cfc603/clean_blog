import sys

from .base import *

DEBUG = False

ALLOWED_HOSTS = [STAGING_URL,]

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
            'NAME': 'cfc$clean_blog',
            'USER': 'clean_blog',
            'PASSWORD': get_secrets('DATABASE_PASS_STAGING'),
            'HOST': 'cfc.mysql.pythonanywhere-services.com',
        }
    }