#python modules
from datetime import timedelta, datetime, date
from django.db.models.functions import Coalesce, Concat, TruncMonth
from django.utils import timezone
from django.utils import timezone
from typing import Any, Callable
#django mod
from django.db.models import F, Q, Avg, Case, CharField, Count, DateField, Max, Min, QuerySet, Value, When
#project mod
from apps.auths.models import User
from apps.blog.models import Category, Comment, Post, Tag

"""hw 3: 50 ORM queries to the blog DB"""

# ----------------- lvl 1 first queries --------------------

NEWEST_POSTS_LIMIT = 5
FIRST_PAGE = 1
PAGE_SIZE = 10 
EDITED_AFTER = timedelta(hours=1)
UNCATEGORIZED = "Uncategorized"
AVERAGE_DIGITS = 2
TOP_AUTHORS_LIMIT = 5
HOT_MIN_COMMENTS = 10
NORMAL_MIN_COMMENTS = 3 
HOT = "hot"
NORMAL = "normal"
QUIET = "quiet"

def categories_by_name() -> QuerySet[Category]:
    """All categories, sorted by name A → Z. """
    return Category.objects.order_by("name")

def  published_posts() -> QuerySet[Post]:
    """Published posts, newest first."""
    return Post.objects.filter(status = Post.Status.PUBLISHED).order_by("-created_at")

def newest_published_posts() -> QuerySet[Post]:
    """The 5 newest published posts."""
    return published_posts()[:NEWEST_POSTS_LIMIT]

def post_by_slug(slug: str) -> Post | None:
    """The post with this slug, or None if there is no such post. No exceptions."""
    return Post.objects.filter(slug = slug).first()

def active_users_count() -> int:
    """Number of active users. Staff users are not counted."""
    return User.objects.filter(is_active = True, is_staff = False).count()

def has_drafts() -> bool:
    """True if there is at least one draft post."""
    return Post.objects.filter(status = Post.Status.DRAFT).exists()

def published_posts_page(page: int) -> QuerySet[Post]:
    """One page of published posts, newest first. 10 posts per page: page 1 is posts 1–10, page 2 is posts 11–20."""
    start: int = (page - FIRST_PAGE) * PAGE_SIZE
    end: int = start + PAGE_SIZE
    return published_posts()[start:end]
# --- Level 2 — Field Lookups ---


def posts_with_word_in_title(word: str) -> QuerySet[Post]:
    """Posts whose title contains word. Letter case does not matter."""
    return Post.objects.filter(title__icontains = word)


def users_with_email_domain(domain: str) -> QuerySet[User]:
    """Users whose email ends with @ + domain."""
    return User.objects.filter(email__iendswith = f"@{domain}")


def posts_without_category() -> QuerySet[Post]:
    """Posts that have no category."""
    return Post.objects.filter(category__isnull = True)


    """Categories whose slug is in the list slugs."""
def categories_by_slugs(slugs: list[str]) -> QuerySet[Category]:
    return Category.objects.filter(slug__in= slugs )

def posts_in_month(year: int, month: int) -> QuerySet[Post]:
    """Posts created in this month of this year."""

    return Post.objects.filter(created_at__year = year, created_at__month=month)

def posts_last_days(days: int) -> QuerySet[Post]:
    """Posts created in the last days days."""

    since: datetime = timezone.now() - timedelta(days=days)
    return Post.objects.filter(created_at__gte = since)

def posts_between(start: date, end: date) -> QuerySet[Post]:
    """Posts created from start to end (both days included)."""
    return Post.objects.filter(created_at__date__range =( start, end)) 


# --- Level 3 — Queries Across Relations ---


def author_published_posts(email: str) -> QuerySet[Post]:
    """Published posts of the author with this email (case-insensitive)."""

    return published_posts().filter(author__email__iexact = email)


def posts_with_tag(tag_slug: str) -> QuerySet[Post]:
    """Posts that have the tag with this slug."""

    return Post.objects.filter(tags__slug = tag_slug)

def comments_in_category(category_slug: str) -> QuerySet[Comment]:
    """Comments on posts of the category with this slug."""
    return Comment.objects.filter(post__category__slug = category_slug)


def users_with_published_posts() -> QuerySet[User]:
    """Users who have at least one published post. Every user appears once."""
    return User.objects.filter(posts__status = Post.Status.PUBLISHED).distinct()


