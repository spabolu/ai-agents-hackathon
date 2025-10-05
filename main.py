# --- 1. IMPORTS ---
from __future__ import annotations
import os
import time
import requests
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, List
from dataclasses import dataclass
from openai import OpenAI

# Import your custom utility functions.
# Make sure you have these files:
# ./utils/linkup_utils.py -> contains perform_web_search(city: str)
# ./utils/freepik_utils.py -> contains create_image(keywords: list)
from utils.linkup_utils import perform_web_search
from utils.freepik_utils import create_image
from utils.weather_utils import get_weather_context
from utils.cultural_utils import (
    analyze_competitor_themes,
    get_demographic_segments,
    generate_demographic_insights,
    detect_strategic_mismatches
)
from config.company_profile import get_company_profile, get_brand_rules_text, get_product_for_season
from utils.translation_utils import (
    translate_texts_async,
    DeepLConfigurationError,
    DeepLTranslationError,
)


# --- Company metadata helpers -------------------------------------------------


@dataclass(frozen=True)
class CompanyMetadata:
    """Canonical representation of the company identity used in prompts."""

    company_name: str
    default_product_name: str
    tagline: str


def _split_company_and_product(label: str) -> tuple[str, str]:
    """Split strings like 'Aura Cold Brew' into ('Aura', 'Cold Brew')."""

    if not label:
        return "", ""

    parts = label.split(" ", 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _strip_company_prefix(product_name: str, company_name: str) -> str:
    """Remove the company prefix from product labels when present."""

    if not product_name or not company_name:
        return product_name

    prefix = f"{company_name} "
    return product_name[len(prefix):] if product_name.startswith(prefix) else product_name


COMPANY_PROFILE = get_company_profile()
_company_name, _brand_product = _split_company_and_product(COMPANY_PROFILE["brand_name"])
if not _brand_product:
    first_core_product = COMPANY_PROFILE["product_portfolio"]["core_products"][0]["name"]
    _brand_product = _strip_company_prefix(first_core_product, _company_name)

COMPANY_METADATA = CompanyMetadata(
    company_name=_company_name,
    default_product_name=_brand_product,
    tagline=COMPANY_PROFILE["tagline"],
)
BRAND_RULES_TEXT = get_brand_rules_text()
DEEPL_TARGET_LANG = "ZH"


# --- Translation helpers ------------------------------------------------------


async def _translate_pairs_async(pairs: List[tuple[str, Optional[str]]]) -> dict[str, str]:
    """Translate multiple named texts to the configured target language."""

    keys: List[str] = []
    payload: List[str] = []
    for key, text in pairs:
        if text:
            keys.append(key)
            payload.append(text)

    if not payload:
        return {}

    try:
        translations = await translate_texts_async(payload, target_lang=DEEPL_TARGET_LANG)
        return {key: value for key, value in zip(keys, translations)}
    except DeepLConfigurationError:
        print("INFO: DeepL translation skipped (DEEPL_API_KEY not configured).")
    except DeepLTranslationError as exc:
        print("Running...")
    except Exception as exc:
        print("Running...")
    return {}


# --- 2. INITIAL SETUP & CONFIGURATION ---

# Load environment variables from a .env file
load_dotenv()

CONFIDENCE_THRESHOLD = 85
# DEMO_MODE ensures a fast and reliable demo by returning a pre-built response.
# Set this to "False" in your TrueFoundry environment variables to use the live API.
DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

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
    headline_mandarin: Optional[str] = None
    body_mandarin: Optional[str] = None
    tagline_mandarin: Optional[str] = None
    tagline: Optional[str] = None
    image_url: str

class AdRequest(BaseModel):
    competitor_ad_text: str

class AdGenerationResponse(BaseModel):
    status: str
    confidence_score: int
    ad_copy: str
    generated_tagline: Optional[str] = None
    ad_copy_mandarin: Optional[str] = None
    tagline_mandarin: Optional[str] = None
    translated_copy: Optional[str] = None
    image_prompt: Optional[str] = None
    competitor_ad_text: str

class MultiDemographicRequest(BaseModel):
    city: str
    country_code: str  # e.g., "US", "AU", "GB"

class DemographicCampaign(BaseModel):
    demographic_segment: str
    age_range: str
    headline: str
    body: str
    headline_mandarin: Optional[str] = None
    body_mandarin: Optional[str] = None
    tagline_mandarin: Optional[str] = None
    tagline: Optional[str] = None
    image_url: str
    strategic_notes: str

class MultiDemographicResponse(BaseModel):
    city: str
    country: str
    weather_context: str
    season: str
    temperature: str
    discovered_event: str
    competitor_analysis: str
    recommended_product: str
    strategic_action: str
    campaigns: List[DemographicCampaign]
    total_campaigns: int


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
        "tagline": "A fresh tagline customized for this opportunity and city.",
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
        tagline = ad_content.get("tagline") or COMPANY_METADATA.tagline
        # Use brand defaults but swap in the contextual tagline
        image_url = await create_image(
            keywords=image_keywords,
            company_name=COMPANY_METADATA.company_name,
            product_name=COMPANY_METADATA.default_product_name,
            tagline_prompt=tagline,
        )
        print(f"  > Image URL: {image_url}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create image with Freepik: {e}")

    translations = await _translate_pairs_async(
        [
            ("headline", ad_content.get("headline")),
            ("body", ad_content.get("body")),
            ("tagline", tagline),
        ]
    )

    print("\n--- ✅ Campaign Generation Complete! ---")

    # == STEP 4: RETURN THE FINAL CAMPAIGN ==
    return CampaignResponse(
        discovered_opportunity=discovered_event,
        headline=ad_content["headline"],
        body=ad_content["body"],
        headline_mandarin=translations.get("headline"),
        body_mandarin=translations.get("body"),
        tagline_mandarin=translations.get("tagline"),
        tagline=tagline,
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
    print(f"Confidence: {data.confidence_score}")
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
async def generate_ad(request: AdRequest):
    start_time = time.time()

    # --- HACKATHON DEMO SHORTCUT ---
    # If in DEMO_MODE, return a pre-built, high-quality response instantly.
    # This makes your demo fast and reliable.
    if DEMO_MODE:
        mock_response = {
            "status": "approved",
            "confidence_score": 95,
            "ad_copy": "Don't settle for a temporary jolt. Elevate your day with the smooth, sustained energy of Aura Cold Brew. Crafted for clarity, not crashes.",
            "generated_tagline": "Aura Cold Brew: Your Daily Ritual, Perfected.",
            "image_prompt": "Minimalist vector art of a sleek Aura Cold Brew can with a green mermaid logo, on a soft pastel mint background, clean typography.",
            "competitor_ad_text": request.competitor_ad_text
        }
        translation_map = await _translate_pairs_async(
            [
                ("ad_copy", mock_response["ad_copy"]),
                ("tagline", mock_response["generated_tagline"]),
            ]
        )
        mock_response["ad_copy_mandarin"] = translation_map.get("ad_copy")
        mock_response["tagline_mandarin"] = translation_map.get("tagline")
        mock_response["translated_copy"] = translation_map.get("ad_copy")
        response_data = AdGenerationResponse(**mock_response)
        _log_mock(response_data)
        duration_ms = (time.time() - start_time) * 1000
        print(f"METRICS: ad_generation.status.approved, duration: {duration_ms:.2f}ms")
        response_data.exec_duration_ms = (time.time() - start_time) * 1000  # type: ignore[attr-defined]
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
    translation_map = await _translate_pairs_async(
        [
            ("ad_copy", ad_copy),
            ("tagline", generated_tagline),
        ]
    )

    final_ad_package = AdGenerationResponse(
        status="approved",
        confidence_score=confidence_score,
        ad_copy=ad_copy,
        generated_tagline=generated_tagline,
        ad_copy_mandarin=translation_map.get("ad_copy"),
        tagline_mandarin=translation_map.get("tagline"),
        translated_copy=translation_map.get("ad_copy"),
        image_prompt=image_keywords,
        competitor_ad_text=request.competitor_ad_text,
    )
    final_ad_package.exec_duration_ms = (time.time() - start_time) * 1000  # type: ignore[attr-defined]
    _log_mock(final_ad_package)
    return final_ad_package


# --- 7. MULTI-DEMOGRAPHIC CAMPAIGN GENERATION ---

@app.post("/generate_multi_demographic_campaign", response_model=MultiDemographicResponse)
async def generate_multi_demographic_campaign(request: MultiDemographicRequest):
    """
    Advanced autonomous marketing workflow that generates location-aware,
    multi-demographic campaigns with weather and cultural context.
    
    This endpoint demonstrates true marketing sentience by:
    1. Analyzing weather and seasonal context
    2. Discovering local events
    3. Understanding cultural nuances
    4. Detecting strategic mismatches
    5. Generating tailored campaigns for each demographic segment
    """
    print("="*80)
    print("🤖 AUTONOMOUS MULTI-DEMOGRAPHIC CAMPAIGN GENERATION")
    print("="*80)
    print(f"Location: {request.city}, {request.country_code}")
    
    # Get hardcoded company profile
    company_profile = COMPANY_PROFILE
    brand_rules = BRAND_RULES_TEXT
    
    # == STEP 1: GATHER CONTEXTUAL INTELLIGENCE ==
    print("\n[1/5] 🌤️  Gathering weather and seasonal context...")
    try:
        weather = await get_weather_context(request.city, request.country_code)
        print(f"  > Temperature: {weather['temperature_celsius']}°C / {weather['temperature_fahrenheit']}°F")
        print(f"  > Conditions: {weather['weather_description']}")
        print(f"  > Season: {weather['season']} ({weather['hemisphere']} hemisphere)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather context: {e}")
    
    # == STEP 2: ANALYZE COMPETITOR LANDSCAPE ==
    print("\n[2/5] 🔍  Analyzing competitor themes and cultural context...")
    try:
        competitor_analysis = await analyze_competitor_themes(
            request.country_code, 
            weather['season'], 
            weather
        )
        print("  > Analysis complete")
        print(competitor_analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze competitors: {e}")
    
    # == STEP 3: DISCOVER LOCAL OPPORTUNITIES ==
    print("\n[3/5] 🕵️  Discovering local events and opportunities...")
    try:
        discovered_event = await perform_web_search(request.city)
        print(f"  > Event Found: {discovered_event[:100]}...")
    except Exception as e:
        print(f"  > Warning: Could not find events: {e}")
        discovered_event = f"General local marketing opportunity in {request.city}"
    
    # == STEP 4: DETECT STRATEGIC MISMATCHES ==
    print("\n[4/5] ⚠️  Detecting strategic mismatches...")
    try:
        mismatch_analysis = await detect_strategic_mismatches(
            request.country_code,
            weather['season'],
            weather,
            "cold brew"
        )
        print(f"  > Strategic Action: {mismatch_analysis['strategic_action']}")
        if mismatch_analysis['recommendations']:
            for rec in mismatch_analysis['recommendations']:
                print(f"    - {rec}")
        
        # Get recommended product based on conditions
        recommended_product = get_product_for_season(
            weather['season'], 
            weather['temperature_celsius']
        )
        print(f"  > Recommended Product: {recommended_product['name']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed strategic analysis: {e}")
    
    # == STEP 5: GENERATE CAMPAIGNS FOR EACH DEMOGRAPHIC ==
    print("\n[5/5] 🎨  Generating campaigns for each demographic segment...")
    
    if not tfy_client:
        raise HTTPException(status_code=500, detail="TrueFoundry client not initialized. Check API key.")
    
    try:
        demographic_segments = await get_demographic_segments(request.country_code)
        campaigns = []
        
        for idx, demographic in enumerate(demographic_segments, 1):
            print(f"\n  [{idx}/{len(demographic_segments)}] Generating for: {demographic['segment']}")
            
            # Generate demographic-specific insights
            demo_insights = generate_demographic_insights(demographic, weather['season'], weather)
            
            # Build a comprehensive prompt for the LLM
            prompt = f"""
You are an expert marketing strategist for {company_profile['brand_name']}.

BRAND GUIDELINES:
{brand_rules}

LOCATION & CONTEXT:
- City: {request.city}, {request.country_code}
- Weather: {weather['context']}
- Temperature: {weather['temperature_celsius']}°C
- Season: {weather['season']} ({weather['hemisphere']} hemisphere)
- Local Event: {discovered_event}

RECOMMENDED PRODUCT:
- Product: {recommended_product['name']}
- Description: {recommended_product['description']}
- Key Features: {', '.join(recommended_product['key_features'])}

TARGET DEMOGRAPHIC:
{demo_insights}

STRATEGIC CONTEXT:
{competitor_analysis}

STRATEGIC ACTION REQUIRED: {mismatch_analysis['strategic_action']}
{chr(10).join(f"- {rec}" for rec in mismatch_analysis['recommendations']) if mismatch_analysis['recommendations'] else ''}

TASK:
Create a highly targeted ad campaign for this specific demographic that:
1. Aligns with the weather and seasonal context
2. Leverages the local event opportunity
3. Speaks directly to this demographic's values and lifestyle
4. Follows all brand guidelines
5. Addresses any strategic mismatches identified

Respond ONLY with a valid JSON object:
{{
    "headline": "A compelling headline (max 12 words) that resonates with this demographic",
    "body": "Engaging body copy (2-3 sentences) that connects the product to their lifestyle and the local context",
    "tagline": "A short tagline tailored to this demographic and context",
    "image_keywords": ["5-7 specific keywords", "for product photography", "that appeals to this demographic"],
    "strategic_notes": "Brief notes on how this campaign addresses the demographic's needs and any strategic pivots made"
}}
"""
            
            # Call the LLM
            response = tfy_client.chat.completions.create(
                model="autonomous-marketer/gpt-5",
                messages=[
                    {"role": "system", "content": "You are a marketing expert that only responds in JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            campaign_data = json.loads(response.choices[0].message.content)
            
            # Generate image for this campaign
            print("    > Generating image...")
            image_keywords = campaign_data.get("image_keywords", ["Aura Cold Brew", "premium coffee"])
            product_display_name = _strip_company_prefix(
                recommended_product['name'], COMPANY_METADATA.company_name
            )
            campaign_tagline = campaign_data.get("tagline") or COMPANY_METADATA.tagline

            # Pass brand information to image generator
            image_url = await create_image(
                keywords=image_keywords,
                company_name=COMPANY_METADATA.company_name,
                product_name=product_display_name or COMPANY_METADATA.default_product_name,
                tagline_prompt=campaign_tagline,
            )

            translations = await _translate_pairs_async(
                [
                    ("headline", campaign_data.get("headline")),
                    ("body", campaign_data.get("body")),
                    ("tagline", campaign_tagline),
                ]
            )

            # Create campaign object
            campaign = DemographicCampaign(
                demographic_segment=demographic['segment'],
                age_range=demographic['age_range'],
                headline=campaign_data['headline'],
                body=campaign_data['body'],
                headline_mandarin=translations.get("headline"),
                body_mandarin=translations.get("body"),
                tagline_mandarin=translations.get("tagline"),
                tagline=campaign_tagline,
                image_url=image_url,
                strategic_notes=campaign_data.get('strategic_notes', '')
            )
            campaigns.append(campaign)
            
            print(f"    ✓ Campaign complete for {demographic['segment']}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate campaigns: {e}")
    
    print("\n" + "="*80)
    print(f"✅ COMPLETE: Generated {len(campaigns)} demographic-specific campaigns")
    print("="*80 + "\n")
    
    # == STEP 6: RETURN COMPREHENSIVE RESPONSE ==
    return MultiDemographicResponse(
        city=request.city,
        country=weather.get('country_code', request.country_code),
        weather_context=weather['context'],
        season=weather['season'],
        temperature=f"{weather['temperature_celsius']}°C / {weather['temperature_fahrenheit']}°F",
        discovered_event=discovered_event,
        competitor_analysis=competitor_analysis,
        recommended_product=recommended_product['name'],
        strategic_action=mismatch_analysis['strategic_action'],
        campaigns=campaigns,
        total_campaigns=len(campaigns)
    )


# --- 8. CREATE A ROOT ENDPOINT FOR HEALTH CHECKS ---
@app.get("/", summary="Check service status")
def read_root():
    return {"message": "Aura Cold Brew Brand Agent (Enhanced Multi-Demographic Version) is online!"}
