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
from datetime import datetime
from uuid import uuid4

# Import your custom utility functions.
# Make sure you have these files:
# ./utils/linkup_utils.py -> contains perform_web_search(city: str)
# ./utils/freepik_utils.py -> contains create_image(keywords: list)
from utils.linkup_utils import perform_web_search
from utils.freepik_utils import create_image

# Import ClickHouse client for REAL analytics logging
try:
    from clickhouse_client import ClickHouseClient
    clickhouse_client = ClickHouseClient()
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False
    print("⚠️  ClickHouse client not available")


# --- 2. INITIAL SETUP & CONFIGURATION ---

# Load environment variables from a .env file
load_dotenv()

CONFIDENCE_THRESHOLD = 85
# DEMO_MODE optimizes for demo reliability (shorter timeouts, etc) but uses REAL APIs
DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() == "true"

# API Keys
TRUEFOUNDRY_API_KEY = os.getenv("TRUEFOUNDRY_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DATADOG_API_KEY = os.getenv("DATADOG_API_KEY")

# Datadog configuration
DATADOG_SITE = "datadoghq.com"
DATADOG_METRICS_URL = f"https://api.{DATADOG_SITE}/api/v2/series"

# Startup check for critical API keys
if not TRUEFOUNDRY_API_KEY:
    print("⚠️  WARNING: TRUEFOUNDRY_API_KEY not set - LLM calls will fail")
if not DATADOG_API_KEY:
    print("⚠️  WARNING: DATADOG_API_KEY not set - metrics will not be sent")

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
    This endpoint orchestrates the entire autonomous marketing workflow with REAL APIs.
    """
    start_time = time.time()

    print("=" * 80)
    print("🚀 REAL OPPORTUNITY CAMPAIGN - Using LIVE APIs")
    print("=" * 80)
    print(f"City: {request.city} | Brand Rules: {request.brand_rules}")

    # == STEP 1: DISCOVER A REAL-TIME OPPORTUNITY WITH LINKUP ==
    print("\n[1/4] 🕵️  Discovering local opportunities with Linkup...")
    try:
        discovered_event = await perform_web_search(request.city)
        if not discovered_event:
            raise ValueError("No event found.")
        print(f"  ✅ Linkup: Opportunity Found")
        print(f"     Event: {discovered_event}")
    except Exception as e:
        print(f"  ❌ Linkup search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform Linkup search: {e}")


    # == STEP 2: GENERATE AD COPY WITH TRUEFOUNDRY (GPT-5) ==
    print("\n[2/4] 🧠  Generating creative campaign with TrueFoundry LLM (GPT-5)...")
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
            model="autonomous-marketer/gpt-5",
            messages=[
                {"role": "system", "content": "You are a marketing expert that only responds in JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            timeout=20 if DEMO_MODE else 60
        )
        llm_output = response.choices[0].message.content
        ad_content = json.loads(llm_output)
        print(f"  ✅ TrueFoundry: Campaign Generated")
        print(f"     Headline: {ad_content.get('headline', 'N/A')}")
        print(f"     Body: {ad_content.get('body', 'N/A')[:60]}...")
    except Exception as e:
        print(f"  ❌ TrueFoundry API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get response from TrueFoundry LLM: {e}")


    # == STEP 3: CREATE THE AD CREATIVE WITH FREEPIK ==
    print("\n[3/4] 🎨  Creating ad visual with Freepik (Gemini 2.5 Flash)...")
    try:
        image_keywords = ad_content.get("image_keywords", ["default", "image"])
        image_url = await create_image(image_keywords)
        print(f"  ✅ Freepik: Image Generated")
        print(f"     URL: {image_url}")
    except Exception as e:
        print(f"  ⚠️  Freepik image generation failed (non-critical): {e}")
        image_url = "https://placeholder.com/campaign-image.jpg"

    # == STEP 4: LOG TO CLICKHOUSE ==
    print("\n[4/4] 📊 Logging to ClickHouse...")
    duration_ms = (time.time() - start_time) * 1000

    if CLICKHOUSE_AVAILABLE:
        try:
            request_id = str(uuid4())
            timestamp = datetime.now()

            clickhouse_client.client.insert(
                'search_queries',
                [[
                    request_id,
                    timestamp,
                    f"Local events in {request.city}",
                    'linkup',
                    'deep',
                    'sourcedAnswer',
                    1,  # result_count
                    duration_ms,
                    True  # success
                ]],
                column_names=['id', 'timestamp', 'query_text', 'api_source', 'depth',
                             'output_type', 'result_count', 'response_time_ms', 'success']
            )
            print(f"  ✅ ClickHouse: Logged campaign search (ID: {request_id})")
        except Exception as e:
            print(f"  ⚠️  ClickHouse logging failed: {e}")

    # == SEND DATADOG METRICS ==
    _send_datadog_metric("campaign.response_time_ms", duration_ms, tags=[f"city:{request.city}"])
    _send_datadog_metric("campaign.generated", 1, tags=["endpoint:generate_opportunity_campaign"])

    print(f"\n✅ COMPLETE: Campaign generation finished in {duration_ms:.2f}ms")
    print("=" * 80)

    # == RETURN THE FINAL CAMPAIGN ==
    return CampaignResponse(
        discovered_opportunity=discovered_event,
        headline=ad_content["headline"],
        body=ad_content["body"],
        image_url=image_url,
    )


# --- 5. HELPER FUNCTIONS FOR AD GENERATION ---

def _log_to_clickhouse(data: AdGenerationResponse, response_time_ms: float):
    """
    Log ad generation request to ClickHouse for REAL analytics.
    """
    if not CLICKHOUSE_AVAILABLE:
        print("⚠️  ClickHouse not available - analytics logging disabled (non-critical)")
        return

    try:
        request_id = str(uuid4())
        timestamp = datetime.now()

        # Log to api_requests_log table
        clickhouse_client.client.insert(
            'api_requests_log',
            [[
                request_id,
                timestamp,
                'ad_generation',  # Custom type
                '/generate-response-ad',
                'POST',
                json.dumps({"competitor_ad": data.competitor_ad_text[:100]}),
                200,
                json.dumps({"status": data.status, "confidence": data.confidence_score}),
                response_time_ms,
                None,  # No error
                '127.0.0.1',
                'FastAPI-Demo'
            ]],
            column_names=['id', 'timestamp', 'api_type', 'endpoint', 'request_method',
                         'request_payload', 'response_status', 'response_body',
                         'response_time_ms', 'error_message', 'client_ip', 'user_agent']
        )
        print(f"✅ ClickHouse: Logged ad generation (ID: {request_id}, Response time: {response_time_ms:.2f}ms)")
    except Exception as e:
        print(f"⚠️  ClickHouse logging failed (non-critical): {str(e)[:100]}")


def _send_datadog_metric(metric_name: str, value: float, tags: list = None):
    """
    Send REAL metric to Datadog API.
    """
    if not DATADOG_API_KEY:
        print(f"⚠️  Datadog API key not set - skipping metric: {metric_name}")
        return

    try:
        now = int(time.time())
        payload = {
            "series": [{
                "metric": metric_name,
                "type": 0,  # 0 = gauge (use integer, not string)
                "points": [{"timestamp": now, "value": value}],
                "tags": tags or []
            }]
        }

        headers = {
            "DD-API-KEY": DATADOG_API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            DATADOG_METRICS_URL,
            headers=headers,
            json=payload,
            timeout=5
        )

        if response.status_code == 202:
            print(f"✅ Datadog: Sent metric '{metric_name}' = {value} (tags: {tags})")
        else:
            print(f"⚠️  Datadog metric failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️  Datadog metric error: {e}")


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
async def generate_ad(request: AdRequest):
    start_time = time.time()

    print("=" * 80)
    print("🚀 REAL AD GENERATION - Using LIVE APIs")
    print("=" * 80)

    # Get brand rules
    brand_rules = _get_brand_rules()
    openai_prompt = _build_openai_prompt(request.competitor_ad_text, brand_rules)

    # === STEP 1: GENERATE AD COPY WITH TRUEFOUNDRY (GPT-5) ===
    print("\n[1/3] 🧠 Calling TrueFoundry LLM (GPT-5)...")

    if not tfy_client:
        raise HTTPException(status_code=500, detail="TrueFoundry client not initialized. Check API key.")

    try:
        response = tfy_client.chat.completions.create(
            model="autonomous-marketer/gpt-5",
            messages=[
                {"role": "system", "content": "You are a marketing expert that only responds in JSON."},
                {"role": "user", "content": openai_prompt}
            ],
            response_format={"type": "json_object"},
            timeout=20 if DEMO_MODE else 60  # Shorter timeout for demo
        )
        llm_output = response.choices[0].message.content
        ad_data = json.loads(llm_output)

        confidence_score = ad_data.get("confidence_score", 0)
        ad_copy = ad_data.get("ad_copy", "Error: No ad copy.")
        generated_tagline = ad_data.get("generated_tagline", "Error: No tagline.")
        image_keywords = ad_data.get("image_keywords", "Minimalist coffee can")

        print(f"  ✅ TrueFoundry Response:")
        print(f"     Confidence: {confidence_score}%")
        print(f"     Ad Copy: {ad_copy[:60]}...")
        print(f"     Tagline: {generated_tagline}")

    except Exception as e:
        print(f"  ❌ TrueFoundry API Error: {e}")
        raise HTTPException(status_code=502, detail=f"Error communicating with TrueFoundry API: {e}")

    # === STEP 2: GENERATE IMAGE WITH FREEPIK (Optional) ===
    print("\n[2/3] 🎨 Generating image with Freepik...")
    image_url = None
    try:
        if isinstance(image_keywords, list):
            image_url = await create_image(image_keywords[:5])  # Limit to 5 keywords
        else:
            image_url = await create_image([image_keywords])
        print(f"  ✅ Freepik Image URL: {image_url}")
    except Exception as e:
        print(f"  ⚠️  Freepik image generation failed (non-critical): {e}")
        image_url = "https://placeholder.com/aura-cold-brew.jpg"

    # === STEP 3: TRANSLATE WITH DEEPL (Optional - may fail if rate limited) ===
    translated_copy = None
    if DEEPL_API_KEY:
        print("\n[3/3] 🌐 Translating with DeepL (optional)...")
        try:
            # DeepL API expects auth in params for free tier, or headers for pro
            deepl_response = requests.post(
                "https://api-free.deepl.com/v2/translate",  # Use free endpoint
                headers={"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"},
                data={
                    "text": ad_copy,
                    "target_lang": "ES",
                    "formality": "prefer_more"  # Professional tone
                },
                timeout=10
            )
            if deepl_response.status_code == 200:
                translated_copy = deepl_response.json()["translations"][0]["text"]
                print(f"  ✅ DeepL Translation (ES): {translated_copy[:60]}...")
            else:
                print(f"  ⚠️  DeepL translation failed: {deepl_response.status_code} (non-critical, continuing)")
        except Exception as e:
            print(f"  ⚠️  DeepL error (non-critical, continuing): {str(e)[:80]}")

    # === DETERMINE STATUS ===
    status = "approved" if confidence_score >= CONFIDENCE_THRESHOLD else "pending_review"

    # === CREATE RESPONSE ===
    final_ad_package = AdGenerationResponse(
        status=status,
        confidence_score=confidence_score,
        ad_copy=ad_copy,
        generated_tagline=generated_tagline,
        translated_copy=translated_copy,
        image_prompt=str(image_keywords) if image_url else None,
        competitor_ad_text=request.competitor_ad_text
    )

    # === LOG TO CLICKHOUSE ===
    duration_ms = (time.time() - start_time) * 1000
    _log_to_clickhouse(final_ad_package, duration_ms)

    # === SEND DATADOG METRICS ===
    _send_datadog_metric("ad_generation.response_time_ms", duration_ms, tags=[f"status:{status}"])
    _send_datadog_metric("ad_generation.confidence_score", confidence_score, tags=[f"status:{status}"])
    _send_datadog_metric(f"ad_generation.status.{status}", 1, tags=["endpoint:generate-response-ad"])

    print(f"\n✅ COMPLETE: Ad generation finished in {duration_ms:.2f}ms")
    print("=" * 80)

    return final_ad_package


# --- 7. CREATE A ROOT ENDPOINT FOR HEALTH CHECKS ---
@app.get("/", summary="Check service status")
def read_root():
    return {"message": "Aura Cold Brew Brand Agent (Final Demo Version) is online!"}