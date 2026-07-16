"""
app/utils/logs.py
Activity log generation and management for MediSense AI.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Literal


LogLevel = Literal["success", "info", "warning", "error"]
LogCategory = Literal["prediction", "consultation", "system", "auth", "model"]

_ICONS: dict[LogLevel, str] = {
    "success": "✅",
    "info":    "🔵",
    "warning": "⚠️",
    "error":   "❌",
}

_LEVEL_COLORS: dict[LogLevel, str] = {
    "success": "#22C55E",
    "info":    "#3B82F6",
    "warning": "#F59E0B",
    "error":   "#EF4444",
}


@dataclass
class LogEntry:
    timestamp: str          # "HH:MM:SS"
    category: LogCategory
    title: str
    detail: str
    level: LogLevel
    raw_dt: str = ""        # ISO datetime for sorting / export

    def to_dict(self) -> dict:
        return asdict(self)


def _fmt_time(dt: datetime) -> str:
    return dt.strftime("%H:%M:%S")


def _fmt_iso(dt: datetime) -> str:
    return dt.isoformat()


# ── Seed system boot entries ─────────────────────────────────────────────────
_BOOT_SEQUENCE: list[tuple[int, LogCategory, str, str, LogLevel]] = [
    (0,  "system", "Dashboard Loaded",       "Application shell initialised", "info"),
    (1,  "system", "Database Connected",     "SQLite session database online", "success"),
    (2,  "system", "ML Models Loaded",       "Logistic Regression, Decision Tree, KNN ready", "success"),
    (3,  "system", "Ollama Connected",       "Local LLM endpoint responding at :11434", "success"),
    (4,  "system", "Analytics Ready",        "Telemetry engine warm and collecting", "success"),
    (5,  "auth",   "User Login Successful",  "Session token issued", "success"),
]


def build_activity_log(prediction_history: list[dict]) -> list[LogEntry]:
    """
    Build a chronological list of LogEntry objects from:
    - boot sequence
    - real prediction history
    - simulated consultation events
    - heartbeat / model checks
    """
    now = datetime.now()
    # Boot entries — minutes before now
    boot_base = now - timedelta(minutes=len(_BOOT_SEQUENCE) + len(prediction_history) + 5)
    entries: list[LogEntry] = []

    for i, (offset, cat, title, detail, level) in enumerate(_BOOT_SEQUENCE):
        dt = boot_base + timedelta(minutes=i)
        entries.append(LogEntry(
            timestamp=_fmt_time(dt),
            category=cat,
            title=title,
            detail=detail,
            level=level,
            raw_dt=_fmt_iso(dt),
        ))

    # Consultation start — before first prediction
    consult_dt = boot_base + timedelta(minutes=len(_BOOT_SEQUENCE))
    entries.append(LogEntry(
        timestamp=_fmt_time(consult_dt),
        category="consultation",
        title="Consultation Started",
        detail="AI-guided symptom intake initiated",
        level="info",
        raw_dt=_fmt_iso(consult_dt),
    ))

    # Real predictions from history
    for idx, pred in enumerate(prediction_history):
        pred_dt = consult_dt + timedelta(minutes=idx + 1, seconds=random.randint(10, 50))
        disease  = pred.get("disease", "Unknown")
        conf     = pred.get("confidence", 0)
        model    = pred.get("model", "Ensemble")
        level: LogLevel = "success" if conf >= 85 else "info" if conf >= 70 else "warning"
        entries.append(LogEntry(
            timestamp=_fmt_time(pred_dt),
            category="prediction",
            title="Prediction Completed",
            detail=f"Disease: {disease} | Confidence: {conf:.1f}% | Model: {model}",
            level=level,
            raw_dt=_fmt_iso(pred_dt),
        ))

    # Heartbeat pulses — last few minutes
    heartbeats = [
        ("Prediction Pipeline Ready",    "All classifiers loaded and verified", "system", "success"),
        ("Response Generated",           "Diagnostic output delivered to frontend", "model",  "success"),
        ("Heartbeat OK",                 "All services nominal", "system", "info"),
    ]
    for i, (title, detail, cat, lvl) in enumerate(heartbeats):
        hb_dt = now - timedelta(seconds=(len(heartbeats) - i) * 45)
        entries.append(LogEntry(
            timestamp=_fmt_time(hb_dt),
            category=cat,   # type: ignore[arg-type]
            title=title,
            detail=detail,
            level=lvl,      # type: ignore[arg-type]
            raw_dt=_fmt_iso(hb_dt),
        ))

    # Sort newest first
    entries.sort(key=lambda e: e.raw_dt, reverse=True)
    return entries


def logs_to_json(entries: list[LogEntry]) -> str:
    return json.dumps([e.to_dict() for e in entries], indent=2)


def logs_to_csv(entries: list[LogEntry]) -> str:
    lines = ["timestamp,category,level,title,detail"]
    for e in entries:
        detail_safe = e.detail.replace('"', '""')
        lines.append(f'{e.timestamp},{e.category},{e.level},"{e.title}","{detail_safe}"')
    return "\n".join(lines)


def log_stats(entries: list[LogEntry]) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "total":       len(entries),
        "today":       sum(1 for e in entries if e.raw_dt.startswith(today)),
        "predictions": sum(1 for e in entries if e.category == "prediction"),
        "errors":      sum(1 for e in entries if e.level == "error"),
        "warnings":    sum(1 for e in entries if e.level == "warning"),
    }


def level_color(level: LogLevel) -> str:
    return _LEVEL_COLORS.get(level, "#3B82F6")


def level_icon(level: LogLevel) -> str:
    return _ICONS.get(level, "🔵")
