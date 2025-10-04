"""Simple end-to-end demo for the Autonomous Brand Agent."""

import argparse
import asyncio
from typing import Iterable, List, Sequence

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


def _print_section(title: str) -> None:
    underline = "-" * len(title)
    print(f"\n{title}\n{underline}")


def _truncate(value: str, limit: int = 70) -> str:
    if value is None:
        return ""
    value = value.strip()
    return value if len(value) <= limit else value[: limit - 3] + "..."


def _print_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> List[List[str]]:
    widths: List[int] = [len(h) for h in headers]
    formatted_rows: List[List[str]] = []
    for row in rows:
        formatted = [_truncate(str(cell) if cell is not None else "") for cell in row]
        formatted_rows.append(formatted)
        widths[:] = [max(w, len(formatted[i])) for i, w in enumerate(widths)]

    divider = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_line = "|" + "|".join(f" {headers[i].ljust(widths[i])} " for i in range(len(headers))) + "|"
    print(divider)
    print(header_line)
    print(divider)
    for row in formatted_rows:
        line = "|" + "|".join(f" {row[i].ljust(widths[i])} " for i in range(len(headers))) + "|"
        print(line)
    print(divider)
    return formatted_rows


async def _run_opportunity_demo(city: str, brand_rules: str) -> main.CampaignResponse:
    _print_section("Opportunity Campaign")
    request = main.CampaignRequest(brand_rules=brand_rules, city=city)
    response = await main.generate_campaign(request)
    print(f"Location          : {city}")
    print(f"Opportunity       : {_truncate(response.discovered_opportunity, 120)}")
    print(f"Headline          : {_truncate(response.headline)}")
    print(f"Primary Message   : {_truncate(response.body)}")
    if response.tagline:
        print(f"Tagline           : {_truncate(response.tagline)}")
    print(f"Creative Reference: {_truncate(response.image_url)}")
    return response


async def _run_multi_demo(city: str, country_code: str) -> main.MultiDemographicResponse:
    _print_section("Multi-Demographic Campaigns")
    request = main.MultiDemographicRequest(city=city, country_code=country_code)
    response = await main.generate_multi_demographic_campaign(request)
    print(f"Location          : {response.city}, {response.country}")
    print(f"Season            : {response.season}")
    print(f"Weather Context   : {_truncate(response.weather_context)}")
    print(f"Strategic Action  : {_truncate(response.strategic_action)}")
    print(f"Recommended Offer : {response.recommended_product}")
    print(f"Event Reference   : {_truncate(response.discovered_event, 120)}")
    return response


def _run_competitor_demo(competitor_ad: str) -> main.AdGenerationResponse:
    _print_section("Competitive Counter-Campaign")
    request = main.AdRequest(competitor_ad_text=competitor_ad)
    response = main.generate_ad(request)
    print(f"Status            : {response.status} (confidence {response.confidence_score}%)")
    print(f"Tagline           : {_truncate(response.generated_tagline)}")
    print(f"Primary Message   : {_truncate(response.ad_copy)}")
    if response.image_prompt:
        print(f"Creative Prompt   : {_truncate(response.image_prompt)}")
    return response


async def _run_demo(args: argparse.Namespace) -> None:
    brand_rules = args.brand_rules or main.BRAND_RULES_TEXT

    try:
        if main.tfy_client is None:
            print("⚠️ Missing TRUEFOUNDRY_API_KEY: skipping campaign generation demos.")
            opportunity = None
            multi = None
        else:
            opportunity = await _run_opportunity_demo(args.city, brand_rules)
            multi = await _run_multi_demo(args.city, args.country)
        competitor = _run_competitor_demo(args.competitor_ad)

        rows = []
        headers = ("Segment", "Audience", "Headline", "Tagline", "Creative")

        if opportunity:
            rows.append(
                (
                    "Opportunity",
                    args.city,
                    opportunity.headline,
                    opportunity.tagline or "",
                    opportunity.image_url or "",
                )
            )

        if multi:
            for campaign in multi.campaigns:
                rows.append(
                    (
                        campaign.demographic_segment,
                        campaign.age_range,
                        campaign.headline,
                        campaign.tagline or "",
                        campaign.image_url or "",
                    )
                )

        rows.append(
            (
                "Competitor Response",
                "—",
                competitor.ad_copy,
                competitor.generated_tagline,
                competitor.image_prompt or "(text prompt)",
            )
        )

        _print_section("Creative Summary")
        table_rows = _print_table(headers[:-1], [row[:-1] for row in rows])

        print("\nCreative References")
        print("-------------------")
        for original_row, formatted_row in zip(rows, table_rows):
            creative = original_row[-1]
            label = formatted_row[0]
            if creative:
                print(f"{label}: {creative}")
    except HTTPException as exc:
        print(f"Demo failed with status {exc.status_code}: {exc.detail}")


def run() -> None:
    args = _parse_args()
    asyncio.run(_run_demo(args))


if __name__ == "__main__":
    run()
