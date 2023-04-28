"""
Django settings for cruise_literature project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

import environ
from django.conf import settings

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Set the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # external apps
    "rest_framework",
    "crispy_forms",
    "crispy_bulma",
    # apps
    "home",
    "document_search",
    "concept_search",
    "users",
    "literature_review",
    "citation_screening",
    "document_classification",
    "organisations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)

ROOT_URLCONF = "cruise_literature.urls"

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    STATIC_DIR,
]

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATE_DIR,
            STATIC_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ALLOW_ROBOTS = env.bool("ALLOW_ROBOTS", default=False)

WSGI_APPLICATION = "cruise_literature.wsgi.application"

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bulma",)

CRISPY_TEMPLATE_PACK = "bulma"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# change to True if you are running this code on M1 Apple Macbook
M1_CHIP = False

AUTH_USER_MODEL = "users.User"

# if True then also search inside CORE publications aggregator
SEARCH_WITH_CORE = True

TEXT_TO_TEXT_API = True

ENTREZ_EMAIL = "YOUR_EMAIL@SERVER.COM"
