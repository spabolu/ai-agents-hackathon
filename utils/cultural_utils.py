import asyncio
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# --- 1. DEMOGRAPHIC & CULTURAL PROFILES ---

DEMOGRAPHIC_PROFILES = {
    "US": {
        "country": "United States",
        "demographics": [
            {
                "segment": "Urban Millennials",
                "age_range": "25-40",
                "characteristics": ["tech-savvy", "sustainability-focused", "experience-driven", "social media active"],
                "values": ["authenticity", "convenience", "wellness", "social responsibility"],
                "lifestyle": "fast-paced urban lifestyle, coffee shop culture, work-from-anywhere"
            },
            {
                "segment": "Gen Z Professionals",
                "age_range": "18-27",
                "characteristics": ["digital natives", "value-conscious", "trend-aware", "community-oriented"],
                "values": ["inclusivity", "transparency", "innovation", "mental health"],
                "lifestyle": "hybrid work, side hustles, content creation, eco-conscious"
            },
            {
                "segment": "Suburban Families",
                "age_range": "30-50",
                "characteristics": ["family-focused", "quality-seeking", "time-constrained", "health-conscious"],
                "values": ["family time", "reliability", "value for money", "health"],
                "lifestyle": "busy schedules, school runs, weekend activities, meal planning"
            }
        ],
        "cultural_themes": {
            "winter": ["hygge", "cozy moments", "holiday gatherings", "fireside comfort", "snow days", "warm indulgence"],
            "spring": ["renewal", "fresh starts", "outdoor activities", "spring cleaning", "Easter celebrations"],
            "summer": ["beach trips", "BBQs", "road trips", "outdoor concerts", "Fourth of July", "vacation mode"],
            "autumn": ["pumpkin spice", "back to school", "football season", "Thanksgiving", "fall foliage", "harvest"]
        },
        "competitor_themes": ["personal indulgence", "premium quality", "convenience", "loyalty rewards"],
        "local_events_focus": ["sports events", "music festivals", "food festivals", "holiday parades"]
    },
    "AU": {
        "country": "Australia",
        "demographics": [
            {
                "segment": "Coastal Professionals",
                "age_range": "25-40",
                "characteristics": ["outdoor-oriented", "laid-back", "health-focused", "beach culture"],
                "values": ["work-life balance", "quality", "sustainability", "local support"],
                "lifestyle": "beach mornings, café culture, active lifestyle, weekend adventures"
            },
            {
                "segment": "Young Urbanites",
                "age_range": "20-30",
                "characteristics": ["cosmopolitan", "food-focused", "socially conscious", "travel-minded"],
                "values": ["experiences", "diversity", "innovation", "community"],
                "lifestyle": "brunch culture, festivals, fitness, exploring local spots"
            },
            {
                "segment": "Regional Families",
                "age_range": "30-55",
                "characteristics": ["community-focused", "practical", "outdoor-loving", "traditional"],
                "values": ["family", "reliability", "Australian-made", "value"],
                "lifestyle": "sports weekends, community events, outdoor activities, local shopping"
            }
        ],
        "cultural_themes": {
            "summer": ["beach parties", "Christmas BBQs", "cricket season", "New Year celebrations", "cooling refreshment", "outdoor living"],
            "autumn": ["back to school", "footy finals", "harvest festivals", "mild weather", "outdoor dining"],
            "winter": ["cozy cafés", "ski season", "comfort food", "indoor gatherings", "warm drinks"],
            "spring": ["spring racing", "flower shows", "outdoor festivals", "warmer days", "renewal"]
        },
        "competitor_themes": ["iced drinks", "beach lifestyle", "Australian-made", "mateship"],
        "local_events_focus": ["sporting events", "beach festivals", "music festivals", "cultural celebrations"],
        "seasonal_note": "Seasons are reversed from Northern Hemisphere - December is peak summer!"
    },
    "GB": {
        "country": "United Kingdom",
        "demographics": [
            {
                "segment": "London Professionals",
                "age_range": "25-40",
                "characteristics": ["cosmopolitan", "career-focused", "culturally diverse", "trend-aware"],
                "values": ["quality", "heritage", "innovation", "sustainability"],
                "lifestyle": "commuter culture, pub culture, theatre, weekend markets"
            },
            {
                "segment": "Students & Young Adults",
                "age_range": "18-28",
                "characteristics": ["budget-conscious", "socially active", "environmentally aware", "digital-first"],
                "values": ["affordability", "social justice", "experiences", "authenticity"],
                "lifestyle": "university life, nightlife, festivals, part-time work"
            }
        ],
        "cultural_themes": {
            "winter": ["Christmas markets", "cozy pubs", "festive cheer", "comfort food", "grey skies", "warm drinks"],
            "spring": ["Easter", "bank holidays", "garden parties", "lighter days", "renewal"],
            "summer": ["festivals", "Wimbledon", "beer gardens", "seaside trips", "long evenings"],
            "autumn": ["back to uni", "bonfire night", "autumn walks", "comfort food", "football season"]
        },
        "competitor_themes": ["heritage", "quality", "café culture", "afternoon treats"],
        "local_events_focus": ["football matches", "music festivals", "cultural events", "royal celebrations"]
    }
}


