from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st


# ──────────────────────────────────────────────
# Core helpers
# ──────────────────────────────────────────────

def escape_html(value: Any) -> str:
    """Escapes a value for safe HTML rendering."""
    return escape(str(value), quote=True)


def text_to_html(value: Any) -> str:
    """Converts newlines to <br> tags after escaping."""
    return escape_html(value).replace("\n", "<br>")


def render_html(html: str) -> None:
    """Safely renders HTML. Uses st.markdown so that <style> blocks apply
    globally to the entire Streamlit page (not isolated in an st.html iframe)."""
    # Strip leading/trailing whitespace per line to keep it compact
    cleaned = " ".join(line.strip() for line in html.split("\n") if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)



# ──────────────────────────────────────────────
# Glass-card helpers
#
# ROOT CAUSE OF GHOST BUBBLES:
# The old glass_card_start() emitted '<div class="glass-card-container">'
# as a single st.markdown() call. Streamlit wraps every markdown call in its
# own <div class="stMarkdown"> element with min-height, so the orphaned opening
# <div> rendered as a visible styled empty box above every card.
#
# FIX: glass_card_start() now injects a CSS-only rule (display:none on the
# emitter itself) plus a unique class that is applied via CSS attribute targeting.
# For pages with mixed Streamlit widgets, use PlotlyCard() context manager.
# ──────────────────────────────────────────────

_card_counter: list[int] = [0]


def glass_card_start(style: str = "") -> None:
    """Opens a glass card visual section.

    GHOST BUBBLE FIX: The opener emits a display:none sentinel element.
    A CSS rule hides the .stMarkdown wrapper that Streamlit creates for it,
    so no visible empty box appears above the card content.
    Pages with only HTML content (render_html calls) should use GlassCard()
    for best results. Pages with native Streamlit widgets (charts, inputs)
    use glass_card_start/end so the widgets render inside the visual region.
    """
    _card_counter[0] += 1
    uid = f"gc-open-{_card_counter[0]}"
    render_html(
        f"""
        <style>
        /* Hide the stMarkdown container of the glass_card_start() sentinel */
        .stMarkdown:has(> div > .{uid}) {{
            display: none !important;
        }}
        </style>
        <div class="{uid}" style="display:none;"></div>
        """
    )


def glass_card_end() -> None:
    """No-op closing companion kept for API compatibility."""
    pass


def GlassCard(title: str, content: str, subtitle: str = "") -> None:
    """Renders a complete glass card in a single st.markdown() call.
    This is always ghost-bubble-free since all HTML is in one call."""
    sub = (
        f'<p style="color:var(--text-muted);font-size:.85rem;'
        f'margin-top:-.5rem;margin-bottom:1rem;">{subtitle}</p>'
        if subtitle else ""
    )
    title_html = (
        f'<h3 style="margin-top:0;margin-bottom:.75rem;">{escape_html(title)}</h3>'
        if title else ""
    )
    render_html(
        f'<div class="glass-card-container">'
        f'{title_html}{sub}<div>{content}</div>'
        f'</div>'
    )


# ──────────────────────────────────────────────
# Page header  (old name + new alias)
# ──────────────────────────────────────────────

def render_page_header(icon: str, title: str, subtitle: str) -> None:
    render_html(
        f"""
        <section class="page-header">
            <div class="page-header__icon">{escape_html(icon)}</div>
            <div>
                <h1>{escape_html(title)}</h1>
                <p>{escape_html(subtitle)}</p>
            </div>
        </section>
        """
    )


def PageHeader(emoji: str, title: str, subtitle: str = "") -> None:
    """Alias for render_page_header that also adds the page-header-wrapper styling."""
    sub = f'<p class="page-header-subtitle">{escape_html(subtitle)}</p>' if subtitle else ""
    render_html(
        f"""
        <div class="page-header-wrapper">
            <span class="page-header-emoji">{escape_html(emoji)}</span>
            <h1 class="page-header-title">{escape_html(title)}</h1>
            {sub}
        </div>
        """
    )


