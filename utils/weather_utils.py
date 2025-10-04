import os
import asyncio
import httpx
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from datetime import datetime

# --- 1. CONFIGURATION ---

load_dotenv()

# Using OpenWeatherMap API (free tier available)
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"


# --- 2. WEATHER DATA FUNCTIONS ---

async def get_weather_context(city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches current weather and seasonal context for a given city.
    
    Args:
        city: The name of the city
        country_code: Optional 2-letter country code (e.g., "US", "AU")
    
    Returns:
        Dictionary containing weather data and seasonal context
    """
    if not WEATHER_API_KEY:
        print("WARNING: OPENWEATHER_API_KEY not found. Using mock weather data.")
        return _get_mock_weather(city, country_code)
    
    location = f"{city},{country_code}" if country_code else city
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get current weather
            weather_url = f"{WEATHER_API_BASE}/weather"
            params = {
                "q": location,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
            
            response = await client.get(weather_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            temp_celsius = data["main"]["temp"]
            temp_fahrenheit = (temp_celsius * 9/5) + 32
            weather_desc = data["weather"][0]["description"]
            weather_main = data["weather"][0]["main"]
            humidity = data["main"]["humidity"]
            
            # Determine season based on hemisphere and month
            month = datetime.now().month
            is_southern = _is_southern_hemisphere(country_code)
            season = _get_season(month, is_southern)
            
            return {
                "city": city,
                "country_code": country_code,
                "temperature_celsius": round(temp_celsius, 1),
                "temperature_fahrenheit": round(temp_fahrenheit, 1),
                "weather_description": weather_desc,
                "weather_main": weather_main,
                "humidity": humidity,
                "season": season,
                "hemisphere": "southern" if is_southern else "northern",
                "context": _generate_weather_context(temp_celsius, weather_main, season)
            }
            
    except httpx.HTTPStatusError as e:
        print(f"Weather API Error: {e.response.status_code}")
        return _get_mock_weather(city, country_code)
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return _get_mock_weather(city, country_code)


def _is_southern_hemisphere(country_code: Optional[str]) -> bool:
    """Determines if a country is in the southern hemisphere."""
    southern_countries = ["AU", "NZ", "ZA", "AR", "BR", "CL", "UY", "PY", "BO", "PE"]
    return country_code in southern_countries if country_code else False


def _get_season(month: int, is_southern: bool) -> str:
    """Determines the season based on month and hemisphere."""
    # Northern hemisphere seasons
    if not is_southern:
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    # Southern hemisphere (reversed)
    else:
        if month in [12, 1, 2]:
            return "summer"
        elif month in [3, 4, 5]:
            return "autumn"
        elif month in [6, 7, 8]:
            return "winter"
        else:
            return "spring"


def _generate_weather_context(temp: float, weather: str, season: str) -> str:
    """Generates marketing-relevant weather context."""
    contexts = []
    
    # Temperature context
    if temp < 5:
        contexts.append("freezing cold weather")
    elif temp < 15:
        contexts.append("cold weather")
    elif temp < 25:
        contexts.append("mild weather")
    elif temp < 30:
        contexts.append("warm weather")
    else:
        contexts.append("hot weather")
    
    # Weather condition context
    if "rain" in weather.lower():
        contexts.append("rainy conditions")
    elif "snow" in weather.lower():
        contexts.append("snowy conditions")
    elif "clear" in weather.lower():
        contexts.append("clear skies")
    elif "cloud" in weather.lower():
        contexts.append("cloudy conditions")
    
    # Season context
    contexts.append(f"{season} season")
    
    return ", ".join(contexts)


def _get_mock_weather(city: str, country_code: Optional[str]) -> Dict[str, Any]:
    """Returns mock weather data for testing/fallback."""
    month = datetime.now().month
    is_southern = _is_southern_hemisphere(country_code)
    season = _get_season(month, is_southern)
    
    # Mock data based on typical conditions
    if country_code == "AU":
        temp = 28.0 if season == "summer" else 15.0
        weather = "Clear"
        desc = "clear sky"
    else:  # Default to US-like weather
        temp = 2.0 if season == "winter" else 25.0
        weather = "Clear"
        desc = "clear sky"
    
    return {
        "city": city,
        "country_code": country_code,
        "temperature_celsius": temp,
        "temperature_fahrenheit": round((temp * 9/5) + 32, 1),
        "weather_description": desc,
        "weather_main": weather,
        "humidity": 65,
        "season": season,
        "hemisphere": "southern" if is_southern else "northern",
        "context": _generate_weather_context(temp, weather, season),
        "mock": True
    }


# --- 3. STANDALONE TEST ---

if __name__ == "__main__":
    async def test_weather():
        print("--- Testing Weather Utility ---\n")
        
        # Test different locations
        locations = [
            ("New York", "US"),
            ("Sydney", "AU"),
            ("London", "GB"),
        ]
        
        for city, country in locations:
            print(f"Fetching weather for {city}, {country}...")
            weather = await get_weather_context(city, country)
            print(f"  Temperature: {weather['temperature_celsius']}°C / {weather['temperature_fahrenheit']}°F")
            print(f"  Conditions: {weather['weather_description']}")
            print(f"  Season: {weather['season']} ({weather['hemisphere']} hemisphere)")
            print(f"  Context: {weather['context']}")
            print()
    
    asyncio.run(test_weather())
