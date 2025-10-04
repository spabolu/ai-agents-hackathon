import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# --- 1. INITIAL SETUP ---

# Load the environment variables (like API key) from the .env file
load_dotenv()

# Get the Perplexity API key from the environment variables
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# Create an instance of the FastAPI application
app = FastAPI()


# --- 2. DEFINE DATA MODELS ---

# This defines what the incoming request data should look like.
# It expects a JSON object with a single key "query" which is a string.
class SearchRequest(BaseModel):
    query: str


# --- 3. CREATE THE API ENDPOINT ---

# This creates an endpoint that listens for POST requests at the "/search" URL.
@app.post("/search")
def run_perplexity_search(request: SearchRequest):
    """
    Receives a query, sends it to the Perplexity API, and returns the result.
    """
    print(f"Received query: {request.query}")

    # This is the header that proves you have a valid API key
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    # This is the data payload we're sending to Perplexity
    payload = {
        "model": "llama-3-sonar-large-32k-online",
        "messages": [
            {"role": "user", "content": request.query}
        ]
    }

    # Make the actual API request to Perplexity
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json=payload
    )

    # Check for errors
    if response.status_code != 200:
        return {"error": "Failed to get response from Perplexity", "details": response.text}

    # Return the JSON response from Perplexity
    return response.json()


# --- 4. CREATE A ROOT ENDPOINT FOR TESTING ---

# This is a simple endpoint to check if your server is running.
@app.get("/")
def read_root():
    return {"status": "Marketing Sentience Agent is online"}
