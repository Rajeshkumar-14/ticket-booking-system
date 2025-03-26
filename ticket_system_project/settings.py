import os
from pathlib import Path
import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
env = environ.Env(
    # Define default types for environment variables to avoid type mismatches
    DEBUG=(bool, False),
    DJANGO_LOGLEVEL=(str, "INFO"),
    EMAIL_PORT=(int, 587),
    DATABASE_PORT=(str, ""),
)
env.read_env(os.path.join(BASE_DIR, ".env"))

# Security settings
SECRET_KEY = env.str("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in the environment variables.")

DEBUG = env.bool("DEBUG")

FIELD_ENCRYPTION_KEY = env.str("FIELD_ENCRYPTION_KEY")
if not FIELD_ENCRYPTION_KEY:
    raise ValueError("FIELD_ENCRYPTION_KEY must be set in the environment variables.")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "crispy_forms",
    "django_redis",  # Added for Redis caching
    "encrypted_model_fields",  # Added for encrypted fields
    # Your apps
    "apps.authentication",
    "apps.administration",
    "apps.core",
    "apps.bus",
    "apps.train",
    "apps.flight",
    "apps.support",
]

CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "custom_middleware.performance_middleware.PerformanceMiddleware",
    "custom_middleware.request_logging_middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "ticket_system_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Use Path for consistency
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

WSGI_APPLICATION = "ticket_system_project.wsgi.application"
ASGI_APPLICATION = "ticket_system_project.asgi.application"

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://localhost", "http://127.0.0.1"])

# Database
DATABASES = {
    "default": {
        "ENGINE": env.str("DATABASE_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env.str("DATABASE_NAME", default=BASE_DIR / "db.sqlite3"),
        "USER": env.str("DATABASE_USERNAME", default=""),
        "PASSWORD": env.str("DATABASE_PASSWORD", default=""),
        "HOST": env.str("DATABASE_HOST", default=""),
        "PORT": env.str("DATABASE_PORT", default=""),
        "OPTIONS": {
            "timeout": 20,  # Add timeout for database connections
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"  # Ensure leading slash for consistency
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "static_root"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",  # Add date format for clarity
        },
    },
    "handlers": {
        "file": {
            "level": env.str("DJANGO_LOGLEVEL").upper(),
            "class": "logging.handlers.RotatingFileHandler",  # Use RotatingFileHandler for log rotation
            "filename": BASE_DIR / "system-log.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file", "console"] if env.bool("DEBUG") else ["file"],
        "level": env.str("DJANGO_LOGLEVEL").upper(),
    },
}

# Email
EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env.str("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="noreply@ticketbooking.com")

# Security settings
SECURE_SSL_REDIRECT = not env.bool("DEBUG")
SESSION_COOKIE_SECURE = not env.bool("DEBUG")
CSRF_COOKIE_SECURE = not env.bool("DEBUG")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000 if not env.bool("DEBUG") else 0  # 1 year for HSTS in production
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.str("REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,  # Add timeout for Redis connections
            "SOCKET_TIMEOUT": 5,
        },
    }
}

# Celery settings
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # Improve Celery startup reliability
CELERY_TASK_TRACK_STARTED = True  # Track task start time
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes timeout for tasks
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft timeout