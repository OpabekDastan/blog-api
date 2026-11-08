"""Local development settings."""

from settings.base import *  # noqa: F401, F403
from settings.base import BASE_DIR

DEBUG: bool = True
ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]

DATABASES: dict[str, dict] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
