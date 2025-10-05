"""
Test script for the Multi-Demographic Campaign Generation endpoint.

This script demonstrates the enhanced autonomous marketing agent's capabilities
by generating location-aware, multi-demographic campaigns for different cities.
"""

import asyncio
import httpx
import json
from typing import Dict, Any


async def test_campaign_generation(city: str, country_code: str) -> Dict[str, Any]:
    """
    Test the multi-demographic campaign generation endpoint.
    
    Args:
        city: City name
        country_code: 2-letter country code
    
    Returns:
        API response dictionary
    """
    url = "http://localhost:8000/generate_multi_demographic_campaign"
    payload = {
        "city": city,
        "country_code": country_code
    }
    
    print(f"\n{'='*80}")
    print(f"Testing Campaign Generation for {city}, {country_code}")
    print(f"{'='*80}\n")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Print summary
            print(f"✅ SUCCESS: Generated {data['total_campaigns']} campaigns\n")
            print(f"📍 Location: {data['city']}, {data['country']}")
            print(f"🌡️  Temperature: {data['temperature']}")
            print(f"🌤️  Weather: {data['weather_context']}")
            print(f"📅 Season: {data['season']}")
            print(f"🎯 Recommended Product: {data['recommended_product']}")
            print(f"⚡ Strategic Action: {data['strategic_action']}")
            print(f"\n📰 Discovered Event:")
            print(f"   {data['discovered_event'][:150]}...")
            
            print(f"\n🎨 Generated Campaigns:")
            for i, campaign in enumerate(data['campaigns'], 1):
                print(f"\n  [{i}] {campaign['demographic_segment']} ({campaign['age_range']})")
                print(f"      Headline: {campaign['headline']}")
                print(f"      Body: {campaign['body'][:100]}...")
                if campaign.get('tagline'):
                    print(f"      Tagline: {campaign['tagline']}")
                if campaign.get('headline_mandarin'):
                    print(f"      Headline (ZH): {campaign['headline_mandarin']}")
                if campaign.get('body_mandarin'):
                    print(f"      Body (ZH): {campaign['body_mandarin'][:100]}...")
                if campaign.get('tagline_mandarin'):
                    print(f"      Tagline (ZH): {campaign['tagline_mandarin']}")
                print(f"      Image: {campaign['image_url'][:60]}...")
                print(f"      Notes: {campaign['strategic_notes'][:80]}...")
            
            return data
            
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


async def run_all_tests():
    """Run tests for multiple locations to demonstrate the system."""
    
    print("\n" + "="*80)
    print("🤖 AUTONOMOUS MULTI-DEMOGRAPHIC CAMPAIGN GENERATION - TEST SUITE")
    print("="*80)
    
    test_cases = [
        ("New York", "US"),
        ("Sydney", "AU"),
        ("London", "GB"),
    ]
    
    results = []
    
    for city, country in test_cases:
        try:
            result = await test_campaign_generation(city, country)
            results.append({
                "city": city,
                "country": country,
                "success": True,
                "campaigns": result['total_campaigns']
            })
            
            # Wait a bit between requests to avoid rate limits
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"\n⚠️  Test failed for {city}, {country}: {e}")
            results.append({
                "city": city,
                "country": country,
                "success": False,
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    
    print("\nDetails:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(f"  {status} {result['city']}, {result['country']}: {result['campaigns']} campaigns generated")
        else:
            print(f"  {status} {result['city']}, {result['country']}: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*80 + "\n")


async def test_single_location():
    """Quick test for a single location."""
    print("\n🚀 Quick Test: Single Location\n")
    
    # Test Sydney, Australia (should show summer campaign in December)
    await test_campaign_generation("Sydney", "AU")


async def compare_hemispheres():
    """
    Demonstrate hemisphere awareness by comparing winter campaigns
    in Northern vs Southern hemisphere.
    """
    print("\n" + "="*80)
    print("🌍 HEMISPHERE COMPARISON TEST")
    print("="*80)
    print("\nThis test demonstrates how the agent adapts to reversed seasons")
    print("in the Southern Hemisphere.\n")
    
    # Northern Hemisphere (Winter = Dec-Feb)
    print("\n--- NORTHERN HEMISPHERE (USA) ---")
    us_result = await test_campaign_generation("New York", "US")
    
    await asyncio.sleep(2)
    
    # Southern Hemisphere (Winter = Jun-Aug, Summer = Dec-Feb)
    print("\n--- SOUTHERN HEMISPHERE (Australia) ---")
    au_result = await test_campaign_generation("Sydney", "AU")
    
    # Compare
    print("\n" + "="*80)
    print("🔍 COMPARISON ANALYSIS")
    print("="*80)
    
    print(f"\nNew York (US):")
    print(f"  Season: {us_result['season']}")
    print(f"  Temperature: {us_result['temperature']}")
    print(f"  Recommended Product: {us_result['recommended_product']}")
    print(f"  Strategic Action: {us_result['strategic_action']}")
    
    print(f"\nSydney (AU):")
    print(f"  Season: {au_result['season']}")
    print(f"  Temperature: {au_result['temperature']}")
    print(f"  Recommended Product: {au_result['recommended_product']}")
    print(f"  Strategic Action: {au_result['strategic_action']}")
    
    print("\n💡 Key Insight:")
    if us_result['season'] != au_result['season']:
        print("   ✓ Agent correctly detected reversed seasons!")
        print(f"   ✓ US is in {us_result['season']}, AU is in {au_result['season']}")
        print(f"   ✓ Recommended different products: {us_result['recommended_product']} vs {au_result['recommended_product']}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "single":
            asyncio.run(test_single_location())
        elif mode == "compare":
            asyncio.run(compare_hemispheres())
        elif mode == "all":
            asyncio.run(run_all_tests())
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python test_multi_demographic.py [single|compare|all]")
    else:
        # Default: run hemisphere comparison (most impressive demo)
        print("Running hemisphere comparison demo...")
        print("(Use 'python test_multi_demographic.py all' to test all locations)")
        asyncio.run(compare_hemispheres())
