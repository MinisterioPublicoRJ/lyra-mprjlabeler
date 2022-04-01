"""
Django settings for mprjlabeler project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import sys
import urllib

from dj_database_url import parse as db_url
from django.contrib import messages
from decouple import config
from dj_database_url import parse as dburl
from kombu.utils.url import quote

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'bt4)*8x(4aza76rh7kq53w55dap350#l%ka7iu0&g+&mmct22%'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ordered_model',
    'labeler',
    'filtro',
    'nested_admin',
]

DEV_PARTY_APPS = [
    'debug_toolbar',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DEV_MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

if config("AMBIENTE", None) == "desenvolvimento":
    INSTALLED_APPS += DEV_PARTY_APPS
    MIDDLEWARE += DEV_MIDDLEWARE

    # necessário para o debug_toobar
    INTERNAL_IPS = [
        # ...
        "127.0.0.1",
        # ...
    ]

ROOT_URLCONF = 'mprjlabeler.urls'

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'mprjlabeler.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

default_dburl = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

TESTING = sys.argv[1:2] == ['test']
if not TESTING:
    DATABASES = {
        'default': config('DATABASE_URL', default=default_dburl, cast=db_url)
    }
else:
    DATABASES = {
        'default': {'ENGINE': 'django.db.backends.sqlite3',
                    "TEST": {
                        "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
                    }
                    }, }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTH_MPRJ = 'http://apps.mprj.mp.br/mpmapas/api/authentication'
AITJ_MPRJ_USERINFO = 'http://apps.mprj.mp.br/mpmapas/api/authenticate'
LOGIN_URL = '/login/'

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# # ### Celery
CELERY_TASK_QUEUE = config("CELERY_QUEUE", None)

CELERY_BROKER_URL = 'sqs://{AWS_ACCESS_KEY_ID}:{AWS_SECRET_ACCESS_KEY}@'.format(
    AWS_ACCESS_KEY_ID=quote(config('AWS_ACCESS_KEY_ID'), safe=''),
    AWS_SECRET_ACCESS_KEY=quote(config('AWS_SECRET_ACCESS_KEY'), safe='')
    )

BROKER_URL = CELERY_BROKER_URL

BROKER_TRANSPORT = 'sqs'
BROKER_TRANSPORT_OPTIONS = {
    'region': 'us-east-1',
}

CELERY_DEFAULT_QUEUE = config("CELERY_QUEUE", None)
CELERY_QUEUES = {
    CELERY_DEFAULT_QUEUE: {
        'exchange': CELERY_DEFAULT_QUEUE,
        'binding_key': CELERY_DEFAULT_QUEUE,
    }
}

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'db+sqlite:///' + os.path.join(BASE_DIR, 'results.sqlite')
CELERY_TASK_SERIALIZER = 'json'


if config("AMBIENTE", None) == "producao":
    DEBUG = False

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

CLASSIFICADOR_CHUNKSIZE = config(
    'CLASSIFICADOR_CHUNKSIZE',
    default=500,
    cast=int
)

ID_MNI = config("ID_MNI")
SENHA_MNI = config("SENHA_MNI")

NOME_FILTRO_PETICAO_INICIAL = "Petição inicial"
MININUM_DOC_COUNT_LDA = config("MININUM_DOC_COUNT_LDA", cast=int, default=1_000)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'filtro': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
