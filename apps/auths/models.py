from typing import Any

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from apps.abstracts.models import AbstractBaseModel


class CustomUserManager(BaseUserManager):
    """Manager for User where email is the unique identifier."""

    def _create_user(
        self,
        email: str,
        password: str | None,
        **extra_fields: Any,
    ) -> "User":
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user: User = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """Custom user that logs in with email instead of username."""

    FIRST_NAME_MAX_LEN = 50
    LAST_NAME_MAX_LEN = 50

    email = models.EmailField(
        unique=True,
        verbose_name="email address",
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LEN,
        verbose_name="first name",
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LEN,
        verbose_name="last name",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="active",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="staff status",
    )

    objects: CustomUserManager = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name
