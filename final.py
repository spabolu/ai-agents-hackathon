# --- 1. IMPORTS ---
from __future__ import annotations
import os
import time
import requests
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from openai import OpenAI

# Import your custom utility functions.
# Make sure you have these files:
# ./utils/linkup_utils.py -> contains perform_web_search(city: str)
# ./utils/freepik_utils.py -> contains create_image(keywords: list)
from utils.linkup_utils import perform_web_search
from utils.freepik_utils import create_image


# --- 2. INITIAL SETUP & CONFIGURATION ---

# Load environment variables from a .env file
load_dotenv()

CONFIDENCE_THRESHOLD = 85
# DEMO_MODE ensures a fast and reliable demo by returning a pre-built response.
# Set this to "False" in your TrueFoundry environment variables to use the live API.
DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")  # Kept for future integration

# Startup check for the most critical API key
if not OPENAI_API_KEY and not DEMO_MODE:
    raise ValueError("FATAL ERROR: OPENAI_API_KEY environment variable not set and not in DEMO_MODE.")

# Initialize the FastAPI application
app = FastAPI(
    title="Autonomous Brand Agent (Aura Cold Brew)",
    description="An AI agent that generates on-brand, competitive marketing responses.",
    version="2.0.0"
)

# Configure the TrueFoundry LLM Client
# Make sure your .env file has TRUEFOUNDRY_API_KEY="your-key-here"
try:
    tfy_client = OpenAI(
        api_key=os.getenv("TRUEFOUNDRY_API_KEY"),
        base_url="https://llm-gateway.truefoundry.com/"
    )
except TypeError:
    print("ERROR: TRUEFOUNDRY_API_KEY not found in .env file.")
    tfy_client = None


# --- 3. DEFINE API DATA MODELS ---

class CampaignRequest(BaseModel):
    brand_rules: str
    city: str

class CampaignResponse(BaseModel):
    discovered_opportunity: str
    headline: str
    body: str
    image_url: str

class AdRequest(BaseModel):
    competitor_ad_text: str

class AdGenerationResponse(BaseModel):
    status: str
    confidence_score: int
    ad_copy: str
    generated_tagline: Optional[str] = None
    translated_copy: Optional[str] = None
    image_prompt: Optional[str] = None
    competitor_ad_text: str


# --- 4. CREATE THE CORE API ENDPOINT ---

