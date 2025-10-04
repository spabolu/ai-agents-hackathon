"""
Company Profile Configuration
Hardcoded brand information for the autonomous marketing agent.
"""

COMPANY_PROFILE = {
    "brand_name": "Aura Cold Brew",
    "tagline": "Elevate Your Moment",
    "industry": "Beverage - Premium Coffee",
    
    "brand_identity": {
        "persona": "Premium, recognizable, global coffee brand",
        "positioning": "High-quality, sustainable, modern lifestyle beverage",
        "values": [
            "Sustainability and environmental responsibility",
            "Innovation in product and experience",
            "Modern on-the-go lifestyle enablement",
            "Premium quality without compromise",
            "Community and connection"
        ],
        "voice": "Confident, warm, aspirational yet accessible",
        "tone_attributes": ["authentic", "premium", "friendly", "inspiring"]
    },
    
    "visual_identity": {
        "logo": "Green Mermaid emblem",
        "primary_colors": ["Forest Green", "Cream White", "Rich Brown"],
        "typography": "Clean, modern sans-serif with strong hierarchy",
        "style": "Minimalist with premium touches",
        "photography_style": "Natural lighting, authentic moments, product-focused",
        "design_principles": [
            "Minimalist vector art and flat design",
            "Pastel backgrounds for freshness and approachability",
            "Product and logo must be prominently featured",
            "Clean composition with intentional negative space"
        ]
    },
    
    "product_portfolio": {
        "core_products": [
            {
                "name": "Aura Cold Brew",
                "description": "Smooth, sustained energy without the crash",
                "key_features": ["slow-steeped", "less acidic", "naturally sweet", "high caffeine"],
                "target_occasion": "daily ritual, work fuel, afternoon pick-me-up"
            },
            {
                "name": "Aura Iced Brew",
                "description": "Refreshing iced coffee for warm days",
                "key_features": ["instantly refreshing", "perfectly chilled", "customizable", "summer-ready"],
                "target_occasion": "hot weather, beach trips, outdoor activities, social gatherings"
            },
            {
                "name": "Aura Hot Brew",
                "description": "Warm comfort in every cup",
                "key_features": ["rich aroma", "warming", "comforting", "premium beans"],
                "target_occasion": "cold mornings, cozy moments, winter warmth, fireside relaxation"
            }
        ],
        "seasonal_variants": [
            "Pumpkin Spice Cold Brew (Autumn)",
            "Peppermint Mocha (Winter)",
            "Vanilla Sweet Cream (Spring)",
            "Tropical Mango Fusion (Summer)"
        ]
    },
    
    "target_audiences": {
        "primary": {
            "segment": "Young Professionals & Urban Millennials",
            "age_range": "25-40",
            "psychographics": [
                "Career-focused and ambitious",
                "Values quality and authenticity",
                "Socially and environmentally conscious",
                "Active on social media",
                "Seeks convenient premium experiences"
            ],
            "behaviors": [
                "Daily coffee ritual",
                "Works in office or hybrid",
                "Values work-life balance",
                "Willing to pay premium for quality"
            ]
        },
        "secondary": {
            "segment": "Gen Z & Students",
            "age_range": "18-27",
            "psychographics": [
                "Digital natives",
                "Value-conscious but quality-seeking",
                "Trend-aware and socially conscious",
                "Community-oriented"
            ],
            "behaviors": [
                "Studies or early career",
                "Social coffee experiences",
                "Influenced by social media",
                "Seeks Instagram-worthy moments"
            ]
        },
        "tertiary": {
            "segment": "Active Lifestyle Enthusiasts",
            "age_range": "28-45",
            "psychographics": [
                "Health and wellness focused",
                "Active and outdoorsy",
                "Sustainability-minded",
                "Premium quality seekers"
            ],
            "behaviors": [
                "Pre/post-workout fuel",
                "Outdoor activities",
                "Fitness-oriented lifestyle",
                "Natural product preference"
            ]
        }
    },
    
    "marketing_guidelines": {
        "messaging_pillars": [
            "Quality: Premium ingredients and careful craftsmanship",
            "Sustainability: Ethically sourced, environmentally responsible",
            "Lifestyle: Fits seamlessly into modern, active lives",
            "Community: Bringing people together over great coffee"
        ],
        "content_themes": [
            "Daily rituals and routines",
            "Moments of pause and reflection",
            "Social connection and gathering",
            "Personal achievement and motivation",
            "Seasonal celebrations and traditions"
        ],
        "do_use": [
            "Authentic, relatable scenarios",
            "Clear product benefits",
            "Seasonal and timely relevance",
            "Local community connections",
            "Aspirational yet achievable lifestyle"
        ],
        "do_not_use": [
            "Generic stock imagery",
            "Overly corporate or stiff language",
            "Unrealistic or staged scenarios",
            "Competitor comparisons (direct)",
            "Health claims without substantiation"
        ]
    },
    
    "competitive_positioning": {
        "key_differentiators": [
            "Superior cold brew process (20-hour steep)",
            "Sustainable sourcing and packaging",
            "Premium quality at accessible price point",
            "Strong community presence and local engagement",
            "Innovative seasonal offerings"
        ],
        "competitive_advantages": [
            "Recognized global brand with local touch",
            "Extensive distribution network",
            "Strong brand loyalty and community",
            "Innovation in product development",
            "Sustainability leadership"
        ],
        "market_position": "Premium accessible - higher quality than mass market, more accessible than luxury"
    },
    
    "campaign_objectives": {
        "awareness": "Increase brand recognition in new markets and demographics",
        "consideration": "Position Aura as the preferred choice for quality coffee",
        "conversion": "Drive trial and purchase through timely, relevant campaigns",
        "loyalty": "Build lasting relationships through consistent quality and values alignment"
    }
}


