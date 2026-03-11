import os
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-for-production")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS_ENV = os.getenv("DJANGO_ALLOWED_HOSTS", "").strip()
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(",") if host.strip()]
elif RAILWAY_PUBLIC_DOMAIN:
    # Автоматически подхватываем Railway-домен, если переменная DJANGO_ALLOWED_HOSTS не задана.
    ALLOWED_HOSTS = [RAILWAY_PUBLIC_DOMAIN]
elif DEBUG:
    # В локальной сети это позволяет открывать сайт по IP компьютера преподавателя.
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = []

# CSRF trusted origins for Railway and other deployments
CSRF_TRUSTED_ORIGINS_ENV = os.getenv("CSRF_TRUSTED_ORIGINS", "").strip()
if CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(",") if origin.strip()]
elif RAILWAY_PUBLIC_DOMAIN:
    # Automatically add Railway domain
    CSRF_TRUSTED_ORIGINS = [f"https://{RAILWAY_PUBLIC_DOMAIN}"]
else:
    CSRF_TRUSTED_ORIGINS = []

# Публичный адрес сервера (опционально), например: http://192.168.1.25:8000
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "teacher",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "mysite.wsgi.application"
# Database configuration
# Важно: в Railway нужно использовать PostgreSQL (DATABASE_URL),
# иначе SQLite хранится на эфемерном диске и данные пропадают после redeploy.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_RAILWAY = bool(os.getenv("RAILWAY_ENVIRONMENT_NAME") or os.getenv("RAILWAY_PROJECT_ID") or os.getenv("RAILWAY_SERVICE_ID"))

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
elif IS_RAILWAY or not DEBUG:
    # Запрещаем тихий fallback на SQLite в production,
    # чтобы не терять викторины/уроки после обновлений.
    raise ImproperlyConfigured(
        "DATABASE_URL не задан. Для production/Railway подключите PostgreSQL и задайте DATABASE_URL. "
        "SQLite в production приведет к потере данных при redeploy."
    )
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = []
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = '/teacher/'

# OpenAI API settings for homework generation
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
USE_OPENAI_FOR_HOMEWORK = bool(OPENAI_API_KEY)
