from .base import *
import os

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split()
CSRF_TRUSTED_ORIGINS = os.environ["CSRF_TRUSTED_ORIGINS"].split()
SESSION_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.environ["MYSQL_HOST"],
        "USER" : os.environ["MYSQL_USER"],
        "PASSWORD"  : os.environ["MYSQL_PASSWORD"],
        "NAME" : os.environ["MYSQL_DATABASE"],
    }
}

STATIC_ROOT = "/var/www/static"
