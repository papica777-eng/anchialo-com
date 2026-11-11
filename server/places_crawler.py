"""Melbourne B2B Lead Engine powered by Google Places API (New) with strict FieldMask & quota guard."""

from datetime import date
import logging
import os
import re
import time
from typing import Any

import httpx

from db import get_conn, init_db

logger = logging.getLogger("anchialo.places")

PLACES_FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.websiteUri,"
    "places.nationalPhoneNumber"
)

MELBOURNE_VERTICAL_QUERIES: list[tuple[str, str, int]] = [
    ("combat_gym", "MMA BJJ Boxing Muay Thai gym Melbourne VIC", 95),
    ("myotherapy", "Myotherapy clinic Melbourne VIC", 92),
    ("remedial_massage", "Remedial massage clinic Melbourne VIC", 88),
    ("pilates", "Reformer Pilates studio Richmond South Yarra Prahran VIC", 84),
    ("float_sauna", "Float centre contrast therapy sauna Melbourne VIC", 82),
    ("greek_hub", "Greek delicatessen pharmacy wellness Oakleigh Northcote VIC", 80),
]

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IGNORED_EMAIL_DOMAINS = ("sentry.io", "wixpress.com", "example.com", "schema.org", "w3.org")


def extract_suburb_from_address(address: str) -> str:
    """Extract suburb label from an Australian formatted address string."""
    parts = [p.strip() for p in (address or "").split(",")]
    if len(parts) >= 2:
        return parts[-2]
    return "Melbourne VIC"


def check_and_increment_places_quota(conn: Any, max_daily: int) -> bool:
    """Enforce daily Google Places API cap to stay cleanly within free monthly SKU allowance."""
    today_key = date.today().isoformat()
    row = conn.execute(
        "SELECT count FROM api_usage_counters WHERE usage_date = ? AND metric = 'google_places'",
        (today_key,),
    ).fetchone()
    current = int(row["count"]) if row else 0
    if current >= max_daily:
        return False
    conn.execute(
        """
        INSERT INTO api_usage_counters (usage_date, metric, count) VALUES (?, 'google_places', 1)
        ON CONFLICT(usage_date, metric) DO UPDATE SET count = count + 1
        """,
        (today_key,),
    )
    return True


async def discover_public_contact_email(website_url: str) -> str:
    """Fetch public business homepage/contact page cleanly to extract a published business email."""
    url = (website_url or "").strip()
    if not url.startswith(("http://", "https://")):
        return ""
    candidates = [url.rstrip("/"), f"{url.rstrip('/')}/contact"]
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            for target in candidates:
                try:
                    res = await client.get(target, headers={"User-Agent": "AnchialoPartnerDiscovery/1.0"})
                    if res.status_code != 200:
                        continue
                    for match in EMAIL_REGEX.findall(res.text):
                        lower = match.lower()
                        if any(bad in lower for bad in IGNORED_EMAIL_DOMAINS):
                            continue
                        if lower.endswith((".png", ".jpg", ".jpeg", ".webp", ".svg")):
                            continue
                        return lower
                except httpx.HTTPError:
                    continue
    except Exception as exc:
        logger.debug("Email enrichment failed for %s: %s", url, exc)
    return ""


async def crawl_melbourne_businesses(
    queries: list[tuple[str, str, int]] | None = None,
    enrich_emails: bool = True,
) -> dict[str, int]:
    """Query Google Places API (New) and store scored Greater Melbourne B2B prospects."""
    init_db()
    api_key = (os.environ.get("GOOGLE_PLACES_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY environment variable is required to crawl Places API.")

    max_daily = int(os.environ.get("MAX_DAILY_PLACES_CALLS") or "80")
    inserted = 0
    enriched = 0
    now = int(time.time())

    async with httpx.AsyncClient(timeout=15.0) as client:
        for category, text_query, base_score in (queries or MELBOURNE_VERTICAL_QUERIES):
            with get_conn() as conn:
                if not check_and_increment_places_quota(conn, max_daily):
                    logger.warning("Daily Google Places quota cap reached (%s). Stopping cleanly.", max_daily)
                    break

            resp = await client.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers={
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": PLACES_FIELD_MASK,
                    "Content-Type": "application/json",
                },
                json={"textQuery": text_query, "regionCode": "AU", "maxResultCount": 20},
            )
            resp.raise_for_status()
            places = resp.json().get("places") or []

            for place in places:
                place_id = str(place.get("id") or "").strip()
                name = str((place.get("displayName") or {}).get("text") or "").strip()
                address = str(place.get("formattedAddress") or "").strip()
                website = str(place.get("websiteUri") or "").strip()
                phone = str(place.get("nationalPhoneNumber") or "").strip()
                if not place_id or not name:
                    continue

                email = ""
                if enrich_emails and website:
                    email = await discover_public_contact_email(website)
                    if email:
                        enriched += 1

                suburb = extract_suburb_from_address(address)
                score = base_score + (5 if email else 0) + (3 if website else 0)
                with get_conn() as conn:
                    cur = conn.execute(
                        """
                        INSERT OR IGNORE INTO b2b_leads (
                            place_id, name, category, suburb, address, phone, website, email, score, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)
                        """,
                        (place_id, name, category, suburb, address, phone, website, email, score, now),
                    )
                    if cur.rowcount > 0:
                        inserted += 1

    return {"inserted": inserted, "emails_enriched": enriched}

