from .base import *

DEBUG = False

ALLOWED_HOSTS = []

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clean_blog',
        'USER': '',
        'PASSWORD': get_secrets('DATABASE_PASS_PRODUCTION'),
        'HOST': 'localhost',
    }
}
