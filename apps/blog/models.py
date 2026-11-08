from django.conf import settings
from django.db import models

from apps.abstracts.models import AbstractBaseModel


class Category(AbstractBaseModel):
    """Post category."""

    NAME_MAX_LEN = 100
    SLUG_MAX_LEN = 100

    name = models.CharField(
        max_length=NAME_MAX_LEN,
        unique=True,
        verbose_name="name",
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LEN,
        unique=True,
        verbose_name="slug",
    )

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Tag(AbstractBaseModel):
    """Post tag."""

    NAME_MAX_LEN = 50
    SLUG_MAX_LEN = 50

    name = models.CharField(
        max_length=NAME_MAX_LEN,
        unique=True,
        verbose_name="name",
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LEN,
        unique=True,
        verbose_name="slug",
    )

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Post(AbstractBaseModel):
    """Blog post."""

    TITLE_MAX_LEN = 200
    SLUG_MAX_LEN = 200
    STATUS_MAX_LEN = 10

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="author",
    )
    title = models.CharField(
        max_length=TITLE_MAX_LEN,
        verbose_name="title",
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LEN,
        unique=True,
        verbose_name="slug",
    )
    body = models.TextField(
        verbose_name="body",
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="category",
    )
    tags = models.ManyToManyField(
        to=Tag,
        blank=True,
        related_name="posts",
        verbose_name="tags",
    )
    status = models.CharField(
        max_length=STATUS_MAX_LEN,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="status",
    )

    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class Comment(AbstractBaseModel):
    """Comment left by a user under a post."""

    STR_BODY_PREVIEW_LEN = 30

    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="post",
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="author",
    )
    body = models.TextField(
        verbose_name="body",
    )

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"
        ordering = ("created_at",)

    def __str__(self) -> str:
        preview: str = self.body[: self.STR_BODY_PREVIEW_LEN]
        return f"Comment {self.pk} on post {self.post_id}: {preview}"
