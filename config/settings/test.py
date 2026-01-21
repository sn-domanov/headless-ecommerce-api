# config/settings/test.py
from .base import *

SECRET_KEY = "7bhw!2f&^aooro4yy@i)a!+9l2(9y5lawy%1gn9%2b(=8ikr81"

DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# MD5 is cryptographically broken, but extremely fast. Use for tests only.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Collects emails in django.core.mail.outbox
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# MEDIA_ROOT = BASE_DIR / "test-media"
