from django.apps import AppConfig


class AuthsConfig(AppConfig):
    """Authentication and custom user model."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "apps.auths"
