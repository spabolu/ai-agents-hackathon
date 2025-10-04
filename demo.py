"""Simple end-to-end demo for the Autonomous Brand Agent."""

import argparse
import asyncio

from fastapi import HTTPException

import main


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an autonomous marketing demo without starting the FastAPI server."
    )
    parser.add_argument(
        "--city",
        default="Sydney",
        help="City to spotlight in the demo (default: Sydney).",
    )
    parser.add_argument(
        "--country",
        default="AU",
        help="Two-letter country code for the city (default: AU).",
    )
    parser.add_argument(
        "--competitor-ad",
        default=(
            "Fuel your hustle with rivals' iced blend. Limited time offer, all buzz,"
            " no crash."
        ),
        help="Sample competitor copy to trigger a response ad.",
    )
    parser.add_argument(
        "--brand-rules",
        default=None,
        help="Override the default brand rules used in the opportunity demo.",
    )
    return parser.parse_args()


async def _run_opportunity_demo(city: str, brand_rules: str) -> None:
    print("\n=== Opportunity Campaign Demo ===")
    request = main.CampaignRequest(brand_rules=brand_rules, city=city)
    response = await main.generate_campaign(request)
    print(f"Discovered Opportunity: {response.discovered_opportunity}")
    print(f"Headline: {response.headline}")
    print(f"Body: {response.body}")
    if response.tagline:
        print(f"Tagline: {response.tagline}")
    print(f"Creative URL: {response.image_url}\n")


async def _run_multi_demo(city: str, country_code: str) -> None:
    print("=== Multi-Demographic Campaign Demo ===")
    request = main.MultiDemographicRequest(city=city, country_code=country_code)
    response = await main.generate_multi_demographic_campaign(request)
    print(
        f"Location: {response.city}, {response.country} | "
        f"Season: {response.season} | Product: {response.recommended_product}"
    )
    print(f"Weather Context: {response.weather_context}")
    print(f"Strategic Action: {response.strategic_action}")
    event_preview = (response.discovered_event or "")[:140]
    ellipsis = "..." if response.discovered_event else ""
    print(f"Discovered Event: {event_preview}{ellipsis}")

    for idx, campaign in enumerate(response.campaigns, start=1):
        print(f"\n[{idx}] {campaign.demographic_segment} ({campaign.age_range})")
        print(f"Headline: {campaign.headline}")
        print(f"Body: {campaign.body}")
        if campaign.tagline:
            print(f"Tagline: {campaign.tagline}")
        print(f"Strategic Notes: {campaign.strategic_notes}")
        print(f"Creative URL: {campaign.image_url}")
    print()


def _run_competitor_demo(competitor_ad: str) -> None:
    print("=== Competitor Response Demo ===")
    request = main.AdRequest(competitor_ad_text=competitor_ad)
    response = main.generate_ad(request)
    print(f"Status: {response.status} | Confidence: {response.confidence_score}")
    print(f"Tagline: {response.generated_tagline}")
    print(f"Ad Copy: {response.ad_copy}")
    if response.image_prompt:
        print(f"Image Prompt: {response.image_prompt}")
    print()


async def _run_demo(args: argparse.Namespace) -> None:
    brand_rules = args.brand_rules or main.BRAND_RULES_TEXT

    try:
        if main.tfy_client is None:
            print("⚠️ Missing TRUEFOUNDRY_API_KEY: skipping campaign generation demos.")
        else:
            await _run_opportunity_demo(args.city, brand_rules)
            await _run_multi_demo(args.city, args.country)
        _run_competitor_demo(args.competitor_ad)
    except HTTPException as exc:
        print(f"Demo failed with status {exc.status_code}: {exc.detail}")


def run() -> None:
    args = _parse_args()
    asyncio.run(_run_demo(args))


if __name__ == "__main__":
    run()