def get_company_profile():
    """Returns the complete company profile."""
    return COMPANY_PROFILE


def get_brand_rules_text() -> str:
    """Returns formatted brand rules for LLM prompts."""
    profile = COMPANY_PROFILE
    
    rules = f"""
## Brand Identity: {profile['brand_name']}
**Tagline**: {profile['tagline']}

**Persona**: {profile['brand_identity']['persona']}
**Positioning**: {profile['brand_identity']['positioning']}

**Core Values**:
{chr(10).join(f"- {value}" for value in profile['brand_identity']['values'])}

**Brand Voice**: {profile['brand_identity']['voice']}
**Tone**: {', '.join(profile['brand_identity']['tone_attributes'])}

## Visual Identity
**Logo**: {profile['visual_identity']['logo']}
**Colors**: {', '.join(profile['visual_identity']['primary_colors'])}
**Typography**: {profile['visual_identity']['typography']}
**Style**: {profile['visual_identity']['style']}

**Design Principles**:
{chr(10).join(f"- {principle}" for principle in profile['visual_identity']['design_principles'])}

## Product Portfolio
**Core Products**:
{chr(10).join(f"- {p['name']}: {p['description']}" for p in profile['product_portfolio']['core_products'])}

## Target Audience
**Primary**: {profile['target_audiences']['primary']['segment']} ({profile['target_audiences']['primary']['age_range']})
**Secondary**: {profile['target_audiences']['secondary']['segment']} ({profile['target_audiences']['secondary']['age_range']})

## Marketing Guidelines
**Messaging Pillars**: {', '.join(profile['marketing_guidelines']['messaging_pillars'])}

**DO USE**: {', '.join(profile['marketing_guidelines']['do_use'])}
**DO NOT USE**: {', '.join(profile['marketing_guidelines']['do_not_use'])}

## Competitive Positioning
{chr(10).join(f"- {diff}" for diff in profile['competitive_positioning']['key_differentiators'])}
"""
    return rules


def get_product_for_season(season: str, temperature: float) -> dict:
    """
    Recommends the best product variant based on season and temperature.
    
    Args:
        season: Current season
        temperature: Temperature in Celsius
    
    Returns:
        Product dictionary from the portfolio
    """
    products = COMPANY_PROFILE['product_portfolio']['core_products']
    
    # Temperature-based logic
    if temperature > 25:
        # Hot weather - recommend iced
        return products[1]  # Aura Iced Brew
    elif temperature < 10:
        # Cold weather - recommend hot
        return products[2]  # Aura Hot Brew
    else:
        # Moderate weather - recommend cold brew
        return products[0]  # Aura Cold Brew
    
    return products[0]  # Default to cold brew


if __name__ == "__main__":
    print("=== COMPANY PROFILE ===\n")
    print(get_brand_rules_text())
    print("\n=== PRODUCT RECOMMENDATION TEST ===")
    print(f"Summer (30°C): {get_product_for_season('summer', 30)['name']}")
    print(f"Winter (5°C): {get_product_for_season('winter', 5)['name']}")
    print(f"Spring (18°C): {get_product_for_season('spring', 18)['name']}")
