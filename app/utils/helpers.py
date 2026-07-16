# pyrefly: ignore [missing-import]
from pathlib import Path

import streamlit as st


@st.cache_data(show_spinner=False)
def _read_css(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def load_css(file_path: str) -> None:
    """Load a CSS file and inject it globally into the Streamlit app.
    
    Uses st.markdown with unsafe_allow_html=True so styles apply to ALL
    Streamlit elements, not just the isolated st.html() iframe.
    """
    try:
        css = _read_css(file_path)
    except FileNotFoundError:
        st.warning(f"CSS file not found at {file_path}")
        return

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_glass_card(content_html: str) -> None:
    """Render trusted HTML content inside a glassmorphism card."""
    st.markdown(f'<div class="glass-card">{content_html}</div>', unsafe_allow_html=True)


import re as _re

def format_clinical_reasoning(raw_text: str) -> str:
    """
    Convert raw AI reasoning text into clean, professional HTML.

    Handles:
    - AI responses that contain raw HTML tags (strips them first)
    - **bold** → <strong>bold</strong>
    - Numbered lists: "1. **Term**: explanation"
    - Bullet lists:   "- **Term**: explanation" or "• item"
    - Plain paragraphs with justified text
    """
    if not raw_text:
        return '<span style="color:rgba(255,255,255,0.4);">No reasoning available.</span>'

    # ── Step 1: Strip any raw HTML the AI may have returned ──────────────
    # If the AI returned HTML markup, remove all tags so we work with plain text
    text = _re.sub(r'<[^>]+>', ' ', raw_text)
    # Collapse runs of whitespace created by tag removal
    text = _re.sub(r'[ \t]{2,}', ' ', text)
    text = _re.sub(r'\n{3,}', '\n\n', text).strip()

    if not text:
        return '<span style="color:rgba(255,255,255,0.4);">No reasoning available.</span>'

    def _md_inline(t: str) -> str:
        """Convert inline **bold** to <strong> within a text fragment."""
        t = _re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#E2E8F0;">\1</strong>', t)
        return t.strip()

    _icons = ["🔷", "🔶", "🔹", "🔸", "🔵", "🟠", "🟣"]

    # ── Step 2: Try numbered list pattern ─────────────────────────────────
    numbered_pattern = _re.compile(
        r'(\d+)\.\s+\*\*([^*]+)\*\*:?\s*(.*?)(?=\d+\.\s+\*\*|\Z)',
        _re.DOTALL
    )
    items = numbered_pattern.findall(text)

    if items:
        first_match = numbered_pattern.search(text)
        intro_raw = text[:first_match.start()].strip() if first_match else ""
        last_end = 0
        for m in numbered_pattern.finditer(text):
            last_end = m.end()
        outro_raw = text[last_end:].strip()

        intro_html = ""
        if intro_raw:
            intro_html = (
                f'<p style="font-family:Inter,sans-serif;font-size:0.88rem;'
                f'color:rgba(255,255,255,0.72);line-height:1.75;text-align:justify;'
                f'margin:0 0 1.1rem 0;font-weight:400;">{_md_inline(intro_raw)}</p>'
            )

        items_html = ""
        for idx, (_, term, body) in enumerate(items):
            icon = _icons[idx % len(_icons)]
            items_html += (
                f'<div style="display:flex;gap:0.9rem;align-items:flex-start;'
                f'background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);'
                f'border-radius:10px;padding:0.85rem 1rem;margin-bottom:0.65rem;">'
                f'<div style="font-size:1.1rem;line-height:1;margin-top:2px;flex-shrink:0;">{icon}</div>'
                f'<div>'
                f'<div style="font-family:Inter,sans-serif;font-size:0.82rem;font-weight:700;'
                f'color:#60BDFF;letter-spacing:0.01em;margin-bottom:0.3rem;">{_md_inline(term)}</div>'
                f'<div style="font-family:Inter,sans-serif;font-size:0.82rem;'
                f'color:rgba(255,255,255,0.65);line-height:1.7;text-align:justify;">'
                f'{_md_inline(body.strip())}</div>'
                f'</div></div>'
            )

        outro_html = ""
        if outro_raw:
            outro_html = (
                f'<p style="font-family:Inter,sans-serif;font-size:0.82rem;'
                f'color:rgba(255,255,255,0.5);line-height:1.7;text-align:justify;'
                f'margin:0.9rem 0 0 0;font-style:italic;'
                f'border-top:1px solid rgba(255,255,255,0.05);padding-top:0.85rem;">'
                f'{_md_inline(outro_raw)}</p>'
            )

        return intro_html + items_html + outro_html

    # ── Step 3: Try bullet list pattern (- item or • item) ────────────────
    bullet_pattern = _re.compile(r'^[-•*]\s+(.+)$', _re.MULTILINE)
    bullets = bullet_pattern.findall(text)

    if bullets:
        non_bullet = bullet_pattern.sub('', text).strip()
        intro_html = ""
        if non_bullet:
            intro_html = (
                f'<p style="font-family:Inter,sans-serif;font-size:0.88rem;'
                f'color:rgba(255,255,255,0.72);line-height:1.75;margin:0 0 1rem 0;">'
                f'{_md_inline(non_bullet)}</p>'
            )
        items_html = ""
        for idx, item in enumerate(bullets):
            icon = _icons[idx % len(_icons)]
            items_html += (
                f'<div style="display:flex;gap:0.75rem;align-items:flex-start;'
                f'padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                f'<span style="font-size:0.9rem;flex-shrink:0;">{icon}</span>'
                f'<span style="font-family:Inter,sans-serif;font-size:0.84rem;'
                f'color:rgba(255,255,255,0.7);line-height:1.65;">{_md_inline(item)}</span>'
                f'</div>'
            )
        return intro_html + items_html

    # ── Step 4: Plain text — split on paragraph breaks ────────────────────
    paragraphs = [p.strip() for p in _re.split(r'\n\n+', text) if p.strip()]
    para_html = ""
    for para in paragraphs:
        para_html += (
            f'<p style="font-family:Inter,sans-serif;font-size:0.85rem;'
            f'color:rgba(255,255,255,0.68);line-height:1.8;text-align:justify;'
            f'margin:0 0 0.85rem 0;font-weight:400;">{_md_inline(para)}</p>'
        )
    return para_html


