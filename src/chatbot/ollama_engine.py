"""
Ollama Engine
=============
Wraps the core Ollama HTTP logic behind the unified engine interface:
  ask(messages, stream) → str | Generator[str, None, None]
  is_available()        → bool

This is the canonical Ollama adapter for the chatbot_router layer.
The original standalone client is preserved in legacy_ollama_engine.py.

Handles:
- Connection failures
- Missing model
- Timeouts
- Streaming and non-streaming modes

Never raises exceptions to the caller.
"""

import json
import logging
import requests
from typing import Generator, Union

from src.chatbot.config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT, LLM_TEMPERATURE, LLM_TOP_P, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

_CHAT_ENDPOINT = f"{OLLAMA_HOST}/api/chat"
_TAGS_ENDPOINT = f"{OLLAMA_HOST}/api/tags"

# Persistent HTTP session for connection reuse
_session = requests.Session()


def is_available() -> bool:
    """
    Return True if the Ollama server is reachable AND the configured model
    is present.  Uses a short timeout so the probe is fast.
    """
    try:
        resp = _session.get(_TAGS_ENDPOINT, timeout=5)
        resp.raise_for_status()
        models = [m.get("name", "") for m in resp.json().get("models", [])]
        # Accept prefix match (e.g. "qwen2.5:3b" matches "qwen2.5:3b-instruct")
        available = any(OLLAMA_MODEL in m or m.startswith(OLLAMA_MODEL.split(":")[0]) for m in models)
        if available:
            logger.info("OllamaEngine: model '%s' found on %s.", OLLAMA_MODEL, OLLAMA_HOST)
        else:
            logger.warning(
                "OllamaEngine: server reachable but model '%s' not found. Available: %s",
                OLLAMA_MODEL, models,
            )
        return available
    except requests.exceptions.RequestException as exc:
        logger.warning("OllamaEngine: server unreachable — %s", exc)
        return False


def ask(
    messages: list[dict],
    stream: bool = False,
) -> Union[str, Generator[str, None, None]]:
    """
    Send messages to Ollama and return the response.

    Parameters
    ----------
    messages : list of {"role": str, "content": str}
    stream   : if True, returns a generator yielding text chunks

    Returns
    -------
    str | Generator[str, None, None]
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": stream,
        "options": {
            "temperature": LLM_TEMPERATURE,
            "top_p": LLM_TOP_P,
            "num_predict": LLM_MAX_TOKENS,
        },
    }

    try:
        response = _session.post(
            _CHAT_ENDPOINT,
            json=payload,
            stream=stream,
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()

        if stream:
            def _stream_gen() -> Generator[str, None, None]:
                try:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    yield data["message"]["content"]
                            except json.JSONDecodeError:
                                continue
                except Exception as exc:
                    logger.error("OllamaEngine: stream error — %s", exc)
                    yield " [stream interrupted]"

            return _stream_gen()
        else:
            return response.json()["message"]["content"]

    except requests.exceptions.Timeout:
        logger.error("OllamaEngine: request timed out after %ss.", OLLAMA_TIMEOUT)
        err = "Error: Local model request timed out. Please try again."
        if stream:
            def _err_gen(): yield err
            return _err_gen()
        return err

    except requests.exceptions.RequestException as exc:
        logger.error("OllamaEngine: connection error — %s", exc)
        err = "Error: Cannot connect to local Qwen model. Ensure Ollama is running."
        if stream:
            def _err_gen(): yield err
            return _err_gen()
        return err

    except Exception as exc:
        logger.error("OllamaEngine: unexpected error — %s", exc)
        err = f"Error: Unexpected Ollama error — {exc}"
        if stream:
            def _err_gen(): yield err
            return _err_gen()
        return err