def posts_without_tags() -> QuerySet[Post]:
    """Posts that have no tags."""
    return Post.objects.filter(tags__isnull=True)


def users_without_comments() -> QuerySet[User]:
    """Users who have never written a comment."""
    return User.objects.filter(comments__isnull = True)


def posts_with_both_tags(first_slug: str, second_slug: str) -> QuerySet[Post]:
    """Posts that have both tags."""
    return Post.objects.filter(tags__slug = first_slug).filter(tags__slug = second_slug)


# --- Level 4 — Q and F ---


def search_posts(text: str) -> QuerySet[Post]:
    """Posts that have text in the title or in the body (case-insensitive)."""
    return Post.objects.filter(Q(title__icontains=text) | Q(body__icontains = text))


def published_posts_missing_info() -> QuerySet[Post]:
    """Published posts that have no category or no tags. Every post appears once."""
    no_category_or_tags: Q = Q(category__isnull=True) | Q(tags__isnull = True)
    return published_posts().filter(no_category_or_tags).distinct()


def edited_posts() -> QuerySet[Post]:
    """Posts that were edited more than 1 hour after they were created."""
    return Post.objects.filter(updated_at__gt = F("created_at")+ EDITED_AFTER)


def comments_by_post_author() -> QuerySet[Comment]:
    """Comments that the author of the post wrote under their own post."""
    return Comment.objects.filter(author = F("post__author"))


def comments_before_post() -> QuerySet[Comment]:
    """Comments created before their post."""
    return Comment.objects.filter(created_at__lt=F("post__created_at"))


# --- Level 5 — values and values_list ---


def published_authors_emails() -> list[str]:
    """Emails of authors who have published posts. Unique, sorted A -> Z."""
    emails: QuerySet = (
        Post.objects.filter(status = Post.Status.PUBLISHED)
        .order_by("author__email")
        .values_list("author__email", flat= True)
        .distinct()
    )
    return list(emails)


def published_posts_overview() -> list[dict[str, Any]]:
    """One dict for each published post with title, author_email, category_name."""
    posts: QuerySet = published_posts().values(
        "title",
        author_email = F("author__email"),
        category_name = Coalesce("category__name", Value(UNCATEGORIZED)),
    )
    return list(posts)

# --- Level 6 — aggregate ---


def posts_stats() -> dict[str, Any]:
    """Total, published, drafts counts, and first/last post dates in one query."""
    return Post.objects.aggregate(
        total = Count("id"),
        published = Count("id", filter=Q(status=Post.Status.PUBLISHED)),
        drafts = Count("id", filter=Q(status=Post.Status.DRAFT)),
        first_post_at = Min("created_at"),
        last_post_at = Max("created_at")
    )


def average_comments_per_post() -> float:
    """Average number of comments on a published post, rounded to 2 digits."""
    posts: QuerySet[Post] = Post.objects.filter(status=Post.Status.PUBLISHED)
    posts = posts.annotate(comment_count = Count("comments"))
    result: dict[str, Any] = posts.aggregate(average=Avg("comment_count",default=0.0))
    return round(result["average"], AVERAGE_DIGITS)


# --- Level 7 — annotate ---


def categories_with_post_count() -> QuerySet[Category]:
    """Every category with post_count. Most posts first, then by name."""
    categories: QuerySet[Category] = Category.objects.annotate(post_count = Count("posts"))
    return categories.order_by("-post_count", "name")


def categories_with_published_count() -> QuerySet[Category]:
    """Every category with published_count (including 0)."""
    only_published: Q = Q(posts__status = Post.Status.PUBLISHED)
    return Category.objects.annotate(
        published_count = Count("posts", filter=only_published)
    )


def top_authors() -> QuerySet[User]:
    """Top 5 users by number of published posts, with published_count."""
    only_published: Q = Q(posts__status = Post.Status.PUBLISHED)
    users: QuerySet[User] = User.objects.annotate(
        published_count = Count("posts", filter=only_published)
    )
    return users.order_by("-published_count", "email")[:TOP_AUTHORS_LIMIT]


def popular_tags(min_posts: int) -> QuerySet[Tag]:
    """Tags used in at least min_posts posts, with post_count."""
    tags: QuerySet[Tag] = Tag.objects.annotate(post_count = Count("posts"))
    return tags.order_by("-post_count", "name")


