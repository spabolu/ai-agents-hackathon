"""Simple end-to-end demo for the Autonomous Brand Agent."""

import argparse
import asyncio
import os
import time
from datetime import datetime
from typing import Iterable, List, Sequence

from fastapi import HTTPException

import main

# Optional analytics sink; demo still runs without the package.
try:
    import clickhouse_connect  # type: ignore
except ImportError:  # pragma: no cover - optional dependency for demos
    clickhouse_connect = None


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


def _persist_clickhouse(rows: List[dict]) -> None:
    """Persist the generated creatives to ClickHouse for quick telemetry review."""
    if not rows:
        return
    if clickhouse_connect is None:
        print("⚠️ ClickHouse client not installed; skipping persistence.")
        return

    raw_host = os.getenv("CLICKHOUSE_HOST") or os.getenv("CLICKHOUSE_ENDPOINT") or ""
    if raw_host.startswith("https://"):
        raw_host = raw_host[len("https://") :]
    host_part = raw_host.split("/", 1)[0]

    host = host_part.split(":", 1)[0] if host_part else ""
    explicit_port = host_part.split(":", 1)[1] if ":" in host_part else None

    port = int(explicit_port or os.getenv("CLICKHOUSE_PORT", "8443"))
    user = os.getenv("CLICKHOUSE_USER") or os.getenv("CLICKHOUSE_ID")
    password = os.getenv("CLICKHOUSE_PASSWORD") or os.getenv("CLICKHOUSE_SECRET")
    database = os.getenv("CLICKHOUSE_DATABASE", "default")
    table = os.getenv("CLICKHOUSE_TABLE", "demo_ads")

    if not host or not user:
        # print("⚠️ ClickHouse configuration missing (set CLICKHOUSE_HOST/ID/SECRET); skipping persistence.")
        return

    try:
        client = clickhouse_connect.get_client(
            host=host,
            port=port,
            username=user,
            password=password,
            database=database,
            secure=True,
        )
    except Exception as exc:  # pragma: no cover - network failures
        print(f"⚠️ Failed to connect to ClickHouse: {exc}")
        return

    create_stmt = f"""
CREATE TABLE IF NOT EXISTS {table} (
    run_id String,
    recorded_at DateTime,
    segment String,
    audience String,
    headline_en String,
    headline_zh String,
    tagline_en String,
    tagline_zh String,
    creative String,
    duration_ms Float64
)
ENGINE MergeTree
ORDER BY (run_id, segment)
"""

    try:
        client.command(create_stmt)
    except Exception as exc:
        print(f"⚠️ Failed to ensure ClickHouse table: {exc}")
        return

    recorded_at = datetime.utcnow()
    run_id = recorded_at.isoformat()

    payload = [
        [
            run_id,
            recorded_at,
            row.get("segment", ""),
            row.get("audience", ""),
            row.get("headline", ""),
            row.get("headline_zh", ""),
            row.get("tagline", ""),
            row.get("tagline_zh", ""),
            row.get("creative", ""),
            float(row.get("duration_ms") or 0.0),
        ]
        for row in rows
    ]

    try:
        client.insert(
            table,
            payload,
            column_names=[
                "run_id",
                "recorded_at",
                "segment",
                "audience",
                "headline_en",
                "headline_zh",
                "tagline_en",
                "tagline_zh",
                "creative",
                "duration_ms",
            ],
        )
        print(f"✓ Stored {len(payload)} creatives in ClickHouse ({table})")
    except Exception as exc:
        print(f"⚠️ Failed to write to ClickHouse: {exc}")


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
    # Surface the Mandarin variants generated through DeepL.
    if response.headline_mandarin:
        print(f"Headline (ZH)     : {_truncate(response.headline_mandarin)}")
    if response.body_mandarin:
        print(f"Primary (ZH)      : {_truncate(response.body_mandarin)}")
    if response.tagline_mandarin:
        print(f"Tagline (ZH)      : {_truncate(response.tagline_mandarin)}")
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
    # Highlight each demographic slice with bilingual copy.
    for idx, campaign in enumerate(response.campaigns, start=1):
        print(f"\n  Segment {idx}: {campaign.demographic_segment} ({campaign.age_range})")
        print(f"    Headline      : {_truncate(campaign.headline)}")
        if campaign.headline_mandarin:
            print(f"    Headline (ZH) : {_truncate(campaign.headline_mandarin)}")
        if campaign.tagline:
            print(f"    Tagline       : {_truncate(campaign.tagline)}")
        if campaign.tagline_mandarin:
            print(f"    Tagline (ZH)  : {_truncate(campaign.tagline_mandarin)}")
        print(f"    Creative      : {_truncate(campaign.image_url)}")
    return response


