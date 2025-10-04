import os
import json
import asyncio
import httpx  # The async-compatible version of 'requests'
from dotenv import load_dotenv
from typing import Any, Dict, Optional

# --- 1. CONFIGURATION ---

# Load environment variables from a .env file
load_dotenv()

# Get the API key from environment variables, with a fallback to your provided key
LINKUP_API_KEY = os.getenv("LINKUP_API_KEY", "047b66c3-0fc9-4277-8475-2bd48eb1397c")
API_BASE_URL = "https://api.linkup.so"

# --- 2. CUSTOM ERROR & HELPER FUNCTIONS ---

class LinkupAPIError(Exception):
    """Raised when the Linkup API returns a non-2xx response."""
    pass

async def _make_request(client: httpx.AsyncClient, url: str, payload: dict, timeout: float) -> dict:
    """Helper function to perform the actual async HTTP request."""
    headers = {
        "Authorization": f"Bearer {LINKUP_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except httpx.HTTPStatusError as e:
        error_details = e.response.text
        try:
            error_details = e.response.json()
        except json.JSONDecodeError:
            pass # Keep text details if not valid JSON
        raise LinkupAPIError(f"Linkup API Error [{e.response.status_code}]: {error_details}")
    except httpx.RequestError as e:
        raise LinkupAPIError(f"Request failed: {e}")

# --- 3. HIGH-LEVEL FUNCTION FOR YOUR AGENT ---

async def perform_web_search(city: str) -> str:
    """
    Finds a timely, relevant local event for a given city.

    This is a simplified wrapper around the powerful linkup_search function,
    tailored specifically for the Marketing Sentience Agent's needs.

    Args:
        city: The name of the city to search for events in.

    Returns:
        A string summarizing the most relevant discovered event.
    """
    print(f"-> LinkUp: Searching for notable events in {city}...")

    # Step 1: Craft a high-quality, natural language query
    query = f"What is a single, notable, upcoming local event, festival, or cultural moment in {city} happening in the next 30-60 days? Focus on events that would attract a large public audience."

    try:
        # Step 2: Call the low-level search function with optimal parameters
        response_data = await linkup_search(
            q=query,
            output_type="sourcedAnswer",
            depth="standard",
        )
        
        # Step 3: Extract the most useful part of the response
        answer = response_data.get("answer")
        if not answer:
            return f"No specific upcoming events found for {city}. General city marketing is recommended."
        
        return answer.strip()

    except LinkupAPIError as e:
        print(f"Error in perform_web_search: {e}")
        return f"Could not retrieve event data for {city} due to an API error."


# --- 4. LOW-LEVEL API FUNCTIONS (ADAPTED FROM YOUR SCRIPT) ---

async def linkup_search(
    q: str,
    output_type: str = "sourcedAnswer",
    depth: str = "standard",
    timeout: float = 60.0,
    session: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """
    Async version of the Linkup /search endpoint.
    (Simplified for the agent's primary use case).
    """
    url = f"{API_BASE_URL.rstrip('/')}/v1/search"
    payload = {"q": q, "outputType": output_type, "depth": depth}
    
    if session:
        return await _make_request(session, url, payload, timeout)
    async with httpx.AsyncClient() as client:
        return await _make_request(client, url, payload, timeout)

async def linkup_fetch(
    url_to_fetch: str,
    timeout: float = 30.0,
    session: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """
    Async version of the Linkup /fetch endpoint.
    """
    url = f"{API_BASE_URL.rstrip('/')}/v1/fetch"
    payload = {"url": url_to_fetch}

    if session:
        return await _make_request(session, url, payload, timeout)
    async with httpx.AsyncClient() as client:
        return await _make_request(client, url, payload, timeout)


# --- 5. STANDALONE TEST BLOCK ---
# You can run this file directly (`python utils/linkup_utils.py`) to test it.
if __name__ == "__main__":
    async def main():
        print("--- Running LinkUp Utility Standalone Test ---")
        if not LINKUP_API_KEY or "047b66c3" in LINKUP_API_KEY:
            print("WARNING: Using a default or missing LinkUp API key. Please set LINKUP_API_KEY in your .env file.")
        
        try:
            # Test the high-level function your agent will use
            city_to_test = "New York"
            event = await perform_web_search(city_to_test)
            
            print("\n--- TEST SUCCEEDED ---")
            print(f"Discovered event for '{city_to_test}':\n{event}")
        except LinkupAPIError as e:
            print("\n--- TEST FAILED ---")
            print(f"Error: {e}")

    # Run the async test function
    asyncio.run(main())