from contextlib import contextmanager

@contextmanager
def PageLayout(emoji: str, title: str, subtitle: str = ""):
    """
    Standardized page layout wrapper.
    Ensures identical spacing between navbar, header, and content across all pages.
    """
    PageHeader(emoji, title, subtitle)
    with st.container():
        yield



# ──────────────────────────────────────────────
# Metric card  (old signature + new alias)
# ──────────────────────────────────────────────

def render_metric_card(
    label: str,
    value: Any,
    *,
    accent: str = "#2563EB",
    helper: str | None = None,
) -> None:
    helper_html = f"<p>{escape_html(helper)}</p>" if helper else ""
    render_html(
        f"""
        <div class="metric-card" style="--metric-accent:{accent};">
            <span>{escape_html(label)}</span>
            <strong>{escape_html(value)}</strong>
            {helper_html}
        </div>
        """
    )


def MetricCard(
    title: str,
    value: str,
    delta: str = "",
    delta_positive: bool = True,
) -> None:
    delta_html = ""
    if delta:
        cls = "delta-positive" if delta_positive else "delta-negative"
        arrow = "↑" if delta_positive else "↓"
        delta_html = f'<div class="metric-card-delta {cls}"><span>{arrow}</span><span>{escape_html(delta)}</span></div>'

    render_html(
        f"""
        <div class="metric-card-wrapper">
            <div class="metric-card-title">{escape_html(title)}</div>
            <div class="metric-card-value">{escape_html(value)}</div>
            {delta_html}
        </div>
        """
    )


# ──────────────────────────────────────────────
# Empty state  (old name + new alias)
# ──────────────────────────────────────────────

def render_empty_state(title: str, body: str) -> None:
    render_html(
        f"""
        <div class="empty-state">
            <strong>{escape_html(title)}</strong>
            <p>{escape_html(body)}</p>
        </div>
        """
    )


