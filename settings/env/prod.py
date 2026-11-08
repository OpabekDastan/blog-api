"""Production settings."""

from settings.base import *  # noqa: F401, F403
from settings.conf import (
    ALLOWED_HOSTS as ENV_ALLOWED_HOSTS,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)

DEBUG: bool = False
ALLOWED_HOSTS: list[str] = ENV_ALLOWED_HOSTS

DATABASES: dict[str, dict] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}