def posts_per_status() -> list[dict[str, Any]]:
    """Number of posts for each status."""
    statuses: QuerySet = Post.objects.values("status").annotate(count= Count("id"))
    return list(statuses.order_by("status"))


def users_activity() -> QuerySet[User]:
    """Every user with accurate post_count and comment_count."""
    return User.objects.annotate(
        post_count = Count("posts", distinct=True),
        comment_count = Count("comments", distinct=True),
    )


# --- Level 8 — Database Functions and Conditions ---


def search_users_by_full_name(text: str) -> QuerySet[User]:
    """Users whose full name ("First Last") contains text (case-insensitive)."""
    users: QuerySet[User] = User.objects.annotate(
        full_name = Concat("first_name", Value(" "), "last_name")
    )
    return users.filter(full_name__icontains = text)


def published_posts_per_month() -> list[dict[str, Any]]:
    """Number of published posts in each month, oldest month first."""
    posts: QuerySet[Post] = Post.objects.filter(status = Post.Status.PUBLISHED)
    posts = posts.annotate(month = TruncMonth("created_at", output_field=DateField()))
    months: QuerySet = posts.values("month").annotate(count = Count("id"))
    return list(months.order_by("month"))

def posts_with_popularity() -> QuerySet[Post]:
    """Every post with comment_count and popularity (hot, normal, quiet)."""
    return Post.objects.annotate(
        comment_count = Count("comments"),
    popularity = Case(
        When(comment_count__gte = HOT_MIN_COMMENTS, then = Value(HOT)),
        When(comment_count__gte=NORMAL_MIN_COMMENTS, then=Value(NORMAL)),
        default=Value(QUIET),
        output_field=CharField(),
    ),

    )


# --- Level 9 — Changing Data ---


def get_or_create_tag(name: str) -> tuple[Tag, bool]:
    """Return the tag with this name, creating it with slug if needed."""
    return (Tag(), False)


def publish_old_drafts(days: int) -> int:
    """Publish all drafts older than days days in one SQL query."""
    return 0


def tag_category_posts(category_slug: str, tag_slug: str) -> int:
    """Add the tag to every post of the category. Return posts count in category."""
    return 0


def merge_categories(source_slug: str, target_slug: str) -> int:
    """Move all posts from source category to target category and delete source."""
    return 0


def delete_inactive_users_comments() -> int:
    """Delete all comments written by inactive users. Return deleted count."""
    return 0


# --- Level 10 — select_related and prefetch_related ---


def published_feed() -> list[str]:
    """50 newest published posts as 'title | author email | category name'."""
    return []


def newest_posts_with_tags() -> list[str]:
    """20 newest posts as 'title: tag1, tag2'."""
    return []


def categories_with_published_posts() -> dict[str, list[str]]:
    """{category name: [titles of its published posts, newest first]}."""
    return {}


# --- Level 11 — Subquery and Exists ---


def posts_with_last_comment() -> QuerySet[Post]:
    """Published posts annotated with last_comment body."""
    return []


def posts_with_staff_comments() -> QuerySet[Post]:
    """Posts with at least one comment from a staff user using Exists."""
    return []


def users_with_draft_as_latest_post() -> QuerySet[User]:
    """Users whose newest post is a draft, annotated with latest_post_status."""
    return []
QUERIES: dict[int, Callable[..., Any]] = {
    1: categories_by_name,
    2: published_posts,
    3: newest_published_posts,
    4: post_by_slug,
    5: active_users_count, 
    6: has_drafts, 
    7: published_posts_page,
    8: posts_with_word_in_title,
    9: users_with_email_domain,
    10: posts_without_category,
    11: categories_by_slugs,
    12: posts_in_month,
    13: posts_last_days,
    14: posts_between,
    15: author_published_posts,
    16: posts_with_tag,
    17: comments_in_category,
    18: users_with_published_posts,
    19: posts_without_tags,
    20: users_without_comments,
    21: posts_with_both_tags,
    22: search_posts,
    23: published_posts_missing_info,
    24: edited_posts,
    25: comments_by_post_author,
    26: comments_before_post,
    27: published_authors_emails,
    28: published_posts_overview,
    29: posts_stats,
    30: average_comments_per_post,
    31: categories_with_post_count,
    32: categories_with_published_count,
    33: top_authors,
    34: popular_tags,
    35: posts_per_status,
    36: users_activity,
    37: search_users_by_full_name,
    38: published_posts_per_month,
    39: posts_with_popularity,
}