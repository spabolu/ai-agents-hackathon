from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Literal, Optional, Union
import requests

# from linkup import LinkupClient

class LinkupAPIError(RuntimeError):
    """Raised when the Linkup API returns a non-2xx response."""


def linkup_search(
    *,
    token: str = "047b66c3-0fc9-4277-8475-2bd48eb1397c",
    q: str,
    depth: Literal["standard", "deep"] = "standard",
    output_type: Literal["sourcedAnswer", "searchResults", "structured"] = "sourcedAnswer",
    structured_output_schema: Optional[Union[str, Dict[str, Any]]] = None,
    include_images: bool = False,
    from_date: Optional[str] = None,          # "YYYY-MM-DD"
    to_date: Optional[str] = None,            # "YYYY-MM-DD"
    exclude_domains: Optional[Iterable[str]] = None,
    include_domains: Optional[Iterable[str]] = None,
    include_inline_citations: Optional[bool] = None,  # only used when output_type="sourcedAnswer"
    include_sources: Optional[bool] = None,           # only used when output_type="structured"
    base_url: str = "https://api.linkup.so",
    timeout: float = 30.0,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    """
    Call Linkup /search.

    Parameters
    ----------
    token : str
        Bearer token for Linkup (no "Bearer " prefix needed).
    q : str
        Natural-language question / query.
    depth : {"standard", "deep"}
        Search depth (precision vs. speed).
    output_type : {"sourcedAnswer", "searchResults", "structured"}
        Response format.
    structured_output_schema : Optional[str | dict]
        Required only when output_type="structured". If dict is provided, it will be json.dumps'ed.
        NOTE: The API expects this as a JSON string, not an object.
    include_images : bool
        Include images in results.
    from_date, to_date : Optional[str]
        Filter results by ISO date "YYYY-MM-DD".
    exclude_domains, include_domains : Optional[Iterable[str]]
        Domain filters.
    include_inline_citations : Optional[bool]
        Only applicable when output_type="sourcedAnswer".
    include_sources : Optional[bool]
        Only applicable when output_type="structured".
    base_url : str
        API base URL (override for testing if needed).
    timeout : float
        Request timeout (seconds).
    session : Optional[requests.Session]
        Provide your own session to reuse connections.

    Returns
    -------
    dict
        Parsed JSON response from Linkup.

    Raises
    ------
    LinkupAPIError
        If the API returns a non-2xx status.
    """
    url = f"{base_url.rstrip('/')}/v1/search"

    # Build payload with only provided fields to keep the request minimal
    payload: Dict[str, Any] = {
        "q": q,
        "depth": depth,
        "outputType": output_type,
        "includeImages": include_images,
    }

    if from_date:
        payload["fromDate"] = from_date
    if to_date:
        payload["toDate"] = to_date
    if exclude_domains is not None:
        payload["excludeDomains"] = list(exclude_domains)
    if include_domains is not None:
        payload["includeDomains"] = list(include_domains)

    # Output-type specific flags
    if output_type == "sourcedAnswer" and include_inline_citations is not None:
        payload["includeInlineCitations"] = include_inline_citations
    if output_type == "structured":
        # Ensure schema is serialized as a JSON string (API expects a string)
        if structured_output_schema is None:
            raise ValueError("structured_output_schema is required when output_type='structured'")
        if isinstance(structured_output_schema, dict):
            payload["structuredOutputSchema"] = json.dumps(structured_output_schema)
        else:
            payload["structuredOutputSchema"] = structured_output_schema
        if include_sources is not None:
            payload["includeSources"] = include_sources
    else:
        # If not structured, make sure we don't accidentally send a schema
        if structured_output_schema is not None:
            raise ValueError("structured_output_schema must be None unless output_type='structured'")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    s = session or requests.Session()
    resp = s.post(url, headers=headers, json=payload, timeout=timeout)

    if not resp.ok:
        # Try to surface API error details
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise LinkupAPIError(f"Linkup /search failed [{resp.status_code}]: {detail}")

    return resp.json()


def linkup_fetch(
    *,
    token: str = "047b66c3-0fc9-4277-8475-2bd48eb1397c",
    url: str,
    include_raw_html: bool = False,
    render_js: bool = False,
    extract_images: bool = False,
    base_url: str = "https://api.linkup.so",
    timeout: float = 30.0,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    """
    Call Linkup /fetch.

    Parameters
    ----------
    token : str
        Bearer token for Linkup (no "Bearer " prefix needed).
    url : str
        The webpage URL to fetch.
    include_raw_html : bool
        Include raw HTML in the response.
    render_js : bool
        Render the page with JavaScript (may increase latency).
    extract_images : bool
        Extract images from the page.
    base_url : str
        API base URL (override for testing if needed).
    timeout : float
        Request timeout (seconds).
    session : Optional[requests.Session]
        Provide your own session to reuse connections.

    Returns
    -------
    dict
        Parsed JSON response from Linkup (e.g., {"markdown": "...", ...}).

    Raises
    ------
    LinkupAPIError
        If the API returns a non-2xx status.
    """
    endpoint = f"{base_url.rstrip('/')}/v1/fetch"

    payload = {
        "url": url,
        "includeRawHtml": include_raw_html,
        "renderJs": render_js,
        "extractImages": extract_images,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    s = session or requests.Session()
    resp = s.post(endpoint, headers=headers, json=payload, timeout=timeout)

    if not resp.ok:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise LinkupAPIError(f"Linkup /fetch failed [{resp.status_code}]: {detail}")

    return resp.json()


# -------------------------
# Quick usage examples
# (uncomment to try)
# -------------------------
# if __name__ == "__main__":
#     TOKEN = "YOUR_LINKUP_API_KEY"
#
#     # 1) /search — sourced answer
#     ans = linkup_search(
#         token=TOKEN,
#         q="What is Microsoft's 2024 revenue?",
#         depth="standard",
#         output_type="sourcedAnswer",
#         include_images=False,
#         from_date="2025-01-01",
#         to_date="2025-01-01",
#         include_domains=["microsoft.com", "agolution.com"],
#         exclude_domains=["wikipedia.com"],
#         include_inline_citations=False,
#     )
#     print(ans)
#
#     # 2) /fetch — get markdown of a page
#     page = linkup_fetch(
#         token=TOKEN,
#         url="https://docs.linkup.so",
#         include_raw_html=False,
#         render_js=False,
#         extract_images=False,
#     )
#     print(page)


ans = linkup_search(
        # token=TOKEN,
        q="What is Microsoft's 2024 revenue?",
        depth="standard",
        output_type="sourcedAnswer",
        include_images=False,
        from_date="2024-01-01",
        # to_date="2025-01-01",
        include_domains=["microsoft.com", "agolution.com"],
        exclude_domains=["wikipedia.com"],
        include_inline_citations=False,
    )

print(json.dumps(ans, indent=2))