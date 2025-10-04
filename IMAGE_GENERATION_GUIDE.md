# Image Generation Guide

## Overview

The `create_image()` function in `utils/freepik_utils.py` now supports dynamic brand customization with company name, product name, and tagline parameters.

## Function Signature

```python
async def create_image(
    keywords: list,
    company_name: str = "Aura",
    product_name: str = "Cold Brew",
    tagline_prompt: str = "Elevate Your Moment"
) -> str
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keywords` | `list` | Required | List of descriptive keywords for the image |
| `company_name` | `str` | `"Aura"` | Brand/company name to display on the product |
| `product_name` | `str` | `"Cold Brew"` | Product name to display |
| `tagline_prompt` | `str` | `"Elevate Your Moment"` | Tagline to include in the image |

## How It Works

The function constructs a detailed prompt for Freepik's AI image generation API:

```
Professional high-resolution close-up product photography of:
{company_name} {product_name}, featuring a sleek can with the logo and 
product name clearly visible in bold letters. The can sits at the center, 
surrounded by simple, stylized swirls of iced coffee shaped like a soft 
tornado, with droplets or small lines suggesting motion. The scene should 
feel refreshing, modern, and energetic, with smooth clean shapes, 
vector-style gradients, and soft shadows. Place the tagline 
{tagline_prompt} in a clear, modern sans-serif font below or above the can.

Visual style: flat illustration, simple composition, vector aesthetic, 
minimal details, strong brand visibility, summer mood, refreshing energy, 
balanced negative space.
```

## Usage Examples

### Example 1: Default Aura Cold Brew

```python
image_url = await create_image(
    keywords=["cold brew", "ice", "refreshing"]
)
# Uses defaults: Aura Cold Brew, "Elevate Your Moment"
```

### Example 2: Aura Iced Brew (Summer Product)

```python
image_url = await create_image(
    keywords=["iced coffee", "beach", "summer vibes"],
    company_name="Aura",
    product_name="Iced Brew",
    tagline_prompt="Cool Down Your Summer"
)
```

### Example 3: Aura Hot Brew (Winter Product)

```python
image_url = await create_image(
    keywords=["hot coffee", "cozy", "winter warmth"],
    company_name="Aura",
    product_name="Hot Brew",
    tagline_prompt="Warm Up Your Winter"
)
```

### Example 4: Custom Brand

```python
image_url = await create_image(
    keywords=["energy drink", "sports", "active lifestyle"],
    company_name="PowerUp",
    product_name="Energy Max",
    tagline_prompt="Unleash Your Potential"
)
```

## Integration with Multi-Demographic Campaigns

In the `/generate_multi_demographic_campaign` endpoint, the function is called with dynamic parameters based on:

1. **Company Profile**: Brand name and tagline from `config/company_profile.py`
2. **Recommended Product**: Product name based on weather/season analysis
3. **LLM-Generated Keywords**: Image keywords from the campaign generation

```python
# From main.py, line 459-464
image_url = await create_image(
    keywords=image_keywords,
    company_name=company_profile['brand_name'].split()[0],  # "Aura"
    product_name=recommended_product['name'].replace('Aura ', ''),  # "Cold Brew", "Iced Brew", etc.
    tagline_prompt=company_profile['tagline']  # "Elevate Your Moment"
)
```

## Image Styling

The function uses the following Freepik API styling parameters:

```python
"styling": {
    "style": "photo",           # Photorealistic style
    "effects": { 
        "color": "vibrant",     # Vibrant colors for commercial appeal
        "lightning": "studio",  # Professional studio lighting
        "framing": "close-up"   # Close-up product focus
    }
}
```

## Visual Output Characteristics

Generated images will feature:

✅ **Product-Focused Composition**
- Product can prominently centered
- Clear brand logo visibility
- Product name in bold, readable text

✅ **Dynamic Visual Elements**
- Stylized swirls or motion effects
- Droplets or splash elements
- Refreshing, energetic vibe

✅ **Professional Styling**
- Flat illustration aesthetic
- Vector-style gradients
- Clean, minimalist design
- Balanced negative space

✅ **Tagline Integration**
- Modern sans-serif typography
- Positioned above or below product
- Clear and readable

## Customization for Different Scenarios

### USA Winter Campaign
```python
image_url = await create_image(
    keywords=["hot coffee", "snow", "cozy fireplace", "winter warmth"],
    company_name="Aura",
    product_name="Hot Brew",
    tagline_prompt="Warm Up Your Winter Moment"
)
```
**Result**: Warm tones, cozy atmosphere, hot beverage steam

### Australia Summer Campaign
```python
image_url = await create_image(
    keywords=["iced coffee", "beach", "sunshine", "cooling refreshment"],
    company_name="Aura",
    product_name="Iced Brew",
    tagline_prompt="The Coolest Way to Celebrate"
)
```
**Result**: Bright colors, beach vibes, iced beverage with condensation

### UK Autumn Campaign
```python
image_url = await create_image(
    keywords=["cold brew", "autumn leaves", "urban cafe", "premium quality"],
    company_name="Aura",
    product_name="Cold Brew",
    tagline_prompt="Your Autumn Ritual"
)
```
**Result**: Warm autumn tones, sophisticated urban setting

## API Configuration

The function uses these API settings:

```python
API_URL = "https://api.freepik.com/v1/ai/gemini-2-5-flash-image-preview"
POLLING_INTERVAL_SECONDS = 3  # Check status every 3 seconds
TIMEOUT_SECONDS = 300  # 5-minute maximum wait time
```

## Error Handling

The function includes robust error handling:

```python
# Missing API key
if not FREEPIK_API_KEY:
    raise Exception("ERROR: FREEPIK_API_KEY not found in environment variables.")

# Empty keywords
if not keywords:
    raise ValueError("Keywords list cannot be empty.")

# Timeout
if time_elapsed > TIMEOUT_SECONDS:
    raise Exception("Timeout reached while waiting for image generation.")
```

## Testing

Test the function standalone:

```bash
python utils/freepik_utils.py
```

This runs the built-in test with example keywords:
```python
example_keywords = ["Starbucks Cold Brew can", "splashes of coffee", "ice cubes"]
```

## Best Practices

1. **Keywords**: Provide 3-7 descriptive keywords
2. **Product Name**: Keep it concise (1-3 words)
3. **Tagline**: Short and memorable (3-6 words)
4. **Company Name**: Single word or short phrase works best

## Limitations

- Maximum generation time: 5 minutes
- Requires valid Freepik API key
- Image aspect ratio: Square (1:1)
- Number of images: 1 per request

## Future Enhancements

Potential improvements:
- [ ] Support for multiple aspect ratios
- [ ] Batch image generation
- [ ] Style variations (photo vs illustration)
- [ ] Color scheme customization
- [ ] Background options (transparent, gradient, solid)
- [ ] Logo upload integration
