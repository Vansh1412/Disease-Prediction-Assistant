"""
app/components/logs_modal.py
Enterprise-grade System Activity Log modal for MediSense AI.
Renders as a full-page overlay with glassmorphic design.
"""
from __future__ import annotations

# pyrefly: ignore [missing-import]
import streamlit as st
from app.utils.logs import (
    build_activity_log, logs_to_json, logs_to_csv, log_stats,
    level_color, LogEntry,
)

_CATEGORIES = {
    "all":          "All",
    "prediction":   "Predictions",
    "consultation": "Consultations",
    "system":       "System",
    "model":        "Model",
    "auth":         "Auth",
}

_MODAL_CSS = """
<style>
/* ── Logs Modal Overlay ───────────────────────────────────────── */
.ms-logs-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.72);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    z-index: 99998;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.2s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp {
    from { opacity: 0; transform: translateY(28px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0)   scale(1);    }
}
.ms-logs-modal {
    background: rgba(11, 18, 32, 0.95);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px;
    backdrop-filter: blur(30px);
    -webkit-backdrop-filter: blur(30px);
    box-shadow: 0 30px 80px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.04) inset;
    width: min(900px, 94vw);
    max-height: 86vh;
    display: flex;
    flex-direction: column;
    animation: slideUp 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    overflow: hidden;
}
/* Header */
.ms-modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.5rem 0.9rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    flex-shrink: 0;
}
.ms-modal-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.ms-modal-title-icon {
    width: 28px; height: 28px;
    background: rgba(37,99,235,0.18);
    border: 1px solid rgba(37,99,235,0.3);
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.88rem;
}
.ms-modal-live {
    display: flex; align-items: center; gap: 5px;
    font-size: 0.65rem; color: #22C55E; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em;
}
.ms-live-dot {
    width: 6px; height: 6px; background: #22C55E; border-radius: 50%;
    animation: livePulse 1.8s ease-in-out infinite;
}
@keyframes livePulse {
    0%,100% { opacity: 1; box-shadow: 0 0 4px #22C55E; }
    50%      { opacity: 0.45; box-shadow: none; }
}
/* Stats row */
.ms-log-stats {
    display: flex;
    gap: 0.75rem;
    padding: 0.85rem 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    flex-shrink: 0;
    flex-wrap: wrap;
}
.ms-stat-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 0.35rem 0.75rem;
    display: flex; flex-direction: column;
    align-items: center;
    min-width: 68px;
}
.ms-stat-num {
    font-size: 1.1rem; font-weight: 800; color: #F8FAFC; line-height: 1;
}
.ms-stat-lbl {
    font-size: 0.58rem; color: rgba(255,255,255,0.35);
    text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px;
}
/* Search bar */
.ms-log-search-wrap {
    padding: 0.65rem 1.5rem 0;
    flex-shrink: 0;
}
.ms-log-search {
    width: 100%;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 0.45rem 0.85rem;
    color: #F8FAFC;
    font-size: 0.78rem;
    font-family: 'Inter', sans-serif;
    outline: none;
    box-sizing: border-box;
    transition: border-color 0.15s;
}
.ms-log-search:focus { border-color: rgba(37,99,235,0.5); }
.ms-log-search::placeholder { color: rgba(255,255,255,0.25); }
/* Filter chips */
.ms-filter-row {
    display: flex; gap: 0.4rem; flex-wrap: wrap;
    padding: 0.55rem 1.5rem;
    flex-shrink: 0;
}
.ms-filter-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 0.18rem 0.7rem;
    font-size: 0.68rem; font-weight: 500;
    color: rgba(255,255,255,0.5);
    cursor: pointer;
    transition: all 0.15s;
    font-family: 'Inter', sans-serif;
}
.ms-filter-chip:hover { color: #fff; background: rgba(255,255,255,0.09); }
.ms-filter-chip.active {
    background: rgba(37,99,235,0.18);
    border-color: rgba(37,99,235,0.4);
    color: #60BDFF; font-weight: 600;
}
/* Log list */
.ms-log-list {
    overflow-y: auto;
    flex: 1;
    padding: 0.5rem 1.5rem 0.75rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(255,255,255,0.1) transparent;
}
.ms-log-list::-webkit-scrollbar { width: 4px; }
.ms-log-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 4px; }
/* Log entry */
.ms-log-entry {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    transition: background 0.12s;
}
.ms-log-entry:last-child { border-bottom: none; }
.ms-log-entry:hover { background: rgba(255,255,255,0.025); border-radius: 8px; padding-left: 6px; padding-right: 6px; margin: 0 -6px; }
.ms-log-dot {
    width: 8px; height: 8px; border-radius: 50%;
    margin-top: 5px; flex-shrink: 0;
}
.ms-log-time {
    font-size: 0.65rem; color: rgba(255,255,255,0.3);
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    min-width: 60px; margin-top: 2px; flex-shrink: 0;
}
.ms-log-body { flex: 1; }
.ms-log-title {
    font-size: 0.78rem; font-weight: 600; color: #E2E8F0;
    margin-bottom: 2px;
}
.ms-log-detail {
    font-size: 0.68rem; color: rgba(255,255,255,0.35);
    line-height: 1.4;
}
.ms-log-cat {
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em;
    padding: 1px 6px; border-radius: 4px;
    background: rgba(255,255,255,0.06);
    color: rgba(255,255,255,0.4);
    margin-top: 2px; display: inline-block;
    flex-shrink: 0;
}
.ms-log-entry.hidden { display: none; }
/* Empty state */
.ms-log-empty {
    text-align: center; padding: 3rem 1rem;
    color: rgba(255,255,255,0.25); font-size: 0.85rem;
}
</style>
"""

