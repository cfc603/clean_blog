import json
from unipath import Path

from django.core.exceptions import ImproperlyConfigured


# Build paths inside the project like this: Path(BASE_DIR, ...)
BASE_DIR = Path(__file__).ancestor(3)


# get secrets from json file
with open(Path(BASE_DIR.parent + '/secrets/secrets.json')) as f:
    secrets = json.loads(f.read())

def get_secrets(setting, secrets=secrets):
    """Get setting variable or return exception"""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = 'Set the {0} enviroment variable'.format(setting)
        raise ImproperlyConfigured


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'clean_blog.urls'

SECRET_KEY = get_secrets('SECRET_KEY')

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
        },
    },
]

WSGI_APPLICATION = 'clean_blog.wsgi.application'


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR.parent + '/static')

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(BASE_DIR.parent + '/media')


STAGING_URL = 'clean_blog-staging.trevorwatson.me'
PRODUCTION_URL = ''