from .base import *

DEBUG = False

ALLOWED_HOSTS = [PRODUCTION_URL, ]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clean_blog',
        'USER': 'admin',
        'PASSWORD': get_secrets('DATABASE_PASS_PRODUCTION'),
        'HOST': 'localhost',
    }
}

# SECURE_SSL_REDIRECT = True