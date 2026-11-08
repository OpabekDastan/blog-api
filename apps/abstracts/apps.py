from django.apps import AppConfig


class AbstractsConfig(AppConfig):
    """Holds abstract models shared across the project."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "apps.abstracts"
