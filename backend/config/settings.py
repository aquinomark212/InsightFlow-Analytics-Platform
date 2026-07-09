from pathlib import Path
from datetime import timedelta
import os 
from dotenv import load_dotenv
from corsheaders.defaults import default_headers
load_dotenv()  # Load environment variables from .env file
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ulec)+vvfe6hnzsu#79=yr(sbt0*a6b3atcm3lui^6s7abi0ji'

# SECURITY WARNING: don't run with debug turned on in production!

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',                # Django REST Framework for APIs
    'rest_framework.authtoken',
    'core',                          # Your custom app

    'django.contrib.sites',          # REQUIRED

    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    

    # dj-rest-auth
    'dj_rest_auth',

    #redis
    'django_rq',

    'corsheaders',
    'channels',
   
 
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# DRF settings (Authentication)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        "customResponse.auth.CookieJWTAuthentication",  # Custom cookie-based JWT authentication
    ),
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Expiration time for access token
    'AUTH_HEADER_TYPES': ('Bearer',),  # JWT token is passed as 'Bearer <token>'
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DB_NAME=os.getenv("DB_NAME", "insightflow")
DB_USER=os.getenv("DB_USER", "postgres")
DB_PASSWORD=os.getenv("DB_PASSWORD", "admin")
DB_HOST=os.getenv("DB_HOST")
DB_PORT=int(os.getenv("DB_PORT", 5432))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,       # your database name
        'USER': DB_USER,           # your DB username
        'PASSWORD': DB_PASSWORD,  # your DB password
        'HOST': DB_HOST, # "localhost" change this if you want to run Local Server
        'PORT': DB_PORT,
    }
}

REDIS_HOST=os.getenv("REDIS_HOST", "localhost")
REDIS_PORT=int(os.getenv("REDIS_PORT", "6379"))

# Redis settings for django-rq
RQ_QUEUES = {
    'default': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    }, 
    'events': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 1,
        'DEFAULT_TIMEOUT': 360,
    },
    'cache': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 1,
        'DEFAULT_TIMEOUT': 360,
    },
    'analytics': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 1,
        'DEFAULT_TIMEOUT': 360,
    },
    'notifications': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 1,
        'DEFAULT_TIMEOUT': 360,
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

LOGIN_REDIRECT_URL = '/accounts/google/login/' 

RQ = {
    "WORKER_CLASS": "rq.worker.SimpleWorker"
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-my-secret-key",
]

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        }
    }
}





