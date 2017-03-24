from .base import *

DEBUG = False

ALLOWED_HOSTS = ['blog.trevorwatson.info',]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clean_blog',
        'USER': 'clean_blog',
        'PASSWORD': get_secrets('DATABASE_PASS_PRODUCTION'),
        'HOST': 'localhost',
    }
}