_MODAL_JS = """
<script>
(function() {
    var searchInput = document.getElementById('ms-log-search');
    var filterBtns  = document.querySelectorAll('.ms-filter-chip');
    var currentCat  = 'all';

    function applyFilters() {
        var q = searchInput ? searchInput.value.toLowerCase() : '';
        document.querySelectorAll('.ms-log-entry').forEach(function(el) {
            var cat   = el.getAttribute('data-cat') || '';
            var text  = el.textContent.toLowerCase();
            var catOk = currentCat === 'all' || cat === currentCat;
            var txtOk = !q || text.includes(q);
            el.classList.toggle('hidden', !(catOk && txtOk));
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }

    filterBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            currentCat = this.getAttribute('data-cat');
            filterBtns.forEach(function(b) { b.classList.remove('active'); });
            this.classList.add('active');
            applyFilters();
        });
    });

    // ESC to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var url = new URL(window.parent.location.href);
            url.searchParams.set('__nav', '__close_logs');
            window.parent.history.replaceState(null, '', url.toString());
            window.parent.location.reload();
        }
    });
})();
</script>
"""


def _render_entry_html(entry: LogEntry) -> str:
    color = level_color(entry.level)
    cat_label = _CATEGORIES.get(entry.category, entry.category.title())
    return f"""
<div class="ms-log-entry" data-cat="{entry.category}">
  <div class="ms-log-dot" style="background:{color};box-shadow:0 0 6px {color}55;"></div>
  <span class="ms-log-time">{entry.timestamp}</span>
  <div class="ms-log-body">
    <div class="ms-log-title">{entry.title}</div>
    <div class="ms-log-detail">{entry.detail}</div>
  </div>
  <span class="ms-log-cat">{cat_label}</span>
</div>
"""


def render_logs_modal() -> None:
    """
    Call this at the top of any page that needs the logs modal.
    Checks st.session_state.show_logs and renders accordingly.
    """
    # Handle close via query param
    close_target = st.query_params.get("__nav", "")
    if close_target == "__close_logs":
        try:
            del st.query_params["__nav"]
        except Exception:
            pass
        st.session_state.show_logs = False
        st.rerun()

    if not st.session_state.get("show_logs", False):
        return

    # Build log data
    predictions = st.session_state.get("prediction_history", [])
    entries = build_activity_log(predictions)
    stats   = log_stats(entries)

    # ── Export buttons (rendered above the modal HTML overlay) ──────
    col_json, col_csv, col_close = st.columns([1, 1, 4])
    with col_json:
        st.download_button(
            "⬇ JSON",
            data=logs_to_json(entries),
            file_name="medisense_logs.json",
            mime="application/json",
            key="logs_dl_json",
            use_container_width=True,
        )
    with col_csv:
        st.download_button(
            "⬇ CSV",
            data=logs_to_csv(entries),
            file_name="medisense_logs.csv",
            mime="text/csv",
            key="logs_dl_csv",
            use_container_width=True,
        )
    with col_close:
        if st.button("✕  Close Logs", key="logs_close_btn", type="secondary"):
            st.session_state.show_logs = False
            st.rerun()

    # ── Build entries HTML ───────────────────────────────────────────
    entries_html = "".join(_render_entry_html(e) for e in entries)
    if not entries_html:
        entries_html = '<div class="ms-log-empty">No log entries found.</div>'

    # ── Filter chips ─────────────────────────────────────────────────
    chips_html = ""
    for key, label in _CATEGORIES.items():
        active = " active" if key == "all" else ""
        chips_html += f'<button class="ms-filter-chip{active}" data-cat="{key}">{label}</button>'

    # ── Stats chips ──────────────────────────────────────────────────
    stats_html = f"""
<div class="ms-stat-chip"><div class="ms-stat-num">{stats["total"]}</div><div class="ms-stat-lbl">Total</div></div>
<div class="ms-stat-chip"><div class="ms-stat-num">{stats["today"]}</div><div class="ms-stat-lbl">Today</div></div>
<div class="ms-stat-chip"><div class="ms-stat-num">{stats["predictions"]}</div><div class="ms-stat-lbl">Predictions</div></div>
<div class="ms-stat-chip" style="border-color:rgba(239,68,68,0.25)">
  <div class="ms-stat-num" style="color:#EF4444">{stats["errors"]}</div><div class="ms-stat-lbl">Errors</div>
</div>
<div class="ms-stat-chip" style="border-color:rgba(245,158,11,0.25)">
  <div class="ms-stat-num" style="color:#F59E0B">{stats["warnings"]}</div><div class="ms-stat-lbl">Warnings</div>
</div>
"""

    modal_html = f"""
{_MODAL_CSS}
<div class="ms-logs-modal">
  <div class="ms-modal-header">
    <div class="ms-modal-title">
      <div class="ms-modal-title-icon">📋</div>
      System Activity Log
    </div>
    <div class="ms-modal-live">
      <div class="ms-live-dot"></div> Live
    </div>
  </div>

  <div class="ms-log-stats">{stats_html}</div>

  <div class="ms-log-search-wrap">
    <input id="ms-log-search" class="ms-log-search"
           type="text" placeholder="🔍  Search logs by title, detail, or category…" />
  </div>

  <div class="ms-filter-row">{chips_html}</div>

  <div class="ms-log-list">
    {entries_html}
  </div>
</div>
{_MODAL_JS}
"""
    st.markdown(modal_html, unsafe_allow_html=True)
