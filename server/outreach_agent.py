"""Spam Act 2003 compliant Melbourne B2B Outreach Agent (Step 1 + Day-3 & Day-7 follow-ups)."""

from datetime import date
import html
import logging
import os
import time
from typing import Any

import httpx

from db import get_conn, init_db
from notifications import is_unsubscribed, normalize_email, send_resend_email, send_telegram_alert

logger = logging.getLogger("anchialo.outreach")


def build_b2b_pitch(lead: dict[str, Any], step: int = 1) -> tuple[str, str, str]:
    """Build TGA-compliant, zero-hype B2B offer offering QR zero-risk stand or wholesale box."""
    biz_name = str(lead.get("name") or "Team").strip()
    category = str(lead.get("category") or "studio").strip()
    suburb = str(lead.get("suburb") or "Melbourne").strip()

    if category == "combat_gym":
        hook = f"fighters and members at {biz_name} training hard in {suburb}"
    elif category in ("myotherapy", "remedial_massage"):
        hook = f"practitioners and clients at {biz_name} looking for clean post-session body care"
    elif category == "greek_hub":
        hook = f"{biz_name} shoppers in {suburb} who appreciate authentic Greek-heritage Black Sea coastal salts from ancient Anchialos"
    else:
        hook = f"clients at {biz_name} in {suburb} looking for post-session relaxation and skin hydration"

    if step == 1:
        subject = f"Free Melbourne tester for {biz_name} (zero-risk QR stand or clinic wholesale)"
        text_body = (
            f"Hi {biz_name} team,\n\n"
            f"I'm Sotir Kichukov, ONE Championship veteran and founder of CPT MMA here in Melbourne. "
            f"We stock ANCHIALO Dual Magnesium Gels (300g) and 100% Pure Black Sea Brine Oil (300ml) harvested from Lake Pomorie, Bulgaria.\n\n"
            f"I thought this would suit {hook} — unlike watery sprays that run and crust, our glycerine-buffered gel massages cleanly with zero drip.\n\n"
            f"Two simple options if you'd like to test a complimentary 300g Arnica/Lavender jar at reception:\n"
            f"1) Zero-Risk QR Counter Stand: $0 upfront stock. We drop off a tester + small counter QR poster; your members order on anchialo.com and your studio earns 18% commission automatically.\n"
            f"2) Clinic / Gym Wholesale Box: 12-jar carton dispatched locally from Melbourne at practitioner margin.\n\n"
            f"Just reply 'TESTER' with your best drop-off window and I'll swing one past or post it free.\n\n"
            f"Best,\nSotir Kichukov\nANCHIALO Australia | CPT MMA Melbourne\nWhatsApp: +61 423 269 586"
        )
    elif step == 2:
        subject = f"Re: Free Lake Pomorie magnesium tester for {biz_name}"
        text_body = (
            f"Hi {biz_name} team,\n\n"
            f"Quick follow-up in case my note earlier this week got buried between client sessions.\n"
            f"Happy to drop off a complimentary 300g Dual Magnesium Gel tester in {suburb} for your coaches or therapists to try first — zero obligation and zero upfront stock required.\n\n"
            f"Reply 'YES' if you'd like one set aside.\n\n"
            f"Cheers,\nSotir Kichukov (+61 423 269 586)"
        )
    else:
        subject = f"Last note — complimentary tester drop-off in {suburb}?"
        text_body = (
            f"Hi {biz_name} team,\n\n"
            f"I'm dropping off samples around {suburb} later this week. Let me know if you'd like a free 300g Lake Pomorie magnesium gel tester at your desk — otherwise I won't crowd your inbox again.\n\n"
            f"Best regards,\nSotir Kichukov | anchialo.com"
        )

    html_paragraphs = "".join(f"<p>{html.escape(p)}</p>" for p in text_body.split("\n\n"))
    return subject, html_paragraphs, text_body


async def personalize_with_llm_if_enabled(lead: dict[str, Any], step: int) -> tuple[str, str, str]:
    """Optionally polish subject/intro via LLM API; cleanly fall back to deterministic template."""
    subject, body_html, body_text = build_b2b_pitch(lead, step=step)
    api_key = (os.environ.get("LLM_API_KEY") or "").strip()
    base_url = (os.environ.get("LLM_BASE_URL") or "").strip().rstrip("/")
    model = (os.environ.get("LLM_MODEL") or "gemini-2.5-flash").strip()
    if not api_key or not base_url:
        return subject, body_html, body_text

    prompt = (
        f"Polish this short, plain B2B outreach email for '{lead.get('name')}' ({lead.get('category')}, {lead.get('suburb')}). "
        "STRICT RULES: No medical, pain, arthritis, or disease claims — strictly cosmetic body care, post-training massage, skin hydration. "
        "Keep under 140 words and preserve the two options (QR zero-upfront stand vs 12-jar wholesale) and Sotir Kichukov signature.\n\n"
        f"{body_text}"
    )
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "temperature": 0.2,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if resp.status_code == 200:
                polished = (
                    resp.json()["choices"][0]["message"]["content"].strip()
                )
                if polished and len(polished) > 60:
                    polished_html = "".join(f"<p>{html.escape(p)}</p>" for p in polished.split("\n\n"))
                    return subject, polished_html, polished
    except Exception as exc:
        logger.warning("LLM personalization fallback engaged: %s", exc)

    return subject, body_html, body_text


