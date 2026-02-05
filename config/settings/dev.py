from config.settings.base import *

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

# Browsable API is enabled in development environment only
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += (
    "rest_framework.renderers.BrowsableAPIRenderer",
)
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] += (
    # JWT auth via Authorization header. Does nothing in the current setup, disabled.
    # "rest_framework_simplejwt.authentication.JWTAuthentication",
    # Browsable API and Swagger
    "rest_framework.authentication.SessionAuthentication",
)

# Security
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
