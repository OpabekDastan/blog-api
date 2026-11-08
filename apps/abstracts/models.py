from django.db import models


class AbstractBaseModel(models.Model):
    """Abstract model that adds creation and update timestamps."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="created at",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="updated at",
    )

    class Meta:
        abstract = True
