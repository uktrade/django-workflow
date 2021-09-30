"""Django settings for django_workflow.

NB: This is a minimal settings module and is only for django_workflow migration
creation, do not try to serve a site using this configuration.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'XXX'
DEBUG = True
ALLOWED_HOSTS = []


class DummyWorkflow:
    pass


DJANGO_WORKFLOWS = {
    "dummy": DummyWorkflow,
}


# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_workflow',
]

MIDDLEWARE = []
TEMPLATES = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'