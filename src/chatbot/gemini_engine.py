"""
Gemini Engine
=============
Wraps the official Google Gen AI SDK (google-genai) — the current SDK
recommended by Google, superseding the legacy google-generativeai package.

Install:  pip install google-genai

Interface (matches ollama_engine / basic_engine):
  is_available() → bool
  ask(messages, stream) → str | Generator[str, None, None]
  get_status() → str
  get_active_model() → str

Design principles
-----------------
- NO startup API probing.  is_available() only verifies configuration
  (key present, SDK importable, client created).  The first real user
  request initialises the active model.
- Lazy model selection: _active_model is set on the first successful ask().
- Full exception tracebacks are logged — never swallowed.
- RESOURCE_EXHAUSTED (429) is treated as a TRANSIENT per-model error with
  exponential back-off retry, not permanent quota exhaustion.
- Permanent errors (invalid key, 404 model not found) abort immediately.
- Cloud environment detection: behaviour is identical across local / cloud.
"""

import logging
import time
import traceback
from typing import Generator, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level state — lazy-initialised once per process
# ---------------------------------------------------------------------------
_client = None          # google.genai.Client instance
_initialised = False    # True once _initialise() has run
_init_error: str = ""
_available_models: list[str] = []
_active_model: str = ""

# ---------------------------------------------------------------------------
# Retry configuration
# ---------------------------------------------------------------------------
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0   # seconds (doubles each attempt)


# ---------------------------------------------------------------------------
# Public status helpers
# ---------------------------------------------------------------------------

def get_status() -> str:
    """Return the exact diagnostic reason for failure or a status string."""
    return _init_error


def get_active_model() -> str:
    """Return the currently selected model name (empty until first ask())."""
    return _active_model


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sort_models_by_priority(models: list[str]) -> list[str]:
    priorities = [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
    ]

    sorted_models: list[str] = []
    for p in priorities:
        if p in models:
            sorted_models.append(p)
    for m in models:
        if "flash-lite" in m and m not in sorted_models:
            sorted_models.append(m)
    for m in models:
        if "flash" in m and m not in sorted_models:
            sorted_models.append(m)
    for m in models:
        if "pro" in m and m not in sorted_models:
            sorted_models.append(m)
    for m in models:
        if m not in sorted_models:
            sorted_models.append(m)
    return sorted_models


# Static fallback list used when model discovery fails
_STATIC_FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
]


def _discover_models() -> list[str]:
    """
    Discover available text generation models via the SDK.
    Falls back to _STATIC_FALLBACK_MODELS on any error — never raises.
    """
    global _client
    if not _client:
        return list(_STATIC_FALLBACK_MODELS)

    try:
        all_models = _client.models.list()
        valid_models: list[str] = []
        for m in all_models:
            name = getattr(m, "name", "")
            if not name.startswith("models/gemini"):
                continue

            actions = getattr(m, "supported_actions", None) or []
            methods = getattr(m, "supported_generation_methods", None) or []

            can_generate = (
                "generateContent" in actions
                or "generateContent" in methods
                or (not actions and not methods)
            )
            if not can_generate:
                continue

            skip_keywords = (
                "embedding", "tts", "-image", "-audio", "-live",
                "native-audio", "computer-use", "robotics", "omni",
            )
            if any(kw in name.lower() for kw in skip_keywords):
                continue

            clean_name = name.replace("models/", "")
            valid_models.append(clean_name)

        logger.info("[Gemini] Discovered %d models via API", len(valid_models))
        if valid_models:
            return valid_models

        logger.warning(
            "[Gemini] No suitable models from API — using static fallback list"
        )
        return list(_STATIC_FALLBACK_MODELS)

    except Exception:
        logger.warning(
            "[Gemini] Model discovery failed — using static fallback list\n%s",
            traceback.format_exc(),
        )
        return list(_STATIC_FALLBACK_MODELS)