@app.post("/generate_opportunity_campaign", response_model=CampaignResponse)
async def generate_campaign(request: CampaignRequest):
    """
    This endpoint orchestrates the entire autonomous marketing workflow.
    """
    print("--- New Campaign Generation Request ---")
    print(f"City: {request.city} | Brand Rules: {request.brand_rules}")

    # == STEP 1: DISCOVER A REAL-TIME OPPORTUNITY ==
    # Use the LinkUp function to find a timely local event.
    print("\n[1/3] 🕵️  Discovering local opportunities with LinkUp...")
    try:
        discovered_event = await perform_web_search(request.city)
        if not discovered_event:
            raise ValueError("No event found.")
        print(f"  > Opportunity Found: {discovered_event}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform LinkUp search: {e}")


    # == STEP 2: GENERATE AD COPY WITH THE LLM ==
    # Craft a detailed prompt and get the LLM to generate the campaign.
    print("\n[2/3] 🧠  Generating creative campaign with TrueFoundry LLM...")
    if not tfy_client:
         raise HTTPException(status_code=500, detail="TrueFoundry client not initialized. Check API key.")

    prompt = f"""
    You are an expert marketing strategist. Your task is to create a hyper-local ad campaign.

    CONTEXT:
    - Your Brand Rules: "{request.brand_rules}"
    - Target City: "{request.city}"
    - Discovered Local Opportunity: "{discovered_event}"

    TASK:
    Generate a complete ad campaign based on this opportunity.
    Respond ONLY with a valid JSON object in the following format:
    {{
        "headline": "A short, catchy headline (max 10 words).",
        "body": "A compelling body text (2-3 sentences).",
        "image_keywords": ["A list of", "5 descriptive keywords", "for a stock photo"]
    }}
    """

    try:
        response = tfy_client.chat.completions.create(
            model="autonomous-marketer/gpt-5", # Your specified model
            messages=[
                {"role": "system", "content": "You are a marketing expert that only responds in JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} # Use JSON mode for reliability
        )
        llm_output = response.choices[0].message.content
        ad_content = json.loads(llm_output)
        print(f"  > Ad Content Generated: {ad_content}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get response from LLM: {e}")


    # == STEP 3: CREATE THE AD CREATIVE ==
    # Use the keywords from the LLM to find an image with Freepik.
    print("\n[3/3] 🎨  Creating ad visual with Freepik...")
    try:
        image_keywords = ad_content.get("image_keywords", ["default", "image"])
        image_url = await create_image(image_keywords)
        print(f"  > Image URL: {image_url}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create image with Freepik: {e}")

    print("\n--- ✅ Campaign Generation Complete! ---")

    # == STEP 4: RETURN THE FINAL CAMPAIGN ==
    return CampaignResponse(
        discovered_opportunity=discovered_event,
        headline=ad_content["headline"],
        body=ad_content["body"],
        image_url=image_url,
    )


# --- 5. HELPER FUNCTIONS FOR AD GENERATION ---

def _log_mock(data: AdGenerationResponse):
    """
    Mocks logging for the hackathon demo. In a real application, this would
    write to a live database (ClickHouse) and send metrics (Datadog).
    """
    print("--- ANALYTICS LOG ---")
    print(f"Timestamp: {time.time()}")
    print(f"Status: {data.status}")
    print(f"Confidence Score: {data.confidence_score}")
    print(f"Ad Copy: {data.ad_copy[:50]}...")
    print("--------------------------")


def _get_brand_rules() -> str:
    """Mocks fetching brand rules for 'Aura Cold Brew'."""
    return """
    ## Brand Identity: Aura Cold Brew
    - **Persona**: Premium, recognizable, global.
    - **Values**: Sustainability, innovation, modern on-the-go lifestyle.
    - **Iconography**: Green Mermaid logo, strong clean typography.
    ## Target Audience
    - **Primary**: Young professionals, urban dwellers, social media active.
    - **Vibe**: Refreshing, portable, high-quality for summer.
    ## Visual Directions
    - **Style**: Minimalist vector art, flat design.
    - **Color**: Pastel backgrounds for summer freshness.
    - **Focus**: Aura Cold Brew can and Green Mermaid logo must be front and center.
    """


def _build_openai_prompt(competitor_ad: str, brand_rules: str) -> str:
    """Builds the structured prompt for the OpenAI API call."""
    return f"""
    You are the autonomous marketing agent for "Aura Cold Brew". Your brand guidelines: {brand_rules}.
    A competitor ad says: '{competitor_ad}'.
    Generate a complete, on-brand response. Follow these steps:
    1.  **Generate Ad Copy**: Write compelling ad copy following brand rules.
    2.  **Generate Tagline**: Create a NEW, witty, competitive tagline.
    3.  **Generate Image Prompt**: Create a concise, descriptive prompt for a Freepik-style image generator, following all 'Visual Directions'.
    4.  **Score Confidence**: Provide a confidence score (1-100).
    Format your response as a single JSON object with keys: "confidence_score", "ad_copy", "generated_tagline", and "image_keywords".
    """


# --- 6. COMPETITIVE AD GENERATION ENDPOINT ---

@app.post("/generate-response-ad", response_model=AdGenerationResponse, summary="Generate a competitive response ad")
def generate_ad(request: AdRequest):
    start_time = time.time()

    # --- HACKATHON DEMO SHORTCUT ---
    # If in DEMO_MODE, return a pre-built, high-quality response instantly.
    # This makes your demo fast and reliable.
    if not DEMO_MODE:
        mock_response = {
            "status": "approved",
            "confidence_score": 95,
            "ad_copy": "Don't settle for a temporary jolt. Elevate your day with the smooth, sustained energy of Aura Cold Brew. Crafted for clarity, not crashes.",
            "generated_tagline": "Aura Cold Brew: Your Daily Ritual, Perfected.",
            "image_prompt": "Minimalist vector art of a sleek Aura Cold Brew can with a green mermaid logo, on a soft pastel mint background, clean typography.",
            "competitor_ad_text": request.competitor_ad_text
        }
        response_data = AdGenerationResponse(**mock_response)
        _log_mock(response_data)
        duration_ms = (time.time() - start_time) * 1000
        print(f"METRICS: ad_generation.status.approved, duration: {duration_ms:.2f}ms")
        return response_data

    # --- LIVE API CALL LOGIC (Disabled in Demo Mode) ---
    brand_rules = _get_brand_rules()
    openai_prompt = _build_openai_prompt(request.competitor_ad_text, brand_rules)

    try:
        openai_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": "gpt-4-turbo", "messages": [{"role": "user", "content": openai_prompt}],
                  "response_format": {"type": "json_object"}},
            timeout=30
        )
        openai_response.raise_for_status()
        content = openai_response.json()['choices'][0]['message']['content']
        ad_data = json.loads(content)

        confidence_score = ad_data.get("confidence_score", 0)
        ad_copy = ad_data.get("ad_copy", "Error: No ad copy.")
        generated_tagline = ad_data.get("generated_tagline", "Error: No tagline.")
        image_keywords = ad_data.get("image_keywords", "Minimalist coffee can")

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error communicating with OpenAI API: {e}")

    # The rest of the logic for confidence check, translation, etc. would go here...
    final_ad_package = AdGenerationResponse(
        status="approved", confidence_score=confidence_score, ad_copy=ad_copy,
        generated_tagline=generated_tagline, translated_copy=f"(ES) {ad_copy}",
        image_prompt=image_keywords, competitor_ad_text=request.competitor_ad_text
    )
    _log_mock(final_ad_package)
    return final_ad_package


# --- 7. CREATE A ROOT ENDPOINT FOR HEALTH CHECKS ---
@app.get("/", summary="Check service status")
def read_root():
    return {"message": "Aura Cold Brew Brand Agent (Final Demo Version) is online!"}