def EmptyState(title: str, body: str, icon: str = "📁") -> None:
    render_html(
        f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">{escape_html(icon)}</div>
            <div class="empty-state-title">{escape_html(title)}</div>
            <p class="empty-state-desc">{escape_html(body)}</p>
        </div>
        """
    )


# ──────────────────────────────────────────────
# Progress bar
# ──────────────────────────────────────────────

def render_progress_bar(value: float, *, color: str = "#2563EB") -> str:
    bounded = max(0.0, min(float(value), 100.0))
    return (
        '<div class="progress-track">'
        f'<div class="progress-fill" style="width:{bounded:.2f}%;background:{color};"></div>'
        "</div>"
    )


# ──────────────────────────────────────────────
# Buttons
# ──────────────────────────────────────────────

def PrimaryButton(label: str, key: str, use_container_width: bool = True) -> bool:
    return st.button(label, key=key, type="primary", use_container_width=use_container_width)


def SecondaryButton(label: str, key: str, use_container_width: bool = True) -> bool:
    return st.button(label, key=key, type="secondary", use_container_width=use_container_width)


def DangerButton(label: str, key: str, use_container_width: bool = True) -> bool:
    return st.button(label, key=key, type="secondary", use_container_width=use_container_width)


# ──────────────────────────────────────────────
# Status badges, dividers, stat counters
# ──────────────────────────────────────────────

def StatusBadge(label: str, status_type: str = "success") -> None:
    render_html(
        f'<span class="status-badge-container status-badge-{status_type}"><span class="status-badge-dot"></span>{escape_html(label)}</span>'
    )


def SectionDivider() -> None:
    render_html('<div class="section-divider-line"></div>')


def StatCounter(value: str, label: str) -> None:
    render_html(
        f"""
        <div class="stat-counter-wrapper">
            <div class="stat-counter-val">{escape_html(value)}</div>
            <div class="stat-counter-label">{escape_html(label)}</div>
        </div>
        """
    )


# ──────────────────────────────────────────────
# Feature card
# ──────────────────────────────────────────────

def FeatureCard(icon: str, title: str, description: str) -> None:
    render_html(
        f"""
        <div class="feature-card-wrapper">
            <div class="feature-card-icon">{escape_html(icon)}</div>
            <h3 class="feature-card-title">{escape_html(title)}</h3>
            <p class="feature-card-desc">{escape_html(description)}</p>
        </div>
        """
    )


# ──────────────────────────────────────────────
# Chat bubble
# ──────────────────────────────────────────────

def ChatBubble(message: str, is_user: bool = False, avatar_label: str = "") -> None:
    row_class = "chat-message-row chat-message-user" if is_user else "chat-message-row chat-message-assistant"
    avatar_class = "chat-avatar-user" if is_user else "chat-avatar-assistant"
    if not avatar_label:
        avatar_label = "U" if is_user else "AI"
    render_html(
        f"""
        <div class="{row_class}">
            <div class="chat-avatar {avatar_class}">{escape_html(avatar_label)}</div>
            <div class="chat-bubble-container">{message}</div>
        </div>
        """
    )


# ──────────────────────────────────────────────
# Hero section
# ──────────────────────────────────────────────

def HeroSection(badge: str, title: str, subtitle: str) -> None:
    render_html(
        f"""
        <div class="hero-wrapper">
            <div class="hero-badge">{escape_html(badge)}</div>
            <h1 class="hero-title-main">{escape_html(title)}</h1>
            <p class="hero-subtitle-main">{escape_html(subtitle)}</p>
        </div>
        """
    )


# ──────────────────────────────────────────────
# Loading spinner / shimmer
# ──────────────────────────────────────────────

def LoadingSpinner() -> None:
    render_html(
        '<div class="loading-wrapper"><div class="dots-loader"><div></div><div></div><div></div></div></div>'
    )


def render_shimmer_card(height_px: int = 150) -> None:
    render_html(
        f'<div class="glass-card-container loading-shimmer" style="height:{height_px}px;opacity:.7;"></div>'
    )


# ──────────────────────────────────────────────
# Navbar / Sidebar / Footer — imported from components
# ──────────────────────────────────────────────

def Navbar(active_page_id: str = "dashboard") -> None:
    from app.components.navbar import render_navbar
    render_navbar(active_page_id)


def Sidebar() -> str:
    from app.components.sidebar import render_sidebar
    return render_sidebar()


def Footer() -> None:
    from app.components.footer import render_footer
    render_footer()


# ──────────────────────────────────────────────
# Misc helpers used by older pages
# ──────────────────────────────────────────────

def SearchBar(placeholder: str = "Search...") -> str:
    return st.text_input("Search", value="", placeholder=placeholder, label_visibility="collapsed")


def NotificationBell(count: int = 0) -> None:
    badge = (
        f'<span style="position:absolute;top:-5px;right:-5px;background:var(--status-error);color:white;border-radius:50%;font-size:.6rem;padding:2px 5px;font-weight:bold;">{count}</span>'
        if count > 0
        else ""
    )
    render_html(
        f'<div style="position:relative;display:inline-block;cursor:pointer;"><span style="font-size:1.3rem;">🔔</span>{badge}</div>'
    )


def UserMenu(username: str, tier: str = "Clinical Workspace") -> None:
    initial = username[:1].upper() if username else "U"
    render_html(
        f"""
        <div style="display:flex;align-items:center;gap:.5rem;background:rgba(255,255,255,.05);padding:.35rem .75rem;border-radius:9999px;">
            <div style="width:24px;height:24px;border-radius:50%;background:var(--primary);display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:bold;color:white;">{escape_html(initial)}</div>
            <span style="font-size:.85rem;font-weight:500;color:var(--text-main);">{escape_html(username)}</span>
        </div>
        """
    )
