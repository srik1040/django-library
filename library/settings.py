"""
Django settings for library project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import dj_database_url
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
LOGIN_URL = '/'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w7)qdx(89m5*d5zyisy5j9+3sg+@i1*jfddbx^i^2em^@y8rlv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2',
    'library_app',
    'fandjango',
    'json_field',
    # 'templatetags'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fandjango.middleware.FacebookMiddleware',
    'fandjango.middleware.FacebookWebMiddleware',
)

ROOT_URLCONF = 'library.urls'

WSGI_APPLICATION = 'library.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'sqlite3.db'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'name',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
        # 'NAME': os.path.join(BASE_DIR, 'sqlite3.db'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

# import dj_database_url

DATABASES['default'] = dj_database_url.config()


TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.contrib.messages.context_processors.messages",
                               # "library_app.context_processor.is_authenticated"
                               "django.core.context_processors.request",
)

FACEBOOK_APPLICATION_ID = 970424339652057
FACEBOOK_APPLICATION_SECRET_KEY = 'e250adbd77eb67fbf006d7faf08cb66a'
FACEBOOK_APPLICATION_NAMESPACE = 'library_django'

FANDJANGO_SITE_URL = 'http://django-library.herokuapp.com/fb/'
# FANDJANGO_SITE_URL = 'http://localhost:8888/fb/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'library_app.auth_backend.PasswordlessAuthBackend',
)