def _classify_error(exc: Exception) -> str:
    """
    Classify a Gemini SDK exception into one of:
      "invalid_key"   — bad API key, stop immediately
      "auth_error"    — authentication / permission failure, stop immediately
      "not_found"     — model deprecated or not accessible, try next model
      "rate_limit"    — transient 429, retry with backoff
      "server_error"  — transient 5xx, retry with backoff
      "network"       — connectivity issue, stop immediately
      "unknown"       — unclassified, try next model
    """
    exc_str = str(exc).lower()
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    try:
        code = int(code)
    except (TypeError, ValueError):
        code = None

    # Invalid API key
    if (
        ("api key" in exc_str and "invalid" in exc_str)
        or "api_key_invalid" in exc_str
        or code == 400 and "api key" in exc_str
    ):
        return "invalid_key"

    # Auth / permission
    if code == 403 or "permission" in exc_str or "forbidden" in exc_str or "unauthenticated" in exc_str:
        return "auth_error"

    # Model not found / deprecated
    if code == 404 or "not_found" in exc_str or "deprecated" in exc_str or "does not exist" in exc_str:
        return "not_found"

    # Rate limit — TRANSIENT, must retry
    if code == 429 or "resource_exhausted" in exc_str or "quota" in exc_str or "rate limit" in exc_str:
        return "rate_limit"

    # Server errors — TRANSIENT
    if code in (500, 502, 503, 504) or "internal" in exc_str or "unavailable" in exc_str or "overload" in exc_str:
        return "server_error"

    # Network
    if (
        "network" in exc_str
        or "connection" in exc_str
        or "timeout" in exc_str
        or "resolve" in exc_str
        or "nameresolution" in exc_str
        or "ssl" in exc_str
    ):
        return "network"

    return "unknown"


# ---------------------------------------------------------------------------
# Initialisation — configuration verification only, no API calls
# ---------------------------------------------------------------------------

def _initialise() -> bool:
    """
    Lazy-initialise the Gemini client.

    Only verifies:
      - google-genai SDK is installed
      - GEMINI_API_KEY is set
      - genai.Client can be constructed

    Does NOT make any API calls.  Returns True on success.
    """
    global _client, _initialised, _init_error, _available_models

    if _initialised:
        return _client is not None

    try:
        from google import genai  # noqa: PLC0415
        from src.chatbot.config import GEMINI_API_KEY  # noqa: PLC0415

        if not GEMINI_API_KEY:
            _init_error = "GEMINI_API_KEY is not set"
            logger.warning("[Gemini] GEMINI_API_KEY is not set — engine disabled")
            _initialised = True
            return False

        _client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("[Gemini] Client created — API key present")

        # Discover models (falls back to static list on any error)
        discovered = _discover_models()
        _available_models = _sort_models_by_priority(discovered)
        logger.info("[Gemini] Model pool: %s", _available_models)

        _initialised = True
        return True

    except ImportError:
        _init_error = "google-genai SDK not installed (pip install google-genai)"
        logger.warning("[Gemini] SDK not installed")
        _initialised = True
        return False

    except Exception:
        _init_error = "Client initialisation failed"
        logger.error("[Gemini] Initialisation error:\n%s", traceback.format_exc())
        _initialised = True
        return False


def _build_contents(messages: list[dict]) -> tuple[list[dict], str]:
    """
    Convert the shared messages format into a (history, prompt) tuple
    compatible with the google-genai chat API.
    """
    system_text = ""
    filtered: list[dict] = []

    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            filtered.append(msg)

    history: list[dict] = []
    last_user_text = ""

    for i, msg in enumerate(filtered):
        role = "model" if msg["role"] == "assistant" else "user"
        text = msg["content"]

        if i == 0 and system_text and role == "user":
            text = f"{system_text}\n\n{text}"

        if i == len(filtered) - 1 and role == "user":
            last_user_text = text
        else:
            history.append({"role": role, "parts": [{"text": text}]})

    return history, last_user_text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_available() -> bool:
    """
    Return True if Gemini is configured and ready.

    This is a CONFIGURATION CHECK only — no API calls are made.
    The first real user message (via ask()) will initialise _active_model.
    """
    if not _initialise() or _client is None:
        return False
    if not _available_models:
        logger.warning("[Gemini] No models in pool")
        return False
    return True


