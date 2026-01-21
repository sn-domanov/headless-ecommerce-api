from config.settings.base import *

SECRET_KEY = "django-insecure-^gz5)3m(p=$*@q%u(d5q@8!y!f5bo9(6b&#)#g4q_a=ak1kgoj"

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
