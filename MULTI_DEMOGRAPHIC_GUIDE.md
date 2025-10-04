# Multi-Demographic Campaign Generation Guide

## Overview

The enhanced Aura Cold Brew Brand Agent now features **autonomous multi-demographic campaign generation** with location-aware intelligence, weather context, and cultural understanding.

## Key Features

### 1. **Location Intelligence**
- Real-time weather data integration
- Hemisphere-aware seasonal detection
- Temperature-based product recommendations

### 2. **Cultural Context Analysis**
- Pre-configured demographic profiles for US, AU, and GB
- Cultural theme mapping by season
- Competitor landscape analysis

### 3. **Strategic Mismatch Detection**
- Automatic detection of product-weather misalignments
- Smart product pivoting (e.g., hot brew in winter, iced brew in summer)
- Actionable recommendations for each market

### 4. **Multi-Demographic Targeting**
- Generates separate campaigns for each demographic segment
- Tailored messaging for different age groups and lifestyles
- Demographic-specific image generation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                        (main.py)                             │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Weather    │    │   Cultural   │    │    LinkUp    │
│   Context    │    │   Analysis   │    │    Search    │
│  (weather_   │    │ (cultural_   │    │  (linkup_    │
│   utils.py)  │    │  utils.py)   │    │   utils.py)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   TrueFoundry    │
                    │   LLM (GPT-5)    │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │     Freepik      │
                    │  Image Gen API   │
                    └──────────────────┘
```

## New Endpoint

### `/generate_multi_demographic_campaign`

**Request:**
```json
{
  "city": "Sydney",
  "country_code": "AU"
}
```

**Response:**
```json
{
  "city": "Sydney",
  "country": "AU",
  "weather_context": "hot weather, clear skies, summer season",
  "season": "summer",
  "temperature": "28°C / 82.4°F",
  "discovered_event": "Sydney Festival happening in January...",
  "competitor_analysis": "Agent Analysis (AU):\nLocation: Australia, Season: Summer\n⚠️ STRATEGIC NOTE: Seasons are reversed from Northern Hemisphere - December is peak summer!\n...",
  "recommended_product": "Aura Iced Brew",
  "strategic_action": "PROCEED AS PLANNED",
  "campaigns": [
    {
      "demographic_segment": "Coastal Professionals",
      "age_range": "25-40",
      "headline": "Cool Down Your Sydney Festival with Aura Iced Brew",
      "body": "Beat the summer heat at Sydney Festival with our perfectly chilled Aura Iced Brew. Refreshing, energizing, and made for beach-loving professionals who don't compromise on quality.",
      "image_url": "https://...",
      "strategic_notes": "Emphasizes beach culture, festival energy, and premium quality for active professionals"
    },
    {
      "demographic_segment": "Young Urbanites",
      "age_range": "20-30",
      "headline": "Your Festival Fuel: Aura Iced Brew",
      "body": "...",
      "image_url": "https://...",
      "strategic_notes": "..."
    }
  ],
  "total_campaigns": 3
}
```

## Example Use Cases

### Example 1: USA Winter Campaign

**Input:**
```json
{
  "city": "New York",
  "country_code": "US"
}
```

**Agent Behavior:**
- Detects: Winter season, cold temperatures (2°C)
- Analysis: Identifies "hygge," "cozy moments," "fireside comfort" as cultural themes
- Strategic Mismatch: Cold brew in freezing weather
- Action: Pivots to "Aura Hot Brew" product
- Generates: 3 campaigns for Urban Millennials, Gen Z Professionals, and Suburban Families
- Themes: Warm indulgence, cozy coffee shops, winter comfort

### Example 2: Australia Summer Campaign

**Input:**
```json
{
  "city": "Sydney",
  "country_code": "AU"
}
```

**Agent Behavior:**
- Detects: Summer season (December!), hot temperatures (28°C)
- Analysis: Identifies "beach parties," "iced drinks," "cooling refreshment" as themes
- Strategic Alignment: Perfect match for cold beverages
- Action: Recommends "Aura Iced Brew"
- Generates: 3 campaigns for Coastal Professionals, Young Urbanites, Regional Families
- Themes: Beach lifestyle, festival energy, outdoor activities

## Configuration

### Environment Variables Required

```bash
# Required
TRUEFOUNDRY_API_KEY=your_truefoundry_key
FREEPIK_API_KEY=your_freepik_key
LINKUP_API_KEY=your_linkup_key

# Optional (uses mock data if not provided)
OPENWEATHER_API_KEY=your_openweather_key

