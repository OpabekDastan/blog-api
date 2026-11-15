from datetime import date, timedelta
from django.utils import timezone
from typing import Any, Callable
from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.db import connection
from django.db.models import Count, Model, QuerySet
from django.test.utils import CaptureQueriesContext
from apps.auths.models import User
from apps.blog.models import Post
from apps.blog.queries import QUERIES






class Command(BaseCommand):
    """Run the ORM queries from apps/blog/queries.py"""

    help = "Run the ORM queries and show the result and the number of SQL queries."

    FIRST_CHANGING_QUERY = 40
    LAST_CHANGING_QUERY = 44
    PREVIEW_ROWS = 5
    SAMPLE_PAGE = 2 
    SAMPLE_DAYS = 30 
    SAMPLE_TAGS_COUNT = 2
    SAMPLE_MIN_POSTS = 10
    LAST_NAME_LETTERS = 3

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--number", 
            type = int,
            help = "Run only the query with this num",
        )
        parser.add_argument(
            "--sql",
            action="store_true",
            help="Also print the SQL that Django request to the DB"

        )
    def handle(self, *args: Any, **options:Any) -> None:
        """Command entry point."""
        number: int | None = options["number"]
        show_sql: bool = options["sql"]

        if number is not None and number not in QUERIES:
            raise CommandError(
                f"Query #{number} does not exist. "
                f"Use a number from {min(QUERIES)} to {max(QUERIES)}." 
            ) 

        arguments: dict[int, dict[str, Any]] = self._get_arguments()
        
        if number is not None:
            self._run_query(number, arguments.get(number, {}), show_sql)
            return
        for query_number in QUERIES:
            if self.FIRST_CHANGING_QUERY <= query_number <= self.LAST_CHANGING_QUERY: 
                continue
            self._run_query(query_number, arguments.get(query_number, {}), show_sql)

    def _get_arguments(self) -> dict [int, dict[str, Any]]:
        """Sample arguments for the queries"""
        today: date = timezone.localdate()
        month_ago: date = today - timedelta(days=self.SAMPLE_DAYS)
        post_slug: str = ""
        title_word: str = ""
        post: Post | None = Post.objects.first()
        if post: 
            post_slug = post_slug
            title_word = post.title.split()[0]
        author_email: str = ""
        full_name: str = ""
        author: User | None = User.objects.filter(
            posts__status = Post.Status.PUBLISHED
        ).first()
        if author:
            author_email = author_email
            last_name_start: str = author.last_name[: self.LAST_NAME_LETTERS]
            full_name_part = f"{author.first_name} {last_name_start}".lower()
        first_tag: str = ""
        second_tag: str = ""
        post_with_tags: Post | None = (
            Post.objects.annotate(tag_count = Count("tags"))
            .filter(tag_count__gte = self.SAMPLE_TAGS_COUNT)
            .first()

        )
        if post_with_tags: 
            tag_slugs: list[str] = list(post_with_tags.tags.values_list("slug", flat=True))
            first_tag = tag_slugs[0]
            second_tag = tag_slugs[1]
        return {
            4: {"slug": post_slug},
            7: {"page": self.SAMPLE_PAGE},
            8: {"word": title_word},
            9: {"domain": "example.com"},
            11: {"slugs": ["python", "django", "devops"]},
            12: {"year": month_ago.year, "month": month_ago.month},
            13: {"days": self.SAMPLE_DAYS},
            14: {"start": month_ago, "end": today},
            15: {"email": author_email.upper()},
            16: {"tag_slug": "orm"},
            17: {"category_slug": "django"},
            21: {"first_slug": first_tag, "second_slug": second_tag},
            22: {"text": title_word},
            34: {"min_posts": self.SAMPLE_MIN_POSTS},

        }
        
    def _run_query(self, number: int, arguments: dict[str,Any], show_sql: bool) -> None:
        """Run one query. Show the num of SQL qs and the result"""

        function: Callable[...,Any] = QUERIES[number]
        with CaptureQueriesContext(connection) as context:
            result: Any = function(**arguments)
            if isinstance(result, QuerySet): 
                list(result)

        sql_count: int = len(context.captured_queries)
        word: str = "query" if sql_count == 1 else "queries"
        self.stdout.write(
            self.style.SUCCESS(f"#{number} {function.__name__} — {sql_count} SQL {word}")
        )
        if show_sql: 
            for query in context.captured_queries:
                self.stdout.write(query["sql"])
        self._print_result(result)

    def _print_result(self, result: Any)->None:
        """Print the one value or the first rows of a list or a QSet"""

        if isinstance(result, dict):
            for key, value in result.items():
                self.stdout.write(f"{key}: {value}")
            return 
        if not isinstance(result, (list, QuerySet)):
            self.stdout.write(f"{result}")
            return

        annotations: list[str] = [] 
        if isinstance(result, QuerySet):
            annotations = list(result.query.annotations)

        rows: list[Any] = list(result)
        for row in rows[:self.PREVIEW_ROWS]:
            line: str = str(row)
            if annotations and isinstance(row, Model):
                values: dict[str,Any] = {}
                for name in annotations:
                    values[name] = getattr(row, name)
                line = f"{line} {values}"
            self.stdout.write(f"{line}")
        self.stdout.write(f"({len(rows)} rows)")
                