"""Async helpers for interacting with the Linkup API."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://api.linkup.so"


class LinkupAPIError(Exception):
    """Raised when the Linkup API returns a non-2xx response."""


def _require_token() -> str:
    token = os.getenv("LINKUP_API_KEY")
    if not token:
        raise RuntimeError("LINKUP_API_KEY environment variable is required")
    return token


async def _make_request(
    client: httpx.AsyncClient,
    url: str,
    payload: Dict[str, Any],
    timeout: float,
) -> Dict[str, Any]:
    token = _require_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        detail: Any
        try:
            detail = exc.response.json()
        except json.JSONDecodeError:
            detail = exc.response.text
        raise LinkupAPIError(f"Linkup API error [{exc.response.status_code}]: {detail}") from exc
    except httpx.RequestError as exc:
        raise LinkupAPIError(f"Linkup request failed: {exc}") from exc


async def perform_web_search(city: str) -> str:
    """Return a short summary of a notable upcoming event for the given city."""
    print(f"-> LinkUp: Searching for notable events in {city}...")
    query = (
        "What is a single, notable, upcoming local event, festival, or cultural moment in "
        f"{city} happening in the next 30-60 days? Focus on events that would attract a large public audience."
    )

    try:
        response_data = await linkup_search(q=query, output_type="sourcedAnswer", depth="standard")
        answer = response_data.get("answer")
        if not answer:
            return f"No specific upcoming events found for {city}. General city marketing is recommended."
        return answer.strip()
    except LinkupAPIError as exc:
        print(f"Error in perform_web_search: {exc}")
        return f"Could not retrieve event data for {city} due to an API error."


async def linkup_search(
    *,
    q: str,
    output_type: str = "sourcedAnswer",
    depth: str = "standard",
    timeout: float = 60.0,
    session: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """Async Linkup `/search` call used by the marketing agent."""
    url = f"{API_BASE_URL.rstrip('/')}/v1/search"
    payload = {"q": q, "outputType": output_type, "depth": depth}

    if session:
        return await _make_request(session, url, payload, timeout)
    async with httpx.AsyncClient() as client:
        return await _make_request(client, url, payload, timeout)


async def linkup_fetch(
    *,
    url_to_fetch: str,
    timeout: float = 30.0,
    session: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """Async Linkup `/fetch` helper."""
    url = f"{API_BASE_URL.rstrip('/')}/v1/fetch"
    payload = {"url": url_to_fetch}

    if session:
        return await _make_request(session, url, payload, timeout)
    async with httpx.AsyncClient() as client:
        return await _make_request(client, url, payload, timeout)


if __name__ == "__main__":
    async def _main() -> None:
        try:
            city_to_test = "New York"
            event = await perform_web_search(city_to_test)
            print("\n--- TEST SUCCEEDED ---")
            print(f"Discovered event for '{city_to_test}':\n{event}")
        except (RuntimeError, LinkupAPIError) as exc:
            print("\n--- TEST FAILED ---")
            print(f"Error: {exc}")

    asyncio.run(_main())