# Optional
DEMO_MODE=False  # Set to True for fast demo responses
```

### Company Profile

The brand information is hardcoded in `config/company_profile.py`:

- **Brand Identity**: Aura Cold Brew positioning, values, voice
- **Visual Identity**: Logo, colors, design principles
- **Product Portfolio**: Core products (Cold Brew, Iced Brew, Hot Brew)
- **Target Audiences**: Primary, secondary, tertiary segments
- **Marketing Guidelines**: Messaging pillars, content themes

To customize for a different brand, edit this file.

### Demographic Profiles

Cultural and demographic data is defined in `utils/cultural_utils.py`:

- **US**: 3 demographic segments with cultural themes by season
- **AU**: 3 demographic segments with reversed seasons
- **GB**: 2 demographic segments with UK-specific themes

Add new countries by extending the `DEMOGRAPHIC_PROFILES` dictionary.

## Workflow Steps

The `/generate_multi_demographic_campaign` endpoint executes:

1. **Weather Context Gathering** (weather_utils.py)
   - Fetches current weather via OpenWeatherMap API
   - Determines season based on hemisphere
   - Generates marketing-relevant context

2. **Competitor Analysis** (cultural_utils.py)
   - Analyzes cultural themes for the location
   - Identifies competitor positioning
   - Maps seasonal cultural moments

3. **Local Event Discovery** (linkup_utils.py)
   - Searches for upcoming local events
   - Finds timely marketing opportunities
   - Provides real-time relevance

4. **Strategic Mismatch Detection** (cultural_utils.py)
   - Checks product-weather alignment
   - Detects seasonal mismatches
   - Recommends product pivots

5. **Multi-Demographic Campaign Generation** (main.py)
   - Iterates through all demographic segments
   - Generates tailored copy for each segment
   - Creates demographic-specific images
   - Compiles comprehensive response

## File Structure

```
ai-agents-hackathon/
├── main.py                          # FastAPI app with endpoints
├── config/
│   └── company_profile.py           # Hardcoded brand information
├── utils/
│   ├── weather_utils.py             # Weather & seasonal context
│   ├── cultural_utils.py            # Demographics & cultural analysis
│   ├── linkup_utils.py              # Event discovery
│   └── freepik_utils.py             # Image generation
├── requirements.txt                 # Python dependencies
└── MULTI_DEMOGRAPHIC_GUIDE.md       # This file
```

## Running the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start the Server
```bash
uvicorn main:app --reload
```

### 4. Test the Endpoint
```bash
curl -X POST "http://localhost:8000/generate_multi_demographic_campaign" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Sydney",
    "country_code": "AU"
  }'
```

### 5. View API Docs
Navigate to: `http://localhost:8000/docs`

## Testing Individual Utilities

Each utility module can be tested standalone:

```bash
# Test weather utility
python utils/weather_utils.py

# Test cultural analysis
python utils/cultural_utils.py

# Test LinkUp search
python utils/linkup_utils.py

# Test Freepik image generation
python utils/freepik_utils.py

# Test company profile
python config/company_profile.py
```

## Key Improvements Over Original

| Feature | Original | Enhanced |
|---------|----------|----------|
| **Location Awareness** | City name only | Weather, season, hemisphere detection |
| **Cultural Context** | Generic | Country-specific themes and demographics |
| **Product Selection** | Fixed (Cold Brew) | Dynamic based on weather/season |
| **Target Audience** | Single campaign | Multiple demographic-specific campaigns |
| **Strategic Intelligence** | None | Mismatch detection and recommendations |
| **Brand Rules** | Passed as parameter | Hardcoded company profile |
| **Seasonal Awareness** | None | Hemisphere-aware with cultural themes |

## Advanced Features

### Hemisphere-Aware Seasons
The system automatically detects that December is **summer** in Australia but **winter** in the USA, adjusting campaigns accordingly.

### Strategic Pivoting
When the system detects a mismatch (e.g., cold brew in freezing weather), it:
1. Flags the mismatch
2. Recommends alternative products
3. Adjusts messaging strategy
4. Generates appropriate campaigns

### Cultural Theme Mapping
Each country has season-specific cultural themes:
- **US Winter**: hygge, fireside, holiday gatherings
- **AU Summer**: beach parties, Christmas BBQs, cricket season
- **GB Summer**: festivals, Wimbledon, beer gardens

## Future Enhancements

- [ ] Add more countries (CA, NZ, DE, FR, JP)
- [ ] Real-time A/B testing integration
- [ ] Sentiment analysis of competitor ads
- [ ] Multi-language support with DeepL
- [ ] Historical performance tracking
- [ ] Dynamic demographic profile learning
- [ ] Integration with social media APIs
- [ ] Campaign scheduling and automation

## Troubleshooting

**Issue**: Weather API returns mock data
- **Solution**: Add `OPENWEATHER_API_KEY` to `.env` file

**Issue**: No demographic campaigns generated
- **Solution**: Ensure `TRUEFOUNDRY_API_KEY` is valid and model is accessible

**Issue**: Image generation fails
- **Solution**: Check `FREEPIK_API_KEY` and API quota

**Issue**: LinkUp search returns generic results
- **Solution**: Verify `LINKUP_API_KEY` or accept fallback behavior

## API Rate Limits

Be aware of rate limits for external APIs:
- **OpenWeatherMap**: 60 calls/minute (free tier)
- **Freepik**: Varies by plan
- **LinkUp**: Check your subscription
- **TrueFoundry**: Check your quota

## License

This project is part of the AI Agents Hackathon.
