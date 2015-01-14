"""Django settings for django-generic-filters demo project."""
from os.path import abspath, dirname, join


# Configure some relative directories.
demoproject_dir = dirname(abspath(__file__))
demo_dir = dirname(demoproject_dir)
root_dir = dirname(demo_dir)
data_dir = join(root_dir, 'var')


# Mandatory settings.
ROOT_URLCONF = 'demoproject.urls'
WSGI_APPLICATION = 'demoproject.wsgi.application'


# Database.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(data_dir, 'db.sqlite'),
    }
}


# Required.
SECRET_KEY = "This is a secret made public on project's repository."

# Media and static files.
MEDIA_ROOT = join(data_dir, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = join(data_dir, 'static')
STATIC_URL = '/static/'


# Applications.
INSTALLED_APPS = (
    # Standard Django applications.
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # The actual django-generic-filters demo.
    'django_genericfilters',
    'demoproject',
    'demoproject.filter',
    # For test purposes. The demo project is part of
    # django-generic-filters test suite.
    'django_nose',
)


# Default middlewares. You may alter the list later.
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    'django.core.context_processors.request',
    "django.contrib.messages.context_processors.messages")

# Development configuration.
DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--verbose',
             '--nocapture',
             '--with-id',  # allows --failed which only reruns failed tests
             '--id-file=%s' % join(data_dir, 'noseids'),
             '--with-doctest',
             '--with-xunit',
             '--xunit-file=%s' % join(data_dir, 'nosetests.xml'),
             '--with-coverage',
             '--cover-erase',
             '--cover-package=django_genericfilters',
             '--no-path-adjustment',
             '--all-modules']
