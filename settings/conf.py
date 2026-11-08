"""Reads environment variables from settings/.env via python-decouple."""

from pathlib import Path

from decouple import Config, Csv, RepositoryEnv

ENV_FILE_PATH: Path = Path(__file__).resolve().parent / ".env"

config: Config = Config(RepositoryEnv(str(ENV_FILE_PATH)))

# ---------- Core ----------
ENV_ID: str = config("BLOG_ENV_ID", cast=str)
SECRET_KEY: str = config("BLOG_SECRET_KEY", cast=str)

# ---------- Production only ----------
ALLOWED_HOSTS: list[str] = config("BLOG_ALLOWED_HOSTS", default="", cast=Csv())
DB_NAME: str = config("BLOG_DB_NAME", default="blog", cast=str)
DB_USER: str = config("BLOG_DB_USER", default="postgres", cast=str)
DB_PASSWORD: str = config("BLOG_DB_PASSWORD", default="", cast=str)
DB_HOST: str = config("BLOG_DB_HOST", default="localhost", cast=str)
DB_PORT: int = config("BLOG_DB_PORT", default=5432, cast=int)
