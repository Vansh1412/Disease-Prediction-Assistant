from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageConfig:
    page_id: str
    label: str
    module: str
    function: str
    dev_only: bool = False


DASHBOARD    = "dashboard"
CONSULTATION = "consultation"
PREDICTION   = "prediction"
HISTORY      = "history"
COMPARISON   = "comparison"
REPORT       = "report"
ANALYTICS    = "analytics"
ABOUT        = "about"
DEVELOPER    = "developer"
ADMIN        = "admin"

DEFAULT_PAGE_ID = DASHBOARD

PAGES: tuple[PageConfig, ...] = (
    PageConfig(DASHBOARD,    "\U0001f3e0 Dashboard",         "app.pages.dashboard",    "render_dashboard"),
    PageConfig(CONSULTATION, "\U0001f4ac AI Consultation",    "app.pages.consultation",  "render_consultation"),
    PageConfig(PREDICTION,   "\U0001fa7a Disease Prediction", "app.pages.prediction",    "render_prediction"),
    PageConfig(HISTORY,      "\U0001f4dc Prediction History", "app.pages.history",       "render_history"),
    PageConfig(COMPARISON,   "\U0001f4ca Model Comparison",   "app.pages.comparison",    "render_comparison"),
    PageConfig(REPORT,       "\U0001f4c4 Medical Report",     "app.pages.report",        "render_report"),
    PageConfig(ANALYTICS,    "\U0001f4c8 Analytics",          "app.pages.analytics",     "render_analytics"),
    PageConfig(ABOUT,        "\u2139\ufe0f About",            "app.pages.about",         "render_about"),
    PageConfig(ADMIN,        "\U0001f512 Admin Portal",       "app.pages.admin",         "render_admin",        dev_only=True),
    PageConfig(
        DEVELOPER,
        "\U0001f468\u200d\U0001f4bb Developer Dashboard",
        "app.pages.developer",
        "render_developer",
        dev_only=True,
    ),
)

PAGE_BY_ID = {page.page_id: page for page in PAGES}
LEGACY_LABEL_TO_ID = {page.label: page.page_id for page in PAGES}


def get_page_options(dev_mode: bool = False) -> list[str]:
    return [page.page_id for page in PAGES if dev_mode or not page.dev_only]


def get_page_label(page_id: str) -> str:
    page = PAGE_BY_ID.get(page_id)
    return page.label if page else PAGE_BY_ID[DEFAULT_PAGE_ID].label


def normalize_page_id(value: object, dev_mode: bool = True) -> str:
    if not isinstance(value, str):
        return DEFAULT_PAGE_ID

    if value in PAGE_BY_ID:
        page = PAGE_BY_ID[value]
        return value if dev_mode or not page.dev_only else DEFAULT_PAGE_ID

    return LEGACY_LABEL_TO_ID.get(value, DEFAULT_PAGE_ID)
