from typing import Any, Callable
from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.db import connection
from django.db.models import Model, QuerySet
from django.test.utils import CaptureQueriesContext
from apps.blog.queries import QUERIES
class Command(BaseCommand):
    """Run the ORM queries from apps/blog/queries.py"""

    help = "Run the ORM queries and show the result and the number of SQL queries."

    FIRST_CHANGING_QUERY = 40
    LAST_CHANGING_QUERY = 44
    PREVIEW_ROWS = 5

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
        if number is not None:
            self._run_query(number, show_sql)
            return
        for query_number in QUERIES:
            if self.FIRST_CHANGING_QUERY <= query_number <= self.LAST_CHANGING_QUERY: 
                continue
            self._run_query(query_number, show_sql)


    def _run_query(self, number: int, show_sql: bool) -> None:
        """Run one query. Show the num of SQL qs and the result"""

        function: Callable[...,Any] = QUERIES[number]
        with CaptureQueriesContext(connection) as context:
            result: Any = function()
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
                