async def _run_competitor_demo(competitor_ad: str) -> main.AdGenerationResponse:
    _print_section("Competitive Counter-Campaign")
    request = main.AdRequest(competitor_ad_text=competitor_ad)
    response = await main.generate_ad(request)
    print(f"Status            : {response.status} (confidence {response.confidence_score}%)")
    print(f"Tagline           : {_truncate(response.generated_tagline)}")
    print(f"Primary Message   : {_truncate(response.ad_copy)}")
    if response.image_prompt:
        print(f"Creative Prompt   : {_truncate(response.image_prompt)}")
    # Capture the Mandarin output from DeepL for parity with the English copy.
    if response.ad_copy_mandarin:
        print(f"Primary (ZH)      : {_truncate(response.ad_copy_mandarin)}")
    if response.tagline_mandarin:
        print(f"Tagline (ZH)      : {_truncate(response.tagline_mandarin)}")
    return response


async def _run_demo(args: argparse.Namespace) -> None:
    brand_rules = args.brand_rules or main.BRAND_RULES_TEXT

    try:
        demo_start = time.time()
        if main.tfy_client is None:
            print("⚠️ Missing TRUEFOUNDRY_API_KEY: skipping campaign generation demos.")
            opportunity = None
            multi = None
        else:
            opportunity = await _run_opportunity_demo(args.city, brand_rules)

            multi = await _run_multi_demo(args.city, args.country)

        competitor = await _run_competitor_demo(args.competitor_ad)

        # Collect a normalized view of every creative we surfaced.
        rows = []

        if opportunity:
            rows.append(
                {
                    "segment": "Opportunity",
                    "audience": args.city,
                    "headline": opportunity.headline,
                    "headline_zh": opportunity.headline_mandarin or "",
                    "tagline": opportunity.tagline or "",
                    "tagline_zh": opportunity.tagline_mandarin or "",
                    "body_zh": opportunity.body_mandarin or "",
                    "creative": opportunity.image_url or "",
                    "duration_ms": None,
                }
            )

        if multi:
            for campaign in multi.campaigns:
                rows.append(
                    {
                        "segment": campaign.demographic_segment,
                        "audience": campaign.age_range,
                        "headline": campaign.headline,
                        "headline_zh": campaign.headline_mandarin or "",
                        "tagline": campaign.tagline or "",
                        "tagline_zh": campaign.tagline_mandarin or "",
                        "body_zh": campaign.body_mandarin or "",
                        "creative": campaign.image_url or "",
                        "duration_ms": None,
                    }
                )

        rows.append(
            {
                "segment": "Competitor Response",
                "audience": "—",
                "headline": competitor.ad_copy,
                "headline_zh": competitor.ad_copy_mandarin or "",
                "tagline": competitor.generated_tagline or "",
                "tagline_zh": competitor.tagline_mandarin or "",
                "body_zh": competitor.ad_copy_mandarin or "",
                "creative": competitor.image_prompt or "(text prompt)",
                "duration_ms": getattr(competitor, "exec_duration_ms", None),
            }
        )

        _print_section("Creative Summary")
        # Summarize English vs Mandarin headlines/taglines side-by-side.
        headers = (
            "Segment",
            "Audience",
            "Headline",
            "Headline (ZH)",
            "Tagline",
            "Tagline (ZH)",
        )
        _print_table(
            headers,
            [
                (
                    row["segment"],
                    row["audience"],
                    row["headline"],
                    row["headline_zh"],
                    row["tagline"],
                    row["tagline_zh"],
                )
                for row in rows
            ],
        )

        print("\nCreative References")
        print("-------------------")
        for row in rows:
            creative = row.get("creative")
            if creative:
                print(f"{row['segment']}: {creative}")

        if any(row.get("body_zh") for row in rows):
            print("\nMandarin Body Copy")
            print("-------------------")
            for row in rows:
                body_zh = row.get("body_zh")
                if body_zh:
                    print(f"{row['segment']}: {body_zh}")

        total_ms = (time.time() - demo_start) * 1000

        rows_for_persistence = rows + [
            {
                "segment": "Demo Total",
                "audience": "—",
                "headline": "",
                "headline_zh": "",
                "tagline": "",
                "tagline_zh": "",
                "body_zh": "",
                "creative": "",
                "duration_ms": total_ms,
            }
        ]

        # Drop the run into ClickHouse so stakeholders can review after the demo.
        _persist_clickhouse(rows_for_persistence)

        print(f"\nTotal Demo Duration: {total_ms:.1f} ms")
    except HTTPException as exc:
        print(f"Demo failed with status {exc.status_code}: {exc.detail}")


def run() -> None:
    args = _parse_args()
    asyncio.run(_run_demo(args))


if __name__ == "__main__":
    run()
