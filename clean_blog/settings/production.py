from .base import *

DEBUG = False

ALLOWED_HOSTS = [PRODUCTION_URL, ]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'salesranktable$clean_blog',
        'USER': 'salesranktable',
        'PASSWORD': get_secrets('DATABASE_PASS_PRODUCTION'),
        'HOST': 'salesranktable.mysql.pythonanywhere-services.com',
    }
}

# SECURE_SSL_REDIRECT = True