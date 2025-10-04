# Autonomous Multi-Demographic Marketing Agent

## 🚀 Overview

An AI-powered autonomous marketing agent that generates **location-aware, multi-demographic campaigns** with real-time weather intelligence, cultural context analysis, and strategic decision-making.

### Key Innovation: Marketing Sentience

The agent demonstrates true autonomous intelligence by:
- 🌍 **Understanding Geography**: Detects that December is summer in Australia, winter in USA
- 🎯 **Strategic Pivoting**: Automatically recommends "Iced Brew" for hot weather, "Hot Brew" for cold
- 🧠 **Cultural Awareness**: Maps seasonal themes like "hygge" (US winter) vs "beach parties" (AU summer)
- 👥 **Multi-Demographic Targeting**: Generates 2-3 tailored campaigns per location
- ⚡ **Real-Time Adaptation**: Uses live weather and local event data

## ✨ Features

### 1. Location Intelligence
- Real-time weather data via OpenWeatherMap API
- Hemisphere-aware seasonal detection
- Temperature-based product recommendations

### 2. Cultural Context Analysis
- Pre-configured demographic profiles (US, AU, GB)
- Cultural theme mapping by season
- Competitor landscape analysis

### 3. Strategic Decision Making
- Automatic mismatch detection (product vs weather)
- Smart product pivoting recommendations
- Actionable insights for each market

### 4. Multi-Demographic Campaigns
- Separate campaigns for each demographic segment
- Tailored messaging for different age groups
- Demographic-specific image generation

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
# Required
TRUEFOUNDRY_API_KEY=your_truefoundry_key
FREEPIK_API_KEY=your_freepik_key
LINKUP_API_KEY=your_linkup_key

# Optional (uses mock data if not provided)
OPENWEATHER_API_KEY=your_openweather_key

# Optional
DEMO_MODE=False
```

### 3. Start the Server

```bash
uvicorn main:app --reload
```

### 4. Test the System

```bash
# Impressive hemisphere comparison demo
python test_multi_demographic.py compare

# Quick single location test
python test_multi_demographic.py single

# Test all locations
python test_multi_demographic.py all

# One-command scripted demo (server-free)
python demo.py --city Sydney --country AU
```

### 5. View API Documentation

Navigate to: `http://localhost:8000/docs`

## 📚 Documentation

- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Complete implementation overview
- **[MULTI_DEMOGRAPHIC_GUIDE.md](MULTI_DEMOGRAPHIC_GUIDE.md)** - Detailed usage guide
- **[IMAGE_GENERATION_GUIDE.md](IMAGE_GENERATION_GUIDE.md)** - Image generation documentation

## 💡 Example: USA vs Australia

### USA Winter Campaign (New York)

**Agent Analysis:**
- Detects: Winter, 2°C, snowy conditions
- Identifies: "hygge," "cozy moments," "fireside comfort"
- **Action: Pivots to "Aura Hot Brew"**

**Campaigns:** 3 demographics with warm, cozy messaging

### Australia Summer Campaign (Sydney)

**Agent Analysis:**
- Detects: Summer (December!), 28°C, clear skies
- Identifies: "beach parties," "iced drinks," "cooling refreshment"
- **Action: Recommends "Aura Iced Brew"**

**Campaigns:** 3 demographics with beach, festival messaging

## 🏗️ Architecture

```
FastAPI App → Weather + Cultural + LinkUp → TrueFoundry LLM → Freepik Images
```

## 📁 Project Structure

```
ai-agents-hackathon/
├── main.py                          # FastAPI app
├── config/company_profile.py        # Brand information
├── utils/
│   ├── weather_utils.py             # Weather context
│   ├── cultural_utils.py            # Demographics
│   ├── linkup_utils.py              # Event discovery
│   └── freepik_utils.py             # Image generation
├── test_multi_demographic.py        # Test suite
└── requirements.txt                 # Dependencies
```

## 🌟 Key Features

✅ Hardcoded company information  
✅ Location-based event search  
✅ Weather intelligence  
✅ Cultural context analysis  
✅ Multi-demographic campaigns  
✅ Autonomous strategic pivoting  

---

**Built for the AI Agents Hackathon**
