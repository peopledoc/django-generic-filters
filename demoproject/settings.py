"""Django settings for django-generic-filters demo project."""

from os import environ
from os.path import abspath, dirname, join

# Configure some relative directories.
demoproject_dir = dirname(abspath(__file__))
root_dir = dirname(demoproject_dir)
data_dir = join(root_dir, "var")


# Mandatory settings.
ROOT_URLCONF = "demoproject.urls"
WSGI_APPLICATION = "demoproject.wsgi.application"


# Database.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": environ.get("PGDATABASE", "django_generic_filters")
        # Configure database using standard PG* environment variables
        # https://www.postgresql.org/docs/current/libpq-envars.html
    }
}

# Template.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": True,
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ),
        },
    },
]


# Required.
SECRET_KEY = "This is a secret made public on project's repository."

# Media and static files.
MEDIA_ROOT = join(data_dir, "media")
MEDIA_URL = "/media/"
STATIC_ROOT = join(data_dir, "static")
STATIC_URL = "/static/"


# Applications.
INSTALLED_APPS = (
    # Standard Django applications.
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # The actual django-generic-filters demo.
    "django_genericfilters",
    "demoproject",
    "demoproject.filter",
)


# Default middlewares. You may alter the list later.
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# Development configuration.
DEBUG = True

USE_TZ = True
