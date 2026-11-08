from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Blog posts, categories, tags and comments."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "apps.blog"
