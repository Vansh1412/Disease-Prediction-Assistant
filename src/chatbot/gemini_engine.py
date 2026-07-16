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

Handles:
- Missing API key
- Package not installed
- Connectivity / quota failures
- Streaming and non-streaming modes
- Conversation history (role mapping: "user"/"assistant" → Gemini content)
- System prompt injection into the first user turn

Never raises exceptions — all errors are logged and returned as strings.
"""

import logging
from typing import Generator, Union

logger = logging.getLogger(__name__)

# Module-level client — lazy-initialised once per process
_client = None          # google.genai.Client instance
_initialised = False
_init_error: str = ""
_available_models: list[str] = []
_active_model: str = ""

def get_status() -> str:
    """Return the exact diagnostic reason for failure or status."""
    return _init_error

def get_active_model() -> str:
    """Return the currently selected model name."""
    return _active_model

def _sort_models_by_priority(models: list[str]) -> list[str]:
    priorities = [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
    ]

    sorted_models = []
    # 1. Exact matches in priority order
    for p in priorities:
        if p in models:
            sorted_models.append(p)

    # 2. Other flash-lite models
    for m in models:
        if "flash-lite" in m and m not in sorted_models:
            sorted_models.append(m)

    # 3. Other flash models
    for m in models:
        if "flash" in m and m not in sorted_models:
            sorted_models.append(m)

    # 4. Other pro models
    for m in models:
        if "pro" in m and m not in sorted_models:
            sorted_models.append(m)

    # 5. Any other remaining models (fallback)
    for m in models:
        if m not in sorted_models:
            sorted_models.append(m)

    return sorted_models


# Static fallback list used when model discovery fails (quota/network)
_STATIC_FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
]

def _discover_models() -> list[str]:
    """Discover available text generation models via the SDK.

    The new google-genai SDK exposes 'supported_actions' (not the older
    'supported_generation_methods').  We accept either field so the engine
    works across SDK versions.

    Returns a prioritised list of model IDs, or _STATIC_FALLBACK_MODELS if
    the API call fails (e.g. quota exceeded at discovery time).
    """
    global _client
    if not _client:
        return list(_STATIC_FALLBACK_MODELS)

    try:
        all_models = _client.models.list()
        valid_models = []
        for m in all_models:
            name = getattr(m, "name", "")
            if not name.startswith("models/gemini"):
                continue

            # New SDK: supported_actions  (preferred)
            actions = getattr(m, "supported_actions", None) or []
            # Legacy SDK: supported_generation_methods
            methods = getattr(m, "supported_generation_methods", None) or []

            # Accept the model if either field confirms it supports generation,
            # OR if both fields are empty (some SDK versions omit them).
            can_generate = (
                "generateContent" in actions
                or "generateContent" in methods
                or (not actions and not methods)  # assume capable if unknown
            )
            if not can_generate:
                continue

            # Exclude embedding / TTS / vision-only / audio models
            skip_keywords = ("embedding", "tts", "-image", "-audio", "-live",
                             "native-audio", "computer-use", "robotics", "omni")
            if any(kw in name.lower() for kw in skip_keywords):
                continue

            clean_name = name.replace("models/", "")
            valid_models.append(clean_name)

        logger.info("[Gemini] Discovered %d models via API", len(valid_models))
        if valid_models:
            return valid_models

        # API returned models but none matched — use static list
        logger.warning("[Gemini] No suitable models found via API — using static fallback list")
        return list(_STATIC_FALLBACK_MODELS)

    except Exception as exc:
        exc_str = str(exc).lower()
        if "429" in exc_str or "quota" in exc_str or "resource_exhausted" in exc_str:
            logger.warning("[Gemini] Quota exceeded during model discovery — using static fallback list")
        else:
            logger.warning("[Gemini] Failed to list models (%s) — using static fallback list", exc)
        return list(_STATIC_FALLBACK_MODELS)

def _initialise() -> bool:
    """Lazy-initialise the Gemini client. Returns True on success."""
    global _client, _initialised, _init_error, _available_models

    if _initialised:
        return _client is not None

    try:
        from google import genai
        from src.chatbot.config import GEMINI_API_KEY

        if not GEMINI_API_KEY:
            _init_error = "API Key missing"
            logger.warning("[Gemini] API Key missing")
            _initialised = True
            return False

        _client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("[Gemini] SDK Loaded — API Key present")

        # Discover models (falls back to static list on quota/network errors)
        discovered = _discover_models()
        _available_models = _sort_models_by_priority(discovered)
        logger.info("[Gemini] Model pool: %s", _available_models)

        _initialised = True
        return True
    except ImportError:
        _init_error = "google-genai SDK not installed (pip install google-genai)"
        logger.warning("[Gemini] SDK missing")
        _initialised = True
        return False
    except Exception as exc:
        _init_error = str(exc)
        logger.error("[Gemini] initialisation failed — %s", exc)
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


def is_available() -> bool:
    """Return True if Gemini is reachable with the configured key."""
    global _available_models, _active_model, _init_error
    if not _initialise() or _client is None:
        return False

    if not _available_models:
        _init_error = "No Gemini models available"
        logger.warning("[Gemini] No Gemini models available")
        logger.info("[Gemini] Switching to Ollama")
        return False

    from src.chatbot.config import GEMINI_MODEL
    models_to_try = [GEMINI_MODEL] if GEMINI_MODEL else _available_models.copy()

    for model_name in models_to_try:
        logger.info("[Gemini] Trying: %s", model_name)
        try:
            _client.models.generate_content(
                model=model_name,
                contents="ping",
            )
            logger.info("[Gemini] Connected — selected model: %s", model_name)
            _active_model = model_name
            return True
        except Exception as exc:
            exc_str = str(exc).lower()

            # ── Account-wide fatal errors — stop immediately ──────────────
            if ("api key" in exc_str and "invalid" in exc_str) or "api_key_invalid" in exc_str:
                _init_error = "Invalid API key"
                logger.warning("[Gemini] Invalid API key")
                return False
            if ("network" in exc_str or "connection" in exc_str
                    or "timeout" in exc_str or "resolve" in exc_str
                    or "nameresolution" in exc_str):
                _init_error = "Internet unavailable"
                logger.warning("[Gemini] Internet unavailable")
                return False
            if "503" in exc_str or ("500" in exc_str and "internal" in exc_str):
                _init_error = "Temporary server issue"
                logger.warning("[Gemini] Temporary server issue")
                return False

            # ── Per-model failures — try the next model ───────────────────
            if "404" in exc_str or "not_found" in exc_str or "deprecated" in exc_str:
                logger.warning("[Gemini] Model %s not found/deprecated — trying next", model_name)
                continue
            if "403" in exc_str or "permission" in exc_str:
                logger.warning("[Gemini] Model %s permission denied — trying next", model_name)
                continue
            if "429" in exc_str or "quota" in exc_str or "resource_exhausted" in exc_str:
                logger.warning("[Gemini] Model %s quota exceeded — trying next", model_name)
                continue

            # Unknown error — log and try next
            logger.warning("[Gemini] Model %s error: %s — trying next", model_name, exc_str[:120])
            continue

    _init_error = "Model retired or not found"
    logger.warning("[Gemini] All models unavailable")
    logger.info("[Gemini] Switching to Ollama")
    return False


def ask(
    messages: list[dict],
    stream: bool = False,
) -> Union[str, Generator[str, None, None]]:
    """
    Send messages to Gemini and return the response.
    """
    global _active_model, _available_models, _init_error
    
    if not _active_model and not is_available():
        err = f"Gemini unavailable: {_init_error}"
        logger.error("[Gemini] ask: %s", err)
        if stream:
            def _err_gen(): yield err
            return _err_gen()
        return err

    from src.chatbot.config import GEMINI_MODEL
    models_to_try = [_active_model] if _active_model else []
    if not GEMINI_MODEL:
        for m in _available_models:
            if m not in models_to_try:
                models_to_try.append(m)

    history, prompt = _build_contents(messages)

    for i, model_name in enumerate(models_to_try):
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
                        if text: yield text
                    try:
                        for chunk in rest:
                            text = getattr(chunk, "text", None)
                            if text: yield text
                    except Exception as exc:
                        logger.error("[Gemini] stream error — %s", exc)
                        yield " [stream interrupted]"

                _active_model = model_name
                return _stream_gen(first_chunk, iterator)
            else:
                response = chat.send_message(prompt)
                _active_model = model_name
                return response.text

        except Exception as exc:
            exc_str = str(exc).lower()
            logger.warning("[Gemini] Model %s failed during ask: %s", model_name, exc_str)
            if "404" in exc_str or "not_found" in exc_str or "deprecated" in exc_str or "permission" in exc_str or "403" in exc_str:
                if i < len(models_to_try) - 1:
                    logger.info("[Gemini] Trying next model...")
                    continue
            
            err = f"Gemini request failed: {exc}"
            logger.error("[Gemini] ask: API call failed — %s", exc)
            if stream:
                def _err_gen(): yield err
                return _err_gen()
            return err

    err = "All Gemini models failed."
    logger.error("[Gemini] ask: %s", err)
    if stream:
        def _err_gen(): yield err
        return _err_gen()
    return err
