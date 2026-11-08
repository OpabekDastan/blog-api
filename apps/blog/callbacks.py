import json
from typing import Any

from django.db.models import Count, QuerySet
from django.http import HttpRequest

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post
from settings.conf import ENV_ID

PRODUCTION_ENV_ID = "prod"
STATUS_FILTER_PARAM = "status__exact"
TOP_AUTHORS_LIMIT = 5
PERCENT = 100


def environment_callback(request: HttpRequest) -> list[str]:
    """Badge in the header: Local (orange) or Production (red)."""
    if ENV_ID == PRODUCTION_ENV_ID:
        return ["Production", "danger"]
    return ["Local", "warning"]


def drafts_badge(request: HttpRequest) -> int:
    """Number of drafts shown next to Posts in the sidebar."""
    return Post.objects.filter(status=Post.Status.DRAFT).count()


def is_superuser(request: HttpRequest) -> bool:
    """Show the item only to superusers."""
    return request.user.is_superuser


def all_posts_tab_active(request: HttpRequest) -> bool:
    """The All tab is active when no status filter is applied."""
    return STATUS_FILTER_PARAM not in request.GET


def _percent(part: int, total: int) -> int:
    if total == 0:
        return 0
    return round(part * PERCENT / total)


def dashboard_callback(request: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
    """Add statistics for the custom admin dashboard."""
    posts_total: int = Post.objects.count()
    published: int = Post.objects.filter(status=Post.Status.PUBLISHED).count()
    drafts: int = posts_total - published

    categories: QuerySet[Category] = Category.objects.annotate(
        posts_total=Count("posts")
    ).order_by("-posts_total")
    top_authors: QuerySet[User] = (
        User.objects.annotate(posts_total=Count("posts"))
        .filter(posts_total__gt=0)
        .order_by("-posts_total")[:TOP_AUTHORS_LIMIT]
    )

    context.update(
        {
            "kpis": [
                {"title": "Users", "value": User.objects.count()},
                {"title": "Published posts", "value": published},
                {"title": "Drafts", "value": drafts},
                {"title": "Comments", "value": Comment.objects.count()},
            ],
            "category_chart": json.dumps(
                {
                    "labels": [category.name for category in categories],
                    "datasets": [
                        {
                            "label": "Posts",
                            "data": [category.posts_total for category in categories],
                        }
                    ],
                }
            ),
            "top_authors_table": {
                "headers": ["Author", "Email", "Posts"],
                "rows": [
                    [author.get_full_name(), author.email, author.posts_total]
                    for author in top_authors
                ],
            },
            "status_progress": [
                {
                    "title": "Published",
                    "description": f"{published} posts",
                    "value": _percent(published, posts_total),
                },
                {
                    "title": "Drafts",
                    "description": f"{drafts} posts",
                    "value": _percent(drafts, posts_total),
                },
            ],
        }
    )
    return context