# --- 2. CULTURAL CONTEXT FUNCTIONS ---

async def get_cultural_context(country_code: str, season: str) -> Dict[str, Any]:
    """
    Retrieves cultural context and demographic information for a country.
    
    Args:
        country_code: 2-letter country code (e.g., "US", "AU", "GB")
        season: Current season ("winter", "spring", "summer", "autumn")
    
    Returns:
        Dictionary containing demographic profiles and cultural themes
    """
    profile = DEMOGRAPHIC_PROFILES.get(country_code, DEMOGRAPHIC_PROFILES["US"])
    
    return {
        "country": profile["country"],
        "country_code": country_code,
        "demographics": profile["demographics"],
        "seasonal_themes": profile["cultural_themes"].get(season, []),
        "competitor_themes": profile["competitor_themes"],
        "local_events_focus": profile["local_events_focus"],
        "seasonal_note": profile.get("seasonal_note", ""),
        "total_segments": len(profile["demographics"])
    }


async def analyze_competitor_themes(country_code: str, season: str, weather_context: Dict[str, Any]) -> str:
    """
    Generates an analysis of competitor themes based on location and season.
    
    Args:
        country_code: 2-letter country code
        season: Current season
        weather_context: Weather data from weather_utils
    
    Returns:
        String analysis of competitor landscape
    """
    cultural = await get_cultural_context(country_code, season)
    
    analysis = f"Agent Analysis ({country_code}):\n"
    analysis += f"Location: {cultural['country']}, Season: {season.title()}\n"
    
    if cultural.get('seasonal_note'):
        analysis += f"⚠️  STRATEGIC NOTE: {cultural['seasonal_note']}\n"
    
    analysis += f"Weather Context: {weather_context.get('context', 'N/A')}\n"
    analysis += f"Temperature: {weather_context.get('temperature_celsius', 'N/A')}°C\n\n"
    
    analysis += f"Key Competitor Themes: {', '.join(cultural['competitor_themes'])}\n"
    analysis += f"Seasonal Cultural Themes: {', '.join(cultural['seasonal_themes'][:5])}\n"
    analysis += f"Target Demographics: {cultural['total_segments']} segments identified\n"
    
    return analysis


async def get_demographic_segments(country_code: str) -> List[Dict[str, Any]]:
    """
    Returns all demographic segments for a country.
    
    Args:
        country_code: 2-letter country code
    
    Returns:
        List of demographic segment dictionaries
    """
    profile = DEMOGRAPHIC_PROFILES.get(country_code, DEMOGRAPHIC_PROFILES["US"])
    return profile["demographics"]


def generate_demographic_insights(demographic: Dict[str, Any], season: str, weather: Dict[str, Any]) -> str:
    """
    Generates marketing insights for a specific demographic segment.
    
    Args:
        demographic: Demographic segment data
        season: Current season
        weather: Weather context
    
    Returns:
        String with actionable insights
    """
    insights = f"Demographic: {demographic['segment']} ({demographic['age_range']})\n"
    insights += f"Key Characteristics: {', '.join(demographic['characteristics'][:3])}\n"
    insights += f"Core Values: {', '.join(demographic['values'][:3])}\n"
    insights += f"Lifestyle Context: {demographic['lifestyle']}\n"
    insights += f"Season: {season.title()}, Weather: {weather.get('weather_description', 'N/A')}\n"
    
    return insights


