import random
import time
from typing import Any

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post, Tag


class Command(BaseCommand):
    """Fill the database with fake users, categories, tags, posts and comments."""

    help = "Fill the database with fake data."

    DEFAULT_USERS = 20
    DEFAULT_POSTS = 100
    DEFAULT_COMMENTS = 500

    SEED_PASSWORD = "password123"
    EMAIL_DOMAIN = "example.com"

    INACTIVE_USERS_SHARE = 0.15
    STAFF_USERS_SHARE = 0.1
    PUBLISHED_SHARE = 0.7
    NO_CATEGORY_SHARE = 0.1
    MIN_TAGS_PER_POST = 0
    MAX_TAGS_PER_POST = 5
    TITLE_WORDS = 6
    POST_PARAGRAPHS = 3
    MIN_COMMENT_SENTENCES = 1
    MAX_COMMENT_SENTENCES = 3
    FIRST_DUPLICATE_SUFFIX = 2

    SUMMARY_LABEL_WIDTH = 11
    SUMMARY_COUNT_WIDTH = 4

    CATEGORY_NAMES = (
        "Python",
        "Django",
        "DevOps",
        "Databases",
        "Frontend",
        "Testing",
        "Security",
        "Career",
    )
    TAG_NAMES = (
        "orm", "api", "rest", "docker", "git", "linux", "sql", "redis",
        "celery", "pytest", "async", "auth", "cache", "admin", "tips",
        "beginner", "advanced", "deploy", "typing", "performance",
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users",
            type=int,
            default=self.DEFAULT_USERS,
            help="Number of users to create",
        )
        parser.add_argument(
            "--posts",
            type=int,
            default=self.DEFAULT_POSTS,
            help="Number of posts to create",
        )
        parser.add_argument(
            "--comments",
            type=int,
            default=self.DEFAULT_COMMENTS,
            help="Number of comments to create",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]
        clear: bool = options["clear"]

        self._validate_counts(users_count, posts_count, comments_count)
        self.fake: Faker = Faker()
        started_at: float = time.perf_counter()

        with transaction.atomic():
            if clear:
                self._clear()

            created: dict[str, int] = {
                "Users": self._create_users(users_count),
                "Categories": self._create_categories(),
                "Tags": self._create_tags(),
                "Posts": self._create_posts(posts_count),
                "Comments": self._create_comments(comments_count),
            }

        self._print_summary(created)
        elapsed: float = time.perf_counter() - started_at
        self.stdout.write(self.style.SUCCESS(f"Done in {elapsed:.2f} seconds"))

    def _print_summary(self, created: dict[str, int]) -> None:
        for label, count in created.items():
            self.stdout.write(
                f"{label + ':':<{self.SUMMARY_LABEL_WIDTH}}"
                f"{count:>{self.SUMMARY_COUNT_WIDTH}} created"
            )

    def _validate_counts(self, users: int, posts: int, comments: int) -> None:
        for name, value in (("users", users), ("posts", posts), ("comments", comments)):
            if value < 0:
                raise CommandError(f"--{name} must be 0 or more, got {value}.")

    def _clear(self) -> None:
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("Old data deleted."))

    def _create_users(self, count: int) -> int:
        password: str = make_password(self.SEED_PASSWORD)
        used_emails: set[str] = set(User.objects.values_list("email", flat=True))
        inactive_count: int = int(count * self.INACTIVE_USERS_SHARE)
        staff_count: int = int(count * self.STAFF_USERS_SHARE)

        users: list[User] = []
        for index in range(count):
            first_name: str = self.fake.first_name()
            last_name: str = self.fake.last_name()
            users.append(
                User(
                    email=self._unique_email(first_name, last_name, used_emails),
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    is_active=index >= inactive_count,
                    is_staff=inactive_count <= index < inactive_count + staff_count,
                )
            )
        User.objects.bulk_create(users)
        return len(users)

    def _unique_email(self, first_name: str, last_name: str, used: set[str]) -> str:
        base: str = slugify(f"{first_name} {last_name}").replace("-", ".")
        email: str = f"{base}@{self.EMAIL_DOMAIN}"
        suffix: int = self.FIRST_DUPLICATE_SUFFIX
        while email in used:
            email = f"{base}{suffix}@{self.EMAIL_DOMAIN}"
            suffix += 1
        used.add(email)
        return email

    def _create_categories(self) -> int:
        existing: set[str] = set(Category.objects.values_list("name", flat=True))
        categories: list[Category] = [
            Category(name=name, slug=slugify(name))
            for name in self.CATEGORY_NAMES
            if name not in existing
        ]
        Category.objects.bulk_create(categories)
        return len(categories)

    def _create_tags(self) -> int:
        existing: set[str] = set(Tag.objects.values_list("name", flat=True))
        tags: list[Tag] = [
            Tag(name=name, slug=slugify(name))
            for name in self.TAG_NAMES
            if name not in existing
        ]
        Tag.objects.bulk_create(tags)
        return len(tags)

    def _create_posts(self, count: int) -> int:
        if count == 0:
            return 0

        authors: list[User] = list(User.objects.all())
        if not authors:
            raise CommandError("Cannot create posts: there are no users. Use --users.")

        categories: list[Category] = list(Category.objects.all())
        tags: list[Tag] = list(Tag.objects.all())
        used_slugs: set[str] = set(Post.objects.values_list("slug", flat=True))

        posts: list[Post] = []
        for _ in range(count):
            title: str = self.fake.sentence(nb_words=self.TITLE_WORDS).rstrip(".")
            posts.append(
                Post(
                    author=random.choice(authors),
                    title=title,
                    slug=self._unique_slug(title, used_slugs),
                    body="".join(
                        f"<div>{paragraph}</div><div><br></div>"
                        for paragraph in self.fake.paragraphs(nb=self.POST_PARAGRAPHS)
                    ),
                    category=self._random_category(categories),
                    status=self._random_status(),
                )
            )
        created: list[Post] = Post.objects.bulk_create(posts)

        for post in created:
            tags_count: int = random.randint(
                self.MIN_TAGS_PER_POST, min(self.MAX_TAGS_PER_POST, len(tags))
            )
            post.tags.set(random.sample(tags, k=tags_count))
        return len(created)

    def _unique_slug(self, title: str, used: set[str]) -> str:
        base: str = slugify(title)
        slug: str = base
        suffix: int = self.FIRST_DUPLICATE_SUFFIX
        while slug in used:
            slug = f"{base}-{suffix}"
            suffix += 1
        used.add(slug)
        return slug

    def _random_category(self, categories: list[Category]) -> Category | None:
        if not categories or random.random() < self.NO_CATEGORY_SHARE:
            return None
        return random.choice(categories)

    def _random_status(self) -> str:
        if random.random() < self.PUBLISHED_SHARE:
            return Post.Status.PUBLISHED
        return Post.Status.DRAFT

    def _create_comments(self, count: int) -> int:
        if count == 0:
            return 0

        authors: list[User] = list(User.objects.all())
        if not authors:
            raise CommandError(
                "Cannot create comments: there are no users. Use --users."
            )
        published: list[Post] = list(Post.objects.filter(status=Post.Status.PUBLISHED))
        if not published:
            raise CommandError(
                "Cannot create comments: there are no published posts. Use --posts."
            )

        comments: list[Comment] = [
            Comment(
                post=random.choice(published),
                author=random.choice(authors),
                body=self.fake.paragraph(
                    nb_sentences=random.randint(
                        self.MIN_COMMENT_SENTENCES, self.MAX_COMMENT_SENTENCES
                    ),
                    variable_nb_sentences=False,
                ),
            )
            for _ in range(count)
        ]
        Comment.objects.bulk_create(comments)
        return len(comments)