def ask(
    messages: list[dict],
    stream: bool = False,
) -> Union[str, Generator[str, None, None]]:
    """
    Send messages to Gemini and return the response.

    - Selects _active_model lazily on first successful call.
    - Retries transient errors (429, 5xx) with exponential back-off.
    - Tries each model in the pool before giving up.
    - Never raises — returns an error string on total failure.
    """
    global _active_model, _available_models, _init_error

    if not is_available():
        err = f"Gemini unavailable: {_init_error}"
        logger.error("[Gemini] ask(): %s", err)
        if stream:
            def _err_gen():
                yield err
            return _err_gen()
        return err

    from src.chatbot.config import GEMINI_MODEL  # noqa: PLC0415

    # Build ordered list: active model first, then the rest of the pool
    if _active_model:
        models_to_try = [_active_model] + [
            m for m in _available_models if m != _active_model
        ]
    elif GEMINI_MODEL:
        models_to_try = [GEMINI_MODEL] + [
            m for m in _available_models if m != GEMINI_MODEL
        ]
    else:
        models_to_try = list(_available_models)

    history, prompt = _build_contents(messages)

    for model_name in models_to_try:
        result = _try_model(model_name, history, prompt, stream)
        if result is not None:
            _active_model = model_name
            return result

    err = "All Gemini models failed — see logs for details."
    logger.error("[Gemini] ask(): %s", err)
    if stream:
        def _err_gen():
            yield err
        return _err_gen()
    return err


def _try_model(
    model_name: str,
    history: list[dict],
    prompt: str,
    stream: bool,
    *,
    max_retries: int = _MAX_RETRIES,
    base_delay: float = _RETRY_BASE_DELAY,
) -> Union[str, Generator, None]:
    """
    Attempt to call model_name with exponential back-off on transient errors.
    Returns the response on success, or None to signal "try next model".
    Never raises.
    """
    delay = base_delay

    for attempt in range(1, max_retries + 1):
        try:
            chat = _client.chats.create(model=model_name, history=history)

            if stream:
                response_stream = chat.send_message_stream(prompt)
                iterator = iter(response_stream)
                try:
                    first_chunk = next(iterator)
                except StopIteration:
                    first_chunk = None

                def _stream_gen(first, rest) -> Generator[str, None, None]:
                    if first:
                        text = getattr(first, "text", None)
                        if text:
                            yield text
                    try:
                        for chunk in rest:
                            text = getattr(chunk, "text", None)
                            if text:
                                yield text
                    except Exception:
                        logger.error(
                            "[Gemini] Stream interrupted for %s:\n%s",
                            model_name,
                            traceback.format_exc(),
                        )
                        yield " [stream interrupted]"

                logger.info(
                    "[Gemini] Streaming via %s (attempt %d)", model_name, attempt
                )
                return _stream_gen(first_chunk, iterator)

            else:
                response = chat.send_message(prompt)
                logger.info(
                    "[Gemini] Response from %s (attempt %d)", model_name, attempt
                )
                return response.text

        except Exception as exc:
            error_class = _classify_error(exc)
            logger.error(
                "[Gemini] Model %s attempt %d/%d — class=%s\n%s",
                model_name,
                attempt,
                max_retries,
                error_class,
                traceback.format_exc(),
            )

            # ── Fatal errors: stop ALL model iteration immediately ────────
            if error_class == "invalid_key":
                global _init_error
                _init_error = "Invalid API key — check GEMINI_API_KEY"
                logger.error("[Gemini] Invalid API key — disabling engine")
                return None

            if error_class == "auth_error":
                _init_error = "Authentication / permission denied"
                logger.error(
                    "[Gemini] Auth error for %s — trying next model", model_name
                )
                return None

            if error_class == "network":
                _init_error = "Network unavailable"
                logger.error("[Gemini] Network error — cannot reach Gemini API")
                return None

            # ── Model-specific permanent errors: skip this model ──────────
            if error_class == "not_found":
                logger.warning(
                    "[Gemini] Model %s not found/deprecated — trying next",
                    model_name,
                )
                return None

            # ── Transient errors: retry with back-off ─────────────────────
            if error_class in ("rate_limit", "server_error"):
                if attempt < max_retries:
                    logger.warning(
                        "[Gemini] Transient %s on %s — waiting %.1fs before retry",
                        error_class,
                        model_name,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    logger.warning(
                        "[Gemini] %s on %s — exhausted retries, trying next model",
                        error_class,
                        model_name,
                    )
                    return None

            # ── Unknown error: skip this model ────────────────────────────
            logger.warning(
                "[Gemini] Unknown error on %s — trying next model", model_name
            )
            return None

    return None
