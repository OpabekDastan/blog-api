from django.contrib import admin
from django.db import models
from django.db.models import Count, Prefetch, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.text import Truncator
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    MultipleRelatedDropdownFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display
from unfold.sections import TableSection

from apps.blog.models import Category, Comment, Post, Tag


class CategoryPostsSection(TableSection):
    """Posts of the category, shown when the row is expanded."""

    verbose_name = "Posts"
    related_name = "posts"
    fields = ("title", "status", "created_at")


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin for post categories."""

    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_sections = (CategoryPostsSection,)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Category]:
        return (
            super()
            .get_queryset(request)
            .annotate(posts_total=Count("posts"))
            .prefetch_related("posts")
        )

    @display(description="Posts", ordering="posts_total")
    def posts_count(self, obj: Category) -> int:
        return obj.posts_total


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    """Admin for post tags."""

    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request: HttpRequest) -> QuerySet[Tag]:
        return super().get_queryset(request).annotate(posts_total=Count("posts"))

    @display(description="Posts", ordering="posts_total")
    def posts_count(self, obj: Tag) -> int:
        return obj.posts_total


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    """Admin for comments."""

    BODY_PREVIEW_LEN = 60

    list_display = ("post_title", "author_email", "short_body", "created_at")
    list_select_related = ("post", "author")
    list_filter = (
        ("post", AutocompleteSelectFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    )
    list_filter_submit = True
    search_fields = ("body", "author__email", "post__title")
    autocomplete_fields = ("post", "author")

    @display(description="Post", ordering="post__title")
    def post_title(self, obj: Comment) -> str:
        return obj.post.title

    @display(description="Author", ordering="author__email")
    def author_email(self, obj: Comment) -> str:
        return obj.author.email

    @display(description="Comment")
    def short_body(self, obj: Comment) -> str:
        return Truncator(obj.body).chars(self.BODY_PREVIEW_LEN)


class PostCommentsSection(TableSection):
    """Comments of the post, shown when the row is expanded."""

    verbose_name = "Comments"
    related_name = "comments"
    fields = ("author", "body", "created_at")


class CommentInline(TabularInline):
    """Comments of the post in their own tab, 10 per page."""

    model = Comment
    extra = 0
    tab = True
    per_page = 10
    fields = ("author", "body", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Comment]:
        return super().get_queryset(request).select_related("author")


@admin.register(Post)
class PostAdmin(ModelAdmin):
    """Admin for blog posts."""

    list_display = (
        "post_header",
        "status_label",
        "category",
        "tags_dropdown",
        "comments_count",
        "created_at",
    )
    list_select_related = ("author", "category")
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("tags", MultipleRelatedDropdownFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    )
    list_filter_submit = True
    list_sections = (PostCommentsSection,)
    search_fields = ("title", "body", "author__email")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category", "tags")
    readonly_fields = ("created_at", "updated_at")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }
    warn_unsaved_form = True
    inlines = (CommentInline,)
    fieldsets = (
        (
            "Content",
            {"classes": ["tab"], "fields": ("title", "slug", "body")},
        ),
        (
            "Classification",
            {"classes": ["tab"], "fields": ("category", "tags", "status")},
        ),
        (
            "Meta",
            {"classes": ["tab"], "fields": ("author", "created_at", "updated_at")},
        ),
    )
    actions = ("publish_selected", "move_to_drafts")
    actions_row = ("toggle_publish",)
    actions_list = ("publish_all_drafts",)
    actions_detail = ("open_comments",)
    actions_submit_line = ("save_and_publish",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        return (
            super()
            .get_queryset(request)
            .annotate(comments_total=Count("comments"))
            .prefetch_related(
                "tags",
                Prefetch("comments", queryset=Comment.objects.select_related("author")),
            )
        )

    @display(description="Post", header=True)
    def post_header(self, obj: Post) -> tuple[str, str]:
        return obj.title, obj.author.email

    @display(
        description="Status",
        ordering="status",
        label={
            Post.Status.PUBLISHED: "success",
            Post.Status.DRAFT: "warning",
        },
    )
    def status_label(self, obj: Post) -> tuple[str, str]:
        return obj.status, obj.get_status_display()

    @display(description="Tags", dropdown=True)
    def tags_dropdown(self, obj: Post) -> dict:
        tags: list[Tag] = list(obj.tags.all())
        return {
            "title": f"Tags: {len(tags)}",
            "items": [
                {
                    "title": tag.name,
                    "link": reverse("admin:blog_tag_change", args=(tag.pk,)),
                }
                for tag in tags
            ],
        }

    @display(description="Comments", ordering="comments_total")
    def comments_count(self, obj: Post) -> int:
        return obj.comments_total

    @action(description="Publish selected", icon="check_circle")
    def publish_selected(self, request: HttpRequest, queryset: QuerySet[Post]) -> None:
        updated: int = queryset.update(status=Post.Status.PUBLISHED)
        self.message_user(request, f"Published: {updated}")

    @action(description="Move to drafts", icon="edit_note")
    def move_to_drafts(self, request: HttpRequest, queryset: QuerySet[Post]) -> None:
        updated: int = queryset.update(status=Post.Status.DRAFT)
        self.message_user(request, f"Moved to drafts: {updated}")

    @action(description="Publish / unpublish", url_path="toggle-publish")
    def toggle_publish(self, request: HttpRequest, object_id: int) -> HttpResponseRedirect:
        post: Post = get_object_or_404(Post, pk=object_id)
        if post.status == Post.Status.PUBLISHED:
            post.status = Post.Status.DRAFT
        else:
            post.status = Post.Status.PUBLISHED
        post.save(update_fields=("status", "updated_at"))
        self.message_user(request, f"{post.title}: {post.get_status_display()}")
        return redirect(
            request.headers.get("referer") or reverse("admin:blog_post_changelist")
        )

    @action(
        description="Publish all drafts",
        icon="done_all",
        url_path="publish-all-drafts",
    )
    def publish_all_drafts(self, request: HttpRequest) -> HttpResponseRedirect:
        updated: int = Post.objects.filter(status=Post.Status.DRAFT).update(
            status=Post.Status.PUBLISHED
        )
        self.message_user(request, f"Published drafts: {updated}")
        return redirect(reverse("admin:blog_post_changelist"))

    @action(description="Open comments", icon="chat", url_path="open-comments")
    def open_comments(self, request: HttpRequest, object_id: int) -> HttpResponseRedirect:
        return redirect(
            f"{reverse('admin:blog_comment_changelist')}?post__id__exact={object_id}"
        )

    @action(description="Save & publish")
    def save_and_publish(self, request: HttpRequest, obj: Post) -> None:
        obj.status = Post.Status.PUBLISHED
        obj.save(update_fields=("status", "updated_at"))