"""Base settings shared by every environment."""

from pathlib import Path

from django.urls import reverse_lazy

from settings.conf import SECRET_KEY  # noqa: F401

# ---------- Paths ----------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
LOGS_DIR: Path = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ---------- Security ----------
DEBUG: bool = False
ALLOWED_HOSTS: list[str] = []

# ---------- Applications ----------
DJANGO_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS: list[str] = []

# Unfold must be loaded BEFORE django.contrib.admin
UNFOLD_APPS: list[str] = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
]

PROJECT_APPS: list[str] = [
    "apps.abstracts",
    "apps.auths",
    "apps.blog",
]

INSTALLED_APPS: list[str] = (
    UNFOLD_APPS + DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS
)

# ---------- Middleware ----------
MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------- URLs / WSGI / ASGI ----------
ROOT_URLCONF: str = "settings.urls"
WSGI_APPLICATION: str = "settings.wsgi.application"
ASGI_APPLICATION: str = "settings.asgi.application"

# ---------- Templates ----------
TEMPLATES: list[dict] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------- Auth ----------
AUTH_USER_MODEL: str = "auths.User"

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------- Internationalization ----------
LANGUAGE_CODE: str = "en-us"
TIME_ZONE: str = "UTC"
USE_I18N: bool = True
USE_TZ: bool = True

# ---------- Static files ----------
STATIC_URL: str = "static/"
STATIC_ROOT: Path = BASE_DIR / "static"

# ---------- Database defaults ----------
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# ---------- Logging ----------
LOGGING: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "app.log",
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}

# ---------- Unfold admin ----------
UNFOLD: dict = {
    "SITE_TITLE": "Blog API",
    "SITE_HEADER": "Blog API",
    "SITE_SUBHEADER": "Admin panel",
    "SITE_SYMBOL": "article",
    "ENVIRONMENT": "apps.blog.callbacks.environment_callback",
    "DASHBOARD_CALLBACK": "apps.blog.callbacks.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "oklch(96.2% 0.018 272.314)",
            "100": "oklch(93% 0.034 272.788)",
            "200": "oklch(87% 0.065 274.039)",
            "300": "oklch(78.5% 0.115 274.713)",
            "400": "oklch(67.3% 0.182 276.935)",
            "500": "oklch(58.5% 0.233 277.117)",
            "600": "oklch(51.1% 0.262 276.966)",
            "700": "oklch(45.7% 0.24 277.023)",
            "800": "oklch(39.8% 0.195 277.366)",
            "900": "oklch(35.9% 0.144 278.697)",
            "950": "oklch(25.7% 0.09 281.288)",
        },
    },
    "SITE_DROPDOWN": [
        {
            "icon": "code",
            "title": "GitHub repository",
            "link": "https://github.com/OpabekDastan/blog-api",
        },
        {
            "icon": "menu_book",
            "title": "Unfold docs",
            "link": "https://unfoldadmin.com/docs/",
        },
    ],
    "COMMAND": {
        "search_models": True,
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Overview",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Content",
                "separator": True,
                "items": [
                    {
                        "title": "Posts",
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_post_changelist"),
                        "badge": "apps.blog.callbacks.drafts_badge",
                    },
                    {
                        "title": "Comments",
                        "icon": "chat",
                        "link": reverse_lazy("admin:blog_comment_changelist"),
                    },
                    {
                        "title": "Categories",
                        "icon": "folder",
                        "link": reverse_lazy("admin:blog_category_changelist"),
                    },
                    {
                        "title": "Tags",
                        "icon": "sell",
                        "link": reverse_lazy("admin:blog_tag_changelist"),
                    },
                ],
            },
            {
                "title": "Users & Access",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:auths_user_changelist"),
                        "permission": "apps.blog.callbacks.is_superuser",
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": "apps.blog.callbacks.is_superuser",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": ["blog.post"],
            "items": [
                {
                    "title": "All",
                    "link": reverse_lazy("admin:blog_post_changelist"),
                    "active": "apps.blog.callbacks.all_posts_tab_active",
                },
                {
                    "title": "Published",
                    "link": lambda request: (
                        f"{reverse_lazy('admin:blog_post_changelist')}"
                        "?status__exact=published"
                    ),
                },
                {
                    "title": "Drafts",
                    "link": lambda request: (
                        f"{reverse_lazy('admin:blog_post_changelist')}"
                        "?status__exact=draft"
                    ),
                },
            ],
        },
    ],
}