def check_daily_b2b_budget(conn: Any, max_daily: int) -> int:
    """Return remaining outreach email quota for today."""
    today_key = date.today().isoformat()
    row = conn.execute(
        "SELECT count FROM api_usage_counters WHERE usage_date = ? AND metric = 'b2b_emails'",
        (today_key,),
    ).fetchone()
    used = int(row["count"]) if row else 0
    return max(0, max_daily - used)


def increment_daily_b2b_count(conn: Any) -> None:
    """Increment daily B2B send counter."""
    today_key = date.today().isoformat()
    conn.execute(
        """
        INSERT INTO api_usage_counters (usage_date, metric, count) VALUES (?, 'b2b_emails', 1)
        ON CONFLICT(usage_date, metric) DO UPDATE SET count = count + 1
        """,
        (today_key,),
    )


async def run_daily_b2b_outreach(db_path: str | None = None) -> dict[str, int]:
    """Send throttled Step 1, Day-3 (Step 2), and Day-7 (Step 3) B2B emails under Spam Act 2003 rules."""
    init_db(db_path)
    max_daily = int(os.environ.get("MAX_DAILY_B2B_EMAILS") or "25")
    now = int(time.time())
    sent = 0
    skipped = 0

    with get_conn(db_path) as conn:
        remaining = check_daily_b2b_budget(conn, max_daily)
        if remaining <= 0:
            return {"sent": 0, "skipped": 0, "remaining_quota": 0}

        # Prioritize scheduled follow-ups first (D3 after Step 1, D7 after Step 2), excluding unsubscribed emails
        candidates = conn.execute(
            """
            SELECT l.id, l.name, l.category, l.suburb, l.email, l.status,
                   COALESCE(MAX(o.step), 0) AS last_step,
                   COALESCE(MAX(o.sent_at), 0) AS last_sent_at
            FROM b2b_leads l
            LEFT JOIN b2b_outreach_log o ON o.lead_id = l.id
            LEFT JOIN unsubscribes u ON LOWER(TRIM(l.email)) = u.email
            WHERE l.email != '' AND l.category != 'combat_gym' AND l.status IN ('new', 'contacted') AND u.email IS NULL
            GROUP BY l.id
            HAVING (last_step = 0)
                OR (last_step = 1 AND last_sent_at <= ?)
                OR (last_step = 2 AND last_sent_at <= ?)
            ORDER BY last_step DESC, l.score DESC
            LIMIT ?
            """,
            (now - 3 * 86400, now - 4 * 86400, remaining),
        ).fetchall()

        for row in candidates:
            lead = dict(row)
            recipient = normalize_email(lead["email"])
            if not recipient or is_unsubscribed(conn, recipient):
                skipped += 1
                continue

            next_step = int(lead["last_step"]) + 1
            subject, body_html, body_text = await personalize_with_llm_if_enabled(lead, next_step)
            ok, status_msg = await send_resend_email(conn, recipient, subject, body_html, body_text)
            if ok:
                sent += 1
                increment_daily_b2b_count(conn)
                conn.execute(
                    """
                    INSERT INTO b2b_outreach_log (lead_id, step, recipient_email, subject, body, status, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (lead["id"], next_step, recipient, subject, body_text, status_msg, now),
                )
                new_status = "sequence_complete" if next_step >= 3 else "contacted"
                conn.execute("UPDATE b2b_leads SET status = ? WHERE id = ?", (new_status, lead["id"]))
            else:
                skipped += 1

    return {"sent": sent, "skipped": skipped, "remaining_quota": max(0, remaining - sent)}


async def notify_warm_leads_digest(db_path: str | None = None) -> list[dict[str, Any]]:
    """Send Sotir a grouped Telegram route list for any B2B leads marked warm/tester_requested."""
    with get_conn(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, name, category, suburb, address, phone, email
            FROM b2b_leads
            WHERE status = 'warm'
            ORDER BY suburb ASC, score DESC
            """
        ).fetchall()
        leads = [dict(r) for r in rows]

    if leads:
        lines = ["MELBOURNE TESTER DROP-OFF ROUTE (WARM B2B):"]
        for i, ld in enumerate(leads, start=1):
            lines.append(f"{i}. {ld['name']} ({ld['suburb']}) — {ld['address']} | {ld['phone'] or ld['email']}")
        await send_telegram_alert("\n".join(lines))
    return leads
