
"""hw 3: 50 ORM queries to the blog DB"""

# ----------------- lvl 1 first queries --------------------
#python modules
from typing import Any, Callable
#django mod
from django.db.models import QuerySet
#project mod
from apps.blog.models import Category, Post


def categories_by_name() -> QuerySet[Category]:
    """All categories, sorted by name A → Z. """
    return Category.objects.order_by("name")

def  published_posts() -> QuerySet[Post]:
    """Published posts, newest first."""
    return Post.objects.filter(status = Post.Status.PUBLISHED).order_by("-created_at")



QUERIES: dict[int, Callable[..., Any]] = {
    1: categories_by_name,
    2: published_posts
}