"""Utilities for translating marketing copy using the DeepL API."""

from __future__ import annotations

import os
from typing import Iterable, List, Optional, Sequence

import httpx
from dotenv import load_dotenv

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_API_URL = os.getenv("DEEPL_API_URL", "https://api-free.deepl.com/v2/translate")

DEFAULT_TIMEOUT = 30.0


class DeepLConfigurationError(RuntimeError):
    """Raised when DeepL configuration is missing or invalid."""


class DeepLTranslationError(RuntimeError):
    """Raised when DeepL returns an unexpected response."""


def _build_form_payload(texts: Sequence[str], target_lang: str, source_lang: Optional[str]) -> List[tuple[str, str]]:
    payload: List[tuple[str, str]] = [
        ("auth_key", DEEPL_API_KEY or ""),
        ("target_lang", target_lang),
    ]
    if source_lang:
        payload.append(("source_lang", source_lang))

    for text in texts:
        payload.append(("text", text))
    return payload


async def translate_texts_async(
    texts: Iterable[str],
    target_lang: str = "ZH",
    source_lang: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> List[str]:
    """Translate a sequence of texts asynchronously using DeepL."""

    text_list = [t for t in texts if t]
    if not text_list:
        return []
    if not DEEPL_API_KEY:
        raise DeepLConfigurationError("DEEPL_API_KEY not set.")

    payload = _build_form_payload(text_list, target_lang, source_lang)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(DEEPL_API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
    
    translations = data.get("translations")
    if not translations:
        raise DeepLTranslationError("DeepL response missing 'translations'.")

    return [item.get("text", "") for item in translations]


def translate_texts(
    texts: Iterable[str],
    target_lang: str = "ZH",
    source_lang: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> List[str]:
    """Translate a sequence of texts synchronously using DeepL."""

    text_list = [t for t in texts if t]
    if not text_list:
        return []
    if not DEEPL_API_KEY:
        raise DeepLConfigurationError("DEEPL_API_KEY not set.")

    payload = _build_form_payload(text_list, target_lang, source_lang)

    with httpx.Client(timeout=timeout) as client:
        response = client.post(DEEPL_API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
    
    translations = data.get("translations")
    if not translations:
        raise DeepLTranslationError("DeepL response missing 'translations'.")

    return [item.get("text", "") for item in translations]


async def translate_text_async(
    text: str,
    target_lang: str = "ZH",
    source_lang: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Translate a single text asynchronously."""

    results = await translate_texts_async([text], target_lang=target_lang, source_lang=source_lang, timeout=timeout)
    return results[0] if results else ""


def translate_text(
    text: str,
    target_lang: str = "ZH",
    source_lang: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Translate a single text synchronously."""

    results = translate_texts([text], target_lang=target_lang, source_lang=source_lang, timeout=timeout)
    return results[0] if results else ""
