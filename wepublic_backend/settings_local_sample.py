import os


SECRET_KEY = 'secretsecretsecret'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<DATABASE NAME>',
        'USER': '<username >',
        'PASSWORD': '<pw>',
        'HOST': '<DNS or IP of postgres server>',
        'PORT': '<Port of PSQL server>',
    }
}

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'
