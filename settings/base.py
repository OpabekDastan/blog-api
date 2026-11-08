"""Base settings shared by every environment."""

from pathlib import Path

from settings.conf import SECRET_KEY  # noqa: F401

# ---------- Paths ----------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
LOGS_DIR: Path = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ---------- Security ----------
DEBUG: bool = False
ALLOWED_HOSTS: list[str] = []

# ---------- Applications ----------
DJANGO_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS: list[str] = []

PROJECT_APPS: list[str] = [
    "apps.abstracts",
    "apps.auths",
    "apps.blog",
]

INSTALLED_APPS: list[str] = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# ---------- Middleware ----------
MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------- URLs / WSGI / ASGI ----------
ROOT_URLCONF: str = "settings.urls"
WSGI_APPLICATION: str = "settings.wsgi.application"
ASGI_APPLICATION: str = "settings.asgi.application"

# ---------- Templates ----------
TEMPLATES: list[dict] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------- Auth ----------
AUTH_USER_MODEL: str = "auths.User"

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------- Internationalization ----------
LANGUAGE_CODE: str = "en-us"
TIME_ZONE: str = "UTC"
USE_I18N: bool = True
USE_TZ: bool = True

# ---------- Static files ----------
STATIC_URL: str = "static/"
STATIC_ROOT: Path = BASE_DIR / "static"

# ---------- Database defaults ----------
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# ---------- Logging ----------
LOGGING: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "app.log",
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}
