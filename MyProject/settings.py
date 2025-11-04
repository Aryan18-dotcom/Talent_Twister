from pathlib import Path
import os
from decouple import config, Csv
import dj_database_url
import environ # Recommended to use django-environ instead of decouple for Django projects

# Initialize django-environ (if you choose to use it, otherwise keep decouple)
# env = environ.Env(
#     DEBUG=(bool, False)
# )
# environ.Env.read_env() # Reads the .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# Load SECRET_KEY from environment variable
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# Set DEBUG based on environment variable, default to False for production
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS for production. Get from environment or specify your Render URL.
# Use Csv for multiple hosts from a comma-separated string
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
# If you are not using Csv, you can use:
# ALLOWED_HOSTS = ['your-app-name.onrender.com',]


# Application definition

INSTALLED_APPS = [
    'daphne', # Use Daphne for Channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'crispy_forms',
    'widget_tweaks',
    # Your apps
    'users',
    'chat',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # ⬅️ ADD THIS FOR STATIC FILES
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Talent_Twister.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templets'], # Use Pathlib for DIRS
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Talent_Twister.wsgi.application'

# Channels settings for ASGI (needed for Daphne)
ASGI_APPLICATION = "Talent_Twister.asgi.application" # Ensure you have an asgi.py

CHANNEL_LAYERS = {
    "default": {
        # For production, use Redis. Render provides managed Redis.
        # You'll get a REDIS_URL environment variable from Render Redis.
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "URL": config('REDIS_URL', default='redis://localhost:6379'), # Use environment variable
        },
    },
}


# Database
# Use PostgreSQL for production on Render
DATABASES = {
    'default': dj_database_url.config(
        # Fallback to sqlite for local dev if DATABASE_URL is not set
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600 # Recommended setting for persistent connections
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# ✅ Static Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Collect static files here for WhiteNoise

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configure WhiteNoise to compress static assets
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ✅ Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings (Using python-decouple for config)
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