# --- 3. STRATEGIC MISMATCH DETECTION ---

async def detect_strategic_mismatches(
    country_code: str, 
    season: str, 
    weather: Dict[str, Any],
    product_type: str = "cold brew"
) -> Dict[str, Any]:
    """
    Detects strategic mismatches between product and market conditions.
    
    Args:
        country_code: 2-letter country code
        season: Current season
        weather: Weather context
        product_type: Type of product being marketed
    
    Returns:
        Dictionary with mismatch analysis and recommendations
    """
    temp = weather.get('temperature_celsius', 20)
    is_hot = temp > 25
    is_cold = temp < 10
    
    mismatches = []
    recommendations = []
    
    # Check temperature vs product type
    if product_type == "cold brew" and is_cold:
        mismatches.append(f"Cold beverage in cold weather ({temp}°C)")
        recommendations.append("Consider promoting hot beverage variants or emphasize indoor enjoyment")
    
    if product_type == "hot beverage" and is_hot:
        mismatches.append(f"Hot beverage in hot weather ({temp}°C)")
        recommendations.append("Pivot to iced variants or emphasize air-conditioned comfort")
    
    # Check seasonal alignment
    _ = await get_cultural_context(country_code, season)  # Validate country/season combo
    if country_code == "AU" and season == "summer" and product_type == "cold brew":
        recommendations.append("OPPORTUNITY: Perfect alignment! Summer in Australia - emphasize beach, cooling, festive celebrations")
    
    if country_code == "US" and season == "winter" and product_type == "cold brew":
        mismatches.append("Winter season may reduce cold beverage appeal")
        recommendations.append("Emphasize indoor coziness, premium quality, or introduce seasonal hot variants")
    
    return {
        "has_mismatches": len(mismatches) > 0,
        "mismatches": mismatches,
        "recommendations": recommendations,
        "strategic_action": "PIVOT REQUIRED" if len(mismatches) > 0 else "PROCEED AS PLANNED"
    }


# --- 4. STANDALONE TEST ---

if __name__ == "__main__":
    async def test_cultural():
        print("--- Testing Cultural Context Utility ---\n")
        
        # Mock weather data
        mock_weather_us = {
            "temperature_celsius": 2,
            "weather_description": "snowy",
            "context": "freezing cold weather, snowy conditions, winter season"
        }
        
        mock_weather_au = {
            "temperature_celsius": 28,
            "weather_description": "clear sky",
            "context": "hot weather, clear skies, summer season"
        }
        
        # Test US
        print("=== UNITED STATES (Winter) ===")
        analysis_us = await analyze_competitor_themes("US", "winter", mock_weather_us)
        print(analysis_us)
        
        segments_us = await get_demographic_segments("US")
        print(f"\nDemographic Segments: {len(segments_us)}")
        for seg in segments_us:
            print(f"  - {seg['segment']}: {seg['age_range']}")
        
        mismatch_us = await detect_strategic_mismatches("US", "winter", mock_weather_us, "cold brew")
        print(f"\nStrategic Analysis: {mismatch_us['strategic_action']}")
        if mismatch_us['recommendations']:
            print(f"Recommendations: {mismatch_us['recommendations'][0]}")
        
        print("\n" + "="*50 + "\n")
        
        # Test Australia
        print("=== AUSTRALIA (Summer) ===")
        analysis_au = await analyze_competitor_themes("AU", "summer", mock_weather_au)
        print(analysis_au)
        
        segments_au = await get_demographic_segments("AU")
        print(f"\nDemographic Segments: {len(segments_au)}")
        for seg in segments_au:
            print(f"  - {seg['segment']}: {seg['age_range']}")
        
        mismatch_au = await detect_strategic_mismatches("AU", "summer", mock_weather_au, "cold brew")
        print(f"\nStrategic Analysis: {mismatch_au['strategic_action']}")
        if mismatch_au['recommendations']:
            print(f"Recommendations: {mismatch_au['recommendations'][0]}")
    
    asyncio.run(test_cultural())
