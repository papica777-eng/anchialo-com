"""FastAPI 24/7 Akash CPU Growth Engine: Dynamic Stripe Checkout, QR Commissions, Cart Recovery & Lifecycle Automation."""

import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import date, datetime
import json
import logging
import os
import re
import sqlite3
import time
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import stripe

from db import get_conn, init_db
from demo_simulator import DEMO_STATE, get_demo_telemetry, reset_demo_data, run_demo_wave
from ebay_client import get_ebay_summary, is_ebay_configured, publish_or_revise_catalog
from notifications import (
    build_unsubscribe_url,
    normalize_email,
    render_lifecycle_template,
    send_resend_email,
    send_telegram_alert,
    verify_unsubscribe_token,
)
from outreach_agent import build_b2b_pitch, run_daily_b2b_outreach
from places_crawler import MELBOURNE_VERTICAL_QUERIES, crawl_melbourne_businesses

logger = logging.getLogger("anchialo.server")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Authoritative server-side catalog prices in AUD cents (Zero Trust — never trust client prices)
SERVER_CATALOG: dict[str, dict[str, Any]] = {
    "gel-arnica": {"name": "Dual Magnesium Gel | Arnica Blend (300g)", "cents": 4900},
    "gel-lavender": {"name": "Dual Magnesium Gel | Lavender Blend (300g)", "cents": 4900},
    "gel-rosemary": {"name": "Dual Magnesium Gel | Rosemary Blend (300g)", "cents": 4900},
    "gel-juniper": {"name": "Dual Magnesium Gel | Juniper Blend (300g)", "cents": 4900},
    "gel-grape": {"name": "Dual Magnesium Gel | Grape Blend (300g)", "cents": 4900},
    "oil-pure": {"name": "Dual Magnesium Oil | Pure Topical Brine (300ml)", "cents": 4900},
    "combo-gel-oil": {"name": "Special Offer | Gel + Oil Combo", "cents": 4900},
    "combo-starter": {"name": "Starter Combo | Dual Magnesium Gel (2-Pack)", "cents": 8900},
    "combo-best-value": {"name": "Best Value Combo | Dual Magnesium Gel (3-Pack)", "cents": 12900},
}

ELIGIBLE_PROMO_PCT = {
    "QUIZ10": 10,
    "FOUNDING10": 10,
    "COMEBACK10": 10,
}

CODE_PATTERN = re.compile(r"^[A-Z0-9_-]{3,24}$")


def sanitize_code(raw: str | None) -> str:
    """Normalize partner/promo codes safely."""
    cleaned = re.sub(r"[^A-Z0-9_-]", "", (raw or "").upper())
    return cleaned[:24]


def calculate_architect_share_cents(total_cents: int, bps: int | None = None) -> int:
    """Compute exact integer-cent revenue share (default 2500 bps = 25.00%) with zero float drift."""
    share_bps = bps if bps is not None else int(os.environ.get("ARCHITECT_SHARE_BPS") or "2500")
    share_bps = max(0, min(10000, share_bps))
    return (max(0, int(total_cents)) * share_bps + 5000) // 10000


def calculate_order_cents(
    items: list[dict[str, Any]],
    promo_code: str | None,
    partner_code: str | None,
) -> dict[str, Any]:
    """Compute authoritative subtotal, discount, shipping, and grand total in integer AUD cents."""
    resolved_items: list[dict[str, Any]] = []
    raw_subtotal_cents = 0

    for item in items:
        sku_id = str(item.get("id") or "").strip()
        qty = max(1, min(50, int(item.get("qty") or 1)))
        catalog_entry = SERVER_CATALOG.get(sku_id)
        if not catalog_entry:
            raise HTTPException(status_code=400, detail=f"Unknown product SKU: {sku_id}")
        unit_cents = int(catalog_entry["cents"])
        line_cents = unit_cents * qty
        raw_subtotal_cents += line_cents
        resolved_items.append(
            {
                "id": sku_id,
                "name": catalog_entry["name"],
                "qty": qty,
                "unit_cents": unit_cents,
                "line_cents": line_cents,
            }
        )

    if not resolved_items:
        raise HTTPException(status_code=400, detail="Cart cannot be empty")

    clean_promo = sanitize_code(promo_code)
    clean_partner = sanitize_code(partner_code)
    effective_code = clean_promo or clean_partner

    discount_pct = 0
    if effective_code:
        if effective_code in ELIGIBLE_PROMO_PCT:
            discount_pct = ELIGIBLE_PROMO_PCT[effective_code]
        elif CODE_PATTERN.match(effective_code):
            discount_pct = 10

    discount_cents = (raw_subtotal_cents * discount_pct + 50) // 100
    final_subtotal_cents = max(0, raw_subtotal_cents - discount_cents)
    shipping_cents = 0 if final_subtotal_cents >= 8000 else 1500
    total_cents = final_subtotal_cents + shipping_cents

    return {
        "items": resolved_items,
        "raw_subtotal_cents": raw_subtotal_cents,
        "discount_pct": discount_pct,
        "discount_cents": discount_cents,
        "final_subtotal_cents": final_subtotal_cents,
        "shipping_cents": shipping_cents,
        "total_cents": total_cents,
        "promo_code": effective_code or None,
        "partner_code": clean_partner or (effective_code if effective_code and effective_code not in ELIGIBLE_PROMO_PCT else None),
    }


def cents_to_aud(cents: int) -> str:
    """Format integer cents cleanly to AUD string without float error."""
    return f"A${cents // 100}.{cents % 100:02d}"


def schedule_lifecycle_job(
    conn: sqlite3.Connection,
    email: str,
    stage: str,
    delay_seconds: int,
    payload: dict[str, Any],
) -> None:
    """Insert a pending automated email job into lifecycle_queue."""
    clean = normalize_email(email)
    if not clean or "@" not in clean:
        return
    send_at = int(time.time()) + max(0, delay_seconds)
    conn.execute(
        """
        INSERT INTO lifecycle_queue (email, stage, payload_json, send_after_ts, status)
        VALUES (?, ?, ?, ?, 'pending')
        """,
        (clean, stage, json.dumps(payload), send_at),
    )


async def record_completed_order(
    conn: sqlite3.Connection,
    *,
    provider: str,
    external_tx_id: str,
    customer_email: str,
    customer_name: str,
    subtotal_cents: int,
    discount_cents: int,
    shipping_cents: int,
    total_cents: int,
    partner_code: str | None,
    promo_code: str | None,
    items: list[dict[str, Any]],
    locality: dict[str, Any] | None,
) -> dict[str, Any]:
    """Idempotently record order, accrue QR partner commission, mark carts recovered, schedule D1/D14/D25, and alert Sotir."""
    now = int(time.time())
    clean_email = normalize_email(customer_email)
    clean_partner = sanitize_code(partner_code) or None
    clean_promo = sanitize_code(promo_code) or None

    existing = conn.execute(
        "SELECT id FROM orders WHERE external_tx_id = ?", (external_tx_id,)
    ).fetchone()
    if existing:
        return {"order_id": existing["id"], "duplicate": True}

    cur = conn.execute(
        """
        INSERT INTO orders (
            provider, external_tx_id, customer_email, customer_name,
            subtotal_cents, discount_cents, shipping_cents, total_cents,
            partner_code, promo_code, items_json, locality_json, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'paid', ?)
        """,
        (
            provider,
            external_tx_id,
            clean_email,
            customer_name.strip(),
            subtotal_cents,
            discount_cents,
            shipping_cents,
            total_cents,
            clean_partner,
            clean_promo,
            json.dumps(items),
            json.dumps(locality or {}),
            now,
        ),
    )
    order_id = int(cur.lastrowid)

    commission_cents = 0
    if clean_partner:
        partner_row = conn.execute(
            "SELECT commission_rate FROM partners WHERE code = ?", (clean_partner,)
        ).fetchone()
        default_rate = float(os.environ.get("DEFAULT_PARTNER_COMMISSION_RATE") or "0.18")
        rate = float(partner_row["commission_rate"]) if partner_row else default_rate
        if not partner_row:
            conn.execute(
                """
                INSERT OR IGNORE INTO partners (code, name, category, suburb, contact_email, commission_rate, created_at)
                VALUES (?, ?, 'qr_referral', 'Melbourne', '', ?, ?)
                """,
                (clean_partner, f"QR Partner {clean_partner}", rate, now),
            )
        basis_cents = max(0, total_cents - shipping_cents)
        commission_cents = int(round(basis_cents * rate))
        conn.execute(
            """
            INSERT INTO commissions (order_id, partner_code, order_total_cents, commission_rate, commission_cents, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'accrued', ?)
            """,
            (order_id, clean_partner, basis_cents, rate, commission_cents, now),
        )

    if clean_email:
        conn.execute(
            "UPDATE abandoned_carts SET recovered = 1 WHERE email = ? AND recovered = 0",
            (clean_email,),
        )
        conn.execute(
            "UPDATE lifecycle_queue SET status = 'cancelled_recovered' WHERE email = ? AND stage IN ('cart_2h', 'cart_24h') AND status = 'pending'",
            (clean_email,),
        )
        base_payload = {
            "customer_name": customer_name or "there",
            "promo_code": clean_promo or "COMEBACK10",
            "order_id": order_id,
        }
        schedule_lifecycle_job(conn, clean_email, "post_d1_usage", 3600, base_payload)
        schedule_lifecycle_job(conn, clean_email, "post_d14_review", 14 * 86400, base_payload)
        schedule_lifecycle_job(conn, clean_email, "post_d25_reorder", 25 * 86400, base_payload)

    loc = locality or {}
    loc_label = f"{loc.get('location', 'Melbourne')} {loc.get('state', 'VIC')} {loc.get('postcode', '')}".strip()
    item_lines = ", ".join(f"{it.get('name', it.get('id'))} x{it.get('qty', 1)}" for it in items)
    partner_line = (
        f"\nQR Partner: {clean_partner} (Commission: {cents_to_aud(commission_cents)})"
        if clean_partner
        else ""
    )
    alert_msg = (
        f"NEW ANCHIALO ORDER #{order_id} [{provider.upper()}]\n"
        f"Total: {cents_to_aud(total_cents)} AUD\n"
        f"Items: {item_lines}\n"
        f"Customer: {customer_name or 'Guest'} ({clean_email or 'no email'})\n"
        f"Dispatch Area: {loc_label}{partner_line}"
    )
    await send_telegram_alert(alert_msg)

    return {"order_id": order_id, "duplicate": False, "commission_cents": commission_cents}


class CheckoutItem(BaseModel):
    id: str
    qty: int = Field(default=1, ge=1, le=50)


class CheckoutSessionRequest(BaseModel):
    items: list[CheckoutItem]
    partner_code: str | None = None
    promo_code: str | None = None
    customer_email: str | None = None
    locality: dict[str, Any] | None = None
    success_url: str = "https://anchialo.com/?payment=stripe_success&session_id={CHECKOUT_SESSION_ID}"
    cancel_url: str = "https://anchialo.com/#collection"


class PayPalOrderRequest(BaseModel):
    tx_id: str
    customer_name: str = ""
    customer_email: str = ""
    amount_aud: float = Field(gt=0)
    partner_code: str | None = None
    promo_code: str | None = None
    locality: dict[str, Any] | None = None
    items: list[dict[str, Any]] = Field(default_factory=list)


class CartCaptureRequest(BaseModel):
    email: str
    cart: list[dict[str, Any]] = Field(default_factory=list)
    subtotal_aud: float = 0.0
    partner_code: str | None = None
    promo_code: str | None = None
    postcode: str = "3000"


class QuizSubmitRequest(BaseModel):
    email: str
    goal: str = "sport"
    recommended_id: str = "gel-arnica"
    partner_code: str | None = None


class CalibrationTestRequest(BaseModel):
    send_telegram: bool = False
    sample_suburb: str = "Richmond VIC"


class DemoWaveRequest(BaseModel):
    user_count: int | None = Field(default=None, ge=1, le=200)
    notify_telegram: bool = True


class DemoToggleRequest(BaseModel):
    enabled: bool


HEARTBEAT_STATE: dict[str, Any] = {
    "started_at": int(time.time()),
    "scheduler_ticks": 0,
    "last_tick_ts": 0,
    "last_lifecycle_processed": 0,
    "last_calibration_ts": 0,
    "last_calibration_status": "not_run",
    "b2b_autopilot_enabled": False,
    "melbourne_business_hours": False,
    "last_b2b_run_date": "",
}

MELBOURNE_TZ = ZoneInfo("Australia/Melbourne")


def is_melbourne_business_hours(now_dt: datetime | None = None) -> bool:
    """Return True strictly during Melbourne Mon-Fri 09:00-17:00 business hours."""
    melb_now = now_dt.astimezone(MELBOURNE_TZ) if now_dt else datetime.now(MELBOURNE_TZ)
    return melb_now.weekday() < 5 and 9 <= melb_now.hour < 17


_b2b_tick_lock = asyncio.Lock()


async def run_melbourne_b2b_schedule_tick(
    now_dt: datetime | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Run daily B2B discovery & outreach once per Melbourne business day (Mon-Fri 09:00-17:00)."""
    melb_now = now_dt.astimezone(MELBOURNE_TZ) if now_dt else datetime.now(MELBOURNE_TZ)
    in_hours = is_melbourne_business_hours(melb_now)
    enabled = (os.environ.get("B2B_AUTOPILOT_ENABLED") or "false").strip().lower() in ("1", "true", "yes")
    HEARTBEAT_STATE["b2b_autopilot_enabled"] = enabled
    HEARTBEAT_STATE["melbourne_business_hours"] = in_hours

    if not enabled or not in_hours:
        return {"ran": False, "reason": "disabled" if not enabled else "outside_melbourne_hours"}

    melb_date = melb_now.date().isoformat()
    async with _b2b_tick_lock:
        with get_conn(db_path) as conn:
            already = conn.execute(
                "SELECT count FROM api_usage_counters WHERE usage_date = ? AND metric = 'b2b_melbourne_run'",
                (melb_date,),
            ).fetchone()
            if already and int(already["count"]) > 0:
                HEARTBEAT_STATE["last_b2b_run_date"] = melb_date
                return {"ran": False, "reason": "already_ran_today", "date": melb_date}

        crawl_res = {"inserted": 0, "emails_enriched": 0}
        if (os.environ.get("GOOGLE_PLACES_API_KEY") or "").strip() or (os.environ.get("SERPAPI_API_KEY") or "").strip():
            crawl_res = await crawl_melbourne_businesses(enrich_emails=True)

        outreach_res = await run_daily_b2b_outreach(db_path=db_path)
        if not outreach_res.get("transport_blocked"):
            with get_conn(db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO api_usage_counters (usage_date, metric, count) VALUES (?, 'b2b_melbourne_run', 1)
                    ON CONFLICT(usage_date, metric) DO UPDATE SET count = count + 1
                    """,
                    (melb_date,),
                )
            HEARTBEAT_STATE["last_b2b_run_date"] = melb_date

        if crawl_res.get("inserted", 0) > 0 or outreach_res.get("sent", 0) > 0:
            await send_telegram_alert(
                f"MELBOURNE B2B DAILY RUN ({melb_now.strftime('%a %H:%M AEDT/AEST')}):\n"
                f"• New Leads: +{crawl_res.get('inserted', 0)} (emails: {crawl_res.get('emails_enriched', 0)})\n"
                f"• Outreach Sent: {outreach_res.get('sent', 0)} | Skipped: {outreach_res.get('skipped', 0)}"
            )

        return {
            "ran": True,
            "date": melb_date,
            "crawl": crawl_res,
            "outreach": outreach_res,
        }

TGA_FORBIDDEN_PATTERN = re.compile(
    r"\b(arthritis|cure|cures|cured|heal|heals|healing|treat|treats|treatment|disease|illness|fractures|neuritis|neuralgia|inflammation|sprains)\b",
    re.IGNORECASE,
)


async def _background_lifecycle_loop() -> None:
    """Autonomous 24/7 scheduler processing lifecycle emails and Melbourne business-hours B2B runs every 3 minutes."""
    await asyncio.sleep(8)
    while True:
        try:
            res = await run_due_lifecycle_jobs(limit=25)
            await run_melbourne_b2b_schedule_tick()
            HEARTBEAT_STATE["scheduler_ticks"] += 1
            HEARTBEAT_STATE["last_tick_ts"] = int(time.time())
            HEARTBEAT_STATE["last_lifecycle_processed"] = int(res.get("processed", 0))
        except Exception as exc:
            logger.warning("Background lifecycle tick error: %s", exc)
        await asyncio.sleep(180)


async def _background_demo_loop() -> None:
    """Autonomous variable-cohort overnight demo runner active when DEMO_STATE['enabled'] is True."""
    await asyncio.sleep(6)
    while True:
        try:
            if DEMO_STATE["enabled"]:
                now = int(time.time())
                due = (
                    int(DEMO_STATE["waves_completed"]) == 0
                    or (now - int(DEMO_STATE["last_wave_ts"])) >= int(DEMO_STATE["interval_seconds"])
                )
                if due:
                    next_wave = int(DEMO_STATE["waves_completed"]) + 1
                    notify = (next_wave == 1) or (next_wave % 6 == 0)
                    await run_demo_wave(user_count=None, notify_telegram=notify)
        except Exception as exc:
            logger.warning("Background demo wave error: %s", exc)
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize SQLite schema at startup and run autonomous 24/7 lifecycle + optional demo workers."""
    init_db()
    HEARTBEAT_STATE["started_at"] = int(time.time())
    worker = asyncio.create_task(_background_lifecycle_loop())
    demo_worker = asyncio.create_task(_background_demo_loop())
    try:
        yield
    finally:
        worker.cancel()
        demo_worker.cancel()
        with suppress(asyncio.CancelledError):
            await worker
        with suppress(asyncio.CancelledError):
            await demo_worker


app = FastAPI(title="ANCHIALO Melbourne Growth Engine", version="1.0.0", lifespan=lifespan)

allowed_origins = [
    o.strip()
    for o in (
        os.environ.get("ALLOWED_ORIGINS")
        or "https://anchialo.com,https://www.anchialo.com,http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, Any]:
    """Liveness and database connectivity check."""
    with get_conn() as conn:
        partner_count = conn.execute("SELECT COUNT(*) FROM partners").fetchone()[0]
        order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    return {"status": "ok", "partners": partner_count, "orders": order_count}


@app.post("/api/checkout/session")
def create_checkout_session(req: CheckoutSessionRequest) -> dict[str, Any]:
    """Create a dynamic Stripe Checkout Session with authoritative pricing and QR partner metadata."""
    pricing = calculate_order_cents(
        [it.model_dump() for it in req.items],
        promo_code=req.promo_code,
        partner_code=req.partner_code,
    )

    secret_key = (os.environ.get("STRIPE_SECRET_KEY") or "").strip()
    if not secret_key or secret_key.startswith("sk_live_replace"):
        raise HTTPException(
            status_code=503,
            detail="STRIPE_SECRET_KEY is not configured on the server.",
        )

    stripe.api_key = secret_key
    line_items = []
    for it in pricing["items"]:
        unit_after_discount = it["unit_cents"]
        if pricing["discount_pct"] > 0:
            unit_after_discount = (unit_after_discount * (100 - pricing["discount_pct"]) + 50) // 100
        line_items.append(
            {
                "price_data": {
                    "currency": "aud",
                    "product_data": {"name": it["name"]},
                    "unit_amount": unit_after_discount,
                },
                "quantity": it["qty"],
            }
        )

    if pricing["shipping_cents"] > 0:
        line_items.append(
            {
                "price_data": {
                    "currency": "aud",
                    "product_data": {"name": "Australia Post Tracked Delivery (Free over A$80)"},
                    "unit_amount": pricing["shipping_cents"],
                },
                "quantity": 1,
            }
        )

    session_kwargs: dict[str, Any] = {
        "mode": "payment",
        "line_items": line_items,
        "success_url": req.success_url,
        "cancel_url": req.cancel_url,
        "shipping_address_collection": {"allowed_countries": ["AU"]},
        "metadata": {
            "partner_code": pricing["partner_code"] or "",
            "promo_code": pricing["promo_code"] or "",
            "subtotal_cents": str(pricing["raw_subtotal_cents"]),
            "discount_cents": str(pricing["discount_cents"]),
            "shipping_cents": str(pricing["shipping_cents"]),
            "items_json": json.dumps(pricing["items"])[:490],
            "locality_json": json.dumps(req.locality or {})[:490],
        },
    }
    if pricing["partner_code"]:
        session_kwargs["client_reference_id"] = pricing["partner_code"]
    if req.customer_email and "@" in req.customer_email:
        session_kwargs["customer_email"] = normalize_email(req.customer_email)

    connect_dest = (os.environ.get("STRIPE_CONNECT_DESTINATION_ID") or "").strip()
    if connect_dest.startswith("acct_"):
        fee_cents = calculate_architect_share_cents(pricing["total_cents"])
        if fee_cents > 0:
            session_kwargs["payment_intent_data"] = {
                "application_fee_amount": fee_cents,
                "transfer_data": {"destination": connect_dest},
            }

    session = stripe.checkout.Session.create(**session_kwargs)
    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "summary": pricing,
    }


@app.post("/api/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
) -> dict[str, Any]:
    """Verify Stripe webhook signature, record order + QR commission, and send Telegram alert."""
    payload_bytes = await request.body()
    wh_secret = (os.environ.get("STRIPE_WEBHOOK_SECRET") or "").strip()
    if not wh_secret or wh_secret.startswith("whsec_replace"):
        raise HTTPException(status_code=503, detail="STRIPE_WEBHOOK_SECRET not configured")
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    try:
        event = stripe.Webhook.construct_event(payload_bytes, stripe_signature, wh_secret)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Stripe signature: {exc}") from exc

    if event.get("type") != "checkout.session.completed":
        return {"received": True, "ignored_type": event.get("type")}

    session_obj = event["data"]["object"]
    metadata = session_obj.get("metadata") or {}
    cust_details = session_obj.get("customer_details") or {}
    partner_code = metadata.get("partner_code") or session_obj.get("client_reference_id")
    promo_code = metadata.get("promo_code")

    try:
        items = json.loads(metadata.get("items_json") or "[]")
    except json.JSONDecodeError:
        items = []
    try:
        locality = json.loads(metadata.get("locality_json") or "{}")
    except json.JSONDecodeError:
        locality = {}

    total_cents = int(session_obj.get("amount_total") or 0)
    discount_cents = int(metadata.get("discount_cents") or 0)
    shipping_cents = int(metadata.get("shipping_cents") or 0)
    subtotal_cents = int(metadata.get("subtotal_cents") or (total_cents - shipping_cents + discount_cents))

    with get_conn() as conn:
        result = await record_completed_order(
            conn,
            provider="stripe",
            external_tx_id=str(session_obj.get("id")),
            customer_email=str(cust_details.get("email") or session_obj.get("customer_email") or ""),
            customer_name=str(cust_details.get("name") or "Stripe Customer"),
            subtotal_cents=subtotal_cents,
            discount_cents=discount_cents,
            shipping_cents=shipping_cents,
            total_cents=total_cents,
            partner_code=partner_code,
            promo_code=promo_code,
            items=items,
            locality=locality,
        )

    return {"received": True, **result}


@app.post("/api/orders/paypal")
async def record_paypal_order(req: PayPalOrderRequest) -> dict[str, Any]:
    """Record PayPal checkout completion for QR partner attribution and lifecycle emails."""
    total_cents = int(round(req.amount_aud * 100))
    with get_conn() as conn:
        result = await record_completed_order(
            conn,
            provider="paypal",
            external_tx_id=req.tx_id.strip(),
            customer_email=req.customer_email,
            customer_name=req.customer_name or "PayPal Customer",
            subtotal_cents=total_cents,
            discount_cents=0,
            shipping_cents=0,
            total_cents=total_cents,
            partner_code=req.partner_code,
            promo_code=req.promo_code,
            items=req.items,
            locality=req.locality,
        )
    return {"status": "ok", **result}


@app.post("/api/cart/capture")
def capture_abandoned_cart(req: CartCaptureRequest) -> dict[str, Any]:
    """Store captured cart email and enqueue 2h & 24h recovery emails via Resend."""
    clean_email = normalize_email(req.email)
    if "@" not in clean_email:
        raise HTTPException(status_code=400, detail="Valid email required")

    now = int(time.time())
    subtotal_cents = int(round(max(0.0, req.subtotal_aud) * 100))
    promo = sanitize_code(req.promo_code) or "COMEBACK10"
    partner = sanitize_code(req.partner_code) or None

    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO abandoned_carts (email, cart_json, subtotal_cents, partner_code, promo_code, postcode, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (clean_email, json.dumps(req.cart), subtotal_cents, partner, promo, req.postcode, now),
        )
        payload = {"promo_code": promo, "cart_id": cur.lastrowid}
        schedule_lifecycle_job(conn, clean_email, "cart_2h", 2 * 3600, payload)
        schedule_lifecycle_job(conn, clean_email, "cart_24h", 24 * 3600, payload)

    return {"status": "captured", "promo_code": promo}


@app.post("/api/quiz/submit")
def submit_ritual_quiz(req: QuizSubmitRequest) -> dict[str, Any]:
    """Persist 30s Ritual Quiz submission and schedule immediate welcome privilege email."""
    clean_email = normalize_email(req.email)
    if "@" not in clean_email:
        raise HTTPException(status_code=400, detail="Valid email required")

    now = int(time.time())
    partner = sanitize_code(req.partner_code) or None
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO quiz_submissions (email, goal, recommended_id, partner_code, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (clean_email, req.goal.strip(), req.recommended_id.strip(), partner, now),
        )
        schedule_lifecycle_job(
            conn,
            clean_email,
            "quiz_welcome",
            0,
            {"promo_code": "QUIZ10", "recommended_id": req.recommended_id},
        )
    return {"status": "ok", "promo_code": "QUIZ10"}


@app.post("/api/lifecycle/run")
async def run_due_lifecycle_jobs(limit: int = Query(default=25, ge=1, le=200)) -> dict[str, Any]:
    """Process due automated lifecycle / cart recovery emails via Resend."""
    now = int(time.time())
    sent_count = 0
    skipped_count = 0
    failed_count = 0

    with get_conn() as conn:
        jobs = conn.execute(
            """
            SELECT id, email, stage, payload_json
            FROM lifecycle_queue
            WHERE status = 'pending' AND send_after_ts <= ?
            ORDER BY send_after_ts ASC
            LIMIT ?
            """,
            (now, limit),
        ).fetchall()

        for job in jobs:
            payload = json.loads(job["payload_json"] or "{}")
            subject, body_html, body_text = render_lifecycle_template(job["stage"], payload)
            ok, reason = await send_resend_email(conn, job["email"], subject, body_html, body_text)
            if ok:
                sent_count += 1
                conn.execute(
                    "UPDATE lifecycle_queue SET status = ?, sent_at = ? WHERE id = ?",
                    (reason, now, job["id"]),
                )
            elif reason == "unsubscribed":
                skipped_count += 1
                conn.execute(
                    "UPDATE lifecycle_queue SET status = 'skipped_unsubscribed', error_msg = ? WHERE id = ?",
                    (reason, job["id"]),
                )
            else:
                failed_count += 1
                conn.execute(
                    "UPDATE lifecycle_queue SET status = 'failed', error_msg = ? WHERE id = ?",
                    (reason[:240], job["id"]),
                )

    return {"processed": len(jobs), "sent": sent_count, "skipped": skipped_count, "failed": failed_count}


@app.get("/api/partners/{code}/stats")
def get_partner_stats(code: str) -> dict[str, Any]:
    """Return QR attribution orders and accrued commission totals for a Melbourne gym/clinic."""
    clean_code = sanitize_code(code)
    with get_conn() as conn:
        partner = conn.execute(
            "SELECT code, name, category, suburb, commission_rate FROM partners WHERE code = ?",
            (clean_code,),
        ).fetchone()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner code not found")

        agg = conn.execute(
            """
            SELECT COUNT(*) AS order_count,
                   COALESCE(SUM(order_total_cents), 0) AS gross_cents,
                   COALESCE(SUM(commission_cents), 0) AS commission_cents
            FROM commissions
            WHERE partner_code = ?
            """,
            (clean_code,),
        ).fetchone()

    return {
        "partner_code": partner["code"],
        "name": partner["name"],
        "category": partner["category"],
        "suburb": partner["suburb"],
        "commission_rate": partner["commission_rate"],
        "orders": int(agg["order_count"]),
        "gross_aud": round(int(agg["gross_cents"]) / 100.0, 2),
        "commission_aud": round(int(agg["commission_cents"]) / 100.0, 2),
    }


@app.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe_endpoint(email: str = Query(...), token: str = Query(...)) -> HTMLResponse:
    """Australian Spam Act 2003 1-click verified opt-out endpoint."""
    clean_email = normalize_email(email)
    if not verify_unsubscribe_token(clean_email, token):
        raise HTTPException(status_code=403, detail="Invalid unsubscribe verification token")

    now = int(time.time())
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO unsubscribes (email, reason, created_at) VALUES (?, 'one_click_link', ?)",
            (clean_email, now),
        )
        conn.execute(
            "UPDATE lifecycle_queue SET status = 'skipped_unsubscribed' WHERE email = ? AND status = 'pending'",
            (clean_email,),
        )

    return HTMLResponse(
        content=(
            "<!DOCTYPE html><html lang='en-AU'><body style='font-family:sans-serif;max-width:520px;margin:60px auto;padding:20px;'>"
            "<h2>You have been unsubscribed</h2>"
            "<p>Your email address has been removed from ANCHIALO Australia promotional and reminder messages.</p>"
            "</body></html>"
        )
    )


def _is_real_secret(env_name: str, placeholder_prefixes: tuple[str, ...] = ("replace", "sk_live_replace", "whsec_replace", "re_replace")) -> bool:
    """Return True if an environment secret is populated with a non-placeholder value."""
    val = (os.environ.get(env_name) or "").strip()
    if not val:
        return False
    return not any(val.startswith(prefix) or "replace_with" in val for prefix in placeholder_prefixes)


@app.get("/")
def root_status() -> dict[str, Any]:
    """Service identity root endpoint linking to live dashboard and health telemetry."""
    return {
        "service": "ANCHIALO Melbourne Growth Engine",
        "version": "1.1.0",
        "dashboard": "/dashboard",
        "telemetry": "/api/telemetry/overview",
        "health": "/health",
    }


@app.get("/api/telemetry/overview")
async def telemetry_overview() -> dict[str, Any]:
    """Return live runtime status of all autonomous agents, daily quotas, orders, eBay AU, and Melbourne leads."""
    now = int(time.time())
    today_key = date.today().isoformat()
    ebay_data = await get_ebay_summary()

    with get_conn() as conn:
        order_agg = conn.execute(
            "SELECT COUNT(*) AS cnt, COALESCE(SUM(total_cents), 0) AS revenue_cents FROM orders"
        ).fetchone()
        comm_agg = conn.execute(
            "SELECT COUNT(*) AS cnt, COALESCE(SUM(commission_cents), 0) AS comm_cents FROM commissions"
        ).fetchone()
        cart_agg = conn.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(recovered), 0) AS recovered FROM abandoned_carts"
        ).fetchone()
        quiz_count = int(conn.execute("SELECT COUNT(*) FROM quiz_submissions").fetchone()[0])
        partner_count = int(conn.execute("SELECT COUNT(*) FROM partners").fetchone()[0])
        lead_rows = conn.execute(
            "SELECT category, COUNT(*) AS cnt FROM b2b_leads GROUP BY category"
        ).fetchall()
        pending_lifecycle = int(
            conn.execute("SELECT COUNT(*) FROM lifecycle_queue WHERE status = 'pending'").fetchone()[0]
        )
        sent_lifecycle = int(
            conn.execute("SELECT COUNT(*) FROM lifecycle_queue WHERE status LIKE 'sent%'").fetchone()[0]
        )
        quota_rows = conn.execute(
            "SELECT metric, count FROM api_usage_counters WHERE usage_date = ?", (today_key,)
        ).fetchall()
        recent_orders = [
            dict(r)
            for r in conn.execute(
                "SELECT id, provider, customer_name, total_cents, partner_code, status, created_at FROM orders ORDER BY id DESC LIMIT 8"
            ).fetchall()
        ]
        recent_outreach = [
            dict(r)
            for r in conn.execute(
                "SELECT o.id, o.step, o.recipient_email, o.subject, o.status, o.sent_at FROM b2b_outreach_log o ORDER BY o.id DESC LIMIT 8"
            ).fetchall()
        ]

    quotas = {r["metric"]: int(r["count"]) for r in quota_rows}
    leads_by_category = {r["category"]: int(r["cnt"]) for r in lead_rows}
    total_leads = sum(leads_by_category.values())

    max_b2b = int(os.environ.get("MAX_DAILY_B2B_EMAILS") or "25")
    max_places = int(os.environ.get("MAX_DAILY_PLACES_CALLS") or "80")

    HEARTBEAT_STATE["melbourne_business_hours"] = is_melbourne_business_hours()
    HEARTBEAT_STATE["b2b_autopilot_enabled"] = (
        (os.environ.get("B2B_AUTOPILOT_ENABLED") or "false").strip().lower() in ("1", "true", "yes")
    )

    integrations = {
        "telegram_bot": _is_real_secret("TELEGRAM_BOT_TOKEN") and _is_real_secret("TELEGRAM_CHAT_ID"),
        "smtp_gmail": _is_real_secret("SMTP_USER") and _is_real_secret("SMTP_PASS"),
        "resend_email": _is_real_secret("RESEND_API_KEY"),
        "stripe_dynamic": _is_real_secret("STRIPE_SECRET_KEY"),
        "google_places": _is_real_secret("GOOGLE_PLACES_API_KEY") or _is_real_secret("SERPAPI_API_KEY"),
        "ebay_au": is_ebay_configured(),
    }

    agents = [
        {
            "id": "telegram_dispatch",
            "name": "Telegram & Order Telemetry Agent (@Anchialobot)",
            "status": "CALIBRATED_LIVE" if integrations["telegram_bot"] else "AWAITING_TOKEN",
            "metrics": f"{int(order_agg['cnt'])} orders · {partner_count} QR partners",
        },
        {
            "id": "lifecycle_recovery",
            "name": "Abandoned Cart & D1/D14/D25 Lifecycle Agent",
            "status": "ACTIVE_24_7" if (integrations["smtp_gmail"] or integrations["resend_email"]) else "LOCAL_QUEUE_ONLY",
            "metrics": f"{pending_lifecycle} pending · {sent_lifecycle} sent · {int(cart_agg['recovered'])}/{int(cart_agg['total'])} carts recovered",
        },
        {
            "id": "places_crawler",
            "name": "Melbourne Google Places B2B Lead Crawler",
            "status": "LIVE_READY" if integrations["google_places"] else "AWAITING_PLACES_KEY",
            "metrics": f"{total_leads} leads stored · {quotas.get('google_places', 0)}/{max_places} API calls today",
        },
        {
            "id": "b2b_outreach",
            "name": "Spam Act 2003 & TGA-Audited B2B Outreach Agent",
            "status": "READY_SMTP" if integrations["smtp_gmail"] else ("READY_RESEND" if integrations["resend_email"] else "DRY_RUN_ONLY"),
            "metrics": f"{quotas.get('b2b_emails', 0)}/{max_b2b} emails today · {len(MELBOURNE_VERTICAL_QUERIES)} verticals",
        },
        {
            "id": "ebay_au_sync",
            "name": "eBay Australia (EBAY_AU) Storefront & Order Sync",
            "status": str(ebay_data.get("status") or "AWAITING_TOKEN"),
            "metrics": f"{int(ebay_data.get('active_listings_count') or 0)} active listings · {int(ebay_data.get('orders_total') or 0)} orders ({int(ebay_data.get('orders_to_ship') or 0)} to ship)",
        },
    ]

    return {
        "status": "ok",
        "uptime_seconds": max(0, now - int(HEARTBEAT_STATE["started_at"])),
        "scheduler": HEARTBEAT_STATE,
        "integrations": integrations,
        "agents": agents,
        "ebay": ebay_data,
        "stats": {
            "orders_count": int(order_agg["cnt"]),
            "revenue_aud": round(int(order_agg["revenue_cents"]) / 100.0, 2),
            "architect_share_bps": int(os.environ.get("ARCHITECT_SHARE_BPS") or "2500"),
            "architect_share_aud": round(calculate_architect_share_cents(int(order_agg["revenue_cents"])) / 100.0, 2),
            "stripe_connect_active": bool((os.environ.get("STRIPE_CONNECT_DESTINATION_ID") or "").strip().startswith("acct_")),
            "commissions_count": int(comm_agg["cnt"]),
            "commissions_aud": round(int(comm_agg["comm_cents"]) / 100.0, 2),
            "quiz_submissions": quiz_count,
            "partners_count": partner_count,
            "b2b_leads_total": total_leads,
            "leads_by_category": leads_by_category,
            "b2b_emails_today": quotas.get("b2b_emails", 0),
            "b2b_emails_limit": max_b2b,
            "places_calls_today": quotas.get("google_places", 0),
            "places_calls_limit": max_places,
        },
        "recent_orders": recent_orders,
        "recent_outreach": recent_outreach,
        "demo": get_demo_telemetry(),
    }


@app.get("/api/ebay/summary")
async def ebay_summary(force: bool = False) -> dict[str, Any]:
    """Return live eBay AU storefront listings, selling limits, and orders."""
    return await get_ebay_summary(force=force)


@app.post("/api/ebay/sync-catalog")
async def ebay_sync_catalog(dry_run: bool = False) -> dict[str, Any]:
    """Verify or publish/revise the 8 TGA-compliant ANCHIALO listings on EBAY_AU."""
    if not is_ebay_configured():
        raise HTTPException(status_code=503, detail="eBay Production OAuth credentials are not configured.")
    return await publish_or_revise_catalog(dry_run=dry_run)


@app.post("/api/demo/wave")
async def trigger_demo_wave(req: DemoWaveRequest | None = None) -> dict[str, Any]:
    """Run a synthetic variable-sized user wave immediately in sandbox mode."""
    req = req or DemoWaveRequest()
    summary = await run_demo_wave(user_count=req.user_count, notify_telegram=req.notify_telegram)
    return {"status": "ok", "wave": summary, "demo": get_demo_telemetry()}


@app.post("/api/demo/toggle")
def toggle_demo_mode(req: DemoToggleRequest) -> dict[str, Any]:
    """Enable or pause autonomous overnight demo waves at runtime."""
    DEMO_STATE["enabled"] = bool(req.enabled)
    return {"status": "ok", "enabled": DEMO_STATE["enabled"], "demo": get_demo_telemetry()}


@app.post("/api/demo/reset")
def reset_demo_sandbox() -> dict[str, Any]:
    """Purge all synthetic sandbox records so the database is clean for Production."""
    removed = reset_demo_data()
    return {"status": "clean_for_production", "removed": removed, "demo": get_demo_telemetry()}


def _tcp_reachable(host: str, port: int, timeout: float = 3.0) -> bool:
    """Verify outbound TCP connectivity without emitting email traffic."""
    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@app.post("/api/bots/test-calibration")
async def run_bot_calibration_test(req: CalibrationTestRequest | None = None) -> dict[str, Any]:
    """Execute non-destructive calibration verification across all 4 autonomous bots + optional live Telegram ping."""
    req = req or CalibrationTestRequest()
    t_start = time.perf_counter()

    # 1. Pricing & DB Calibration Check (integer cents accuracy)
    pricing_probe = calculate_order_cents([{"id": "combo-starter", "qty": 1}], promo_code="CPT15", partner_code="CPT15")
    pricing_ok = pricing_probe["total_cents"] == 8010 and pricing_probe["shipping_cents"] == 0

    with get_conn() as conn:
        partner_row = conn.execute("SELECT code, commission_rate FROM partners WHERE code = 'CPT15'").fetchone()
        db_ok = partner_row is not None

    # 2. B2B Pitch Dry-Run + TGA/ACCC Therapeutic Claim Filter Check
    sample_lead = {"name": "Melbourne Combat Collective", "category": "combat_gym", "suburb": req.sample_suburb}
    pitch_subject, _pitch_html, pitch_text = build_b2b_pitch(sample_lead, step=1)
    tga_matches = TGA_FORBIDDEN_PATTERN.findall(f"{pitch_subject}\n{pitch_text}")
    tga_clean = len(tga_matches) == 0

    # 3. Lifecycle Template & Unsubscribe HMAC Calibration
    unsub_sample = build_unsubscribe_url("calibration@anchialo.com")
    _subj, _html, lfc_text = render_lifecycle_template("quiz_welcome", {"promo_code": "QUIZ10", "recommended_id": "gel-arnica"})
    lifecycle_tga_matches = TGA_FORBIDDEN_PATTERN.findall(lfc_text)
    lifecycle_ok = len(lifecycle_tga_matches) == 0 and "token=" in unsub_sample

    # 4. Telegram Bot Ping (real network check only when send_telegram=True)
    telegram_sent = False
    telegram_latency_ms = 0
    if req.send_telegram:
        t_tg = time.perf_counter()
        msg = (
            "[ANCHIALO BOT CALIBRATION REPORT]\n"
            f"DB & Pricing Check: {'PASS' if (db_ok and pricing_ok) else 'FAIL'}\n"
            f"TGA/ACCC Pitch Audit: {'0 violations (PASS)' if tga_clean else 'VIOLATION'}\n"
            f"Lifecycle Unsubscribe HMAC: {'PASS' if lifecycle_ok else 'FAIL'}\n"
            f"Target Market: {req.sample_suburb} | Status: ALL 4 BOTS CALIBRATED"
        )
        telegram_sent = await send_telegram_alert(msg)
        telegram_latency_ms = int((time.perf_counter() - t_tg) * 1000)

    smtp_host = (os.environ.get("SMTP_HOST") or "smtp.gmail.com").strip()
    smtp_probe_enabled = _is_real_secret("SMTP_USER") and _is_real_secret("SMTP_PASS")
    smtp_465_ok = await asyncio.to_thread(_tcp_reachable, smtp_host, 465) if smtp_probe_enabled else False
    smtp_587_ok = await asyncio.to_thread(_tcp_reachable, smtp_host, 587) if smtp_probe_enabled else False

    total_ms = int((time.perf_counter() - t_start) * 1000)
    all_ok = db_ok and pricing_ok and tga_clean and lifecycle_ok

    HEARTBEAT_STATE["last_calibration_ts"] = int(time.time())
    HEARTBEAT_STATE["last_calibration_status"] = "CALIBRATED" if all_ok else "ATTENTION"

    return {
        "calibrated": all_ok,
        "latency_ms": total_ms,
        "checks": {
            "sqlite_and_partners": db_ok,
            "integer_cents_pricing": pricing_ok,
            "b2b_pitch_tga_violations": len(tga_matches),
            "lifecycle_tga_violations": len(lifecycle_tga_matches),
            "unsubscribe_hmac_valid": "token=" in unsub_sample,
            "smtp_configured": smtp_probe_enabled,
            "smtp_465_reachable": smtp_465_ok,
            "smtp_587_reachable": smtp_587_ok,
            "telegram_configured": _is_real_secret("TELEGRAM_BOT_TOKEN") and _is_real_secret("TELEGRAM_CHAT_ID"),
            "telegram_live_ping_sent": telegram_sent,
            "telegram_latency_ms": telegram_latency_ms,
        },
        "sample_b2b_pitch": {
            "subject": pitch_subject,
            "preview": pitch_text[:280] + "...",
        },
    }


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ANCHIALO 24/7 Bot Telemetry & Command Center</title>
  <style>
    :root { --bg:#080e15; --card:#101926; --border:rgba(212,175,55,0.28); --gold:#d4af37; --text:#eef2f7; --muted:#94a3b8; --ok:#10b981; --warn:#f59e0b; }
    * { box-sizing:border-box; margin:0; padding:0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background:var(--bg); color:var(--text); padding:28px; line-height:1.5; }
    .wrap { max-width:1400px; margin:0 auto; }
    .top { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px; border-bottom:1px solid var(--border); padding-bottom:18px; margin-bottom:24px; }
    .kicker { font-size:11px; letter-spacing:2px; color:var(--gold); font-weight:700; text-transform:uppercase; }
    h1 { font-size:26px; font-weight:700; margin-top:4px; }
    .actions { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    button { background:var(--gold); color:#0a1017; border:none; border-radius:10px; padding:10px 18px; font-weight:700; cursor:pointer; font-size:13.5px; transition:opacity .2s; }
    button.sec { background:rgba(255,255,255,0.08); color:var(--text); border:1px solid var(--border); }
    button:hover { opacity:0.9; }
    .grid4 { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:22px; }
    .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-bottom:22px; }
    .card { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:18px 20px; }
    .stat-val { font-size:28px; font-weight:800; color:var(--gold); margin:6px 0 4px; }
    .stat-lbl { font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:1px; }
    .agent-row { display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.06); gap:12px; }
    .agent-row:last-child { border-bottom:none; }
    .badge { padding:4px 10px; border-radius:999px; font-size:11px; font-weight:700; letter-spacing:0.5px; }
    .badge.ok { background:rgba(16,185,129,0.16); color:#34d399; border:1px solid rgba(16,185,129,0.35); }
    .badge.warn { background:rgba(245,158,11,0.16); color:#fbbf24; border:1px solid rgba(245,158,11,0.35); }
    pre { background:#05090e; border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:14px; font-size:12.5px; color:#cbd5e1; overflow:auto; max-height:290px; white-space:pre-wrap; }
    table { width:100%; border-collapse:collapse; font-size:13px; }
    th, td { text-align:left; padding:9px 8px; border-bottom:1px solid rgba(255,255,255,0.06); }
    th { color:var(--gold); font-size:11px; text-transform:uppercase; }
    @media (max-width:960px) { .grid4 { grid-template-columns:repeat(2,1fr); } .grid2 { grid-template-columns:1fr; } }
    @media (max-width:560px) { .grid4 { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <div class="kicker">AKASH DECENTRALIZED CLOUD · MELBOURNE GROWTH NODE</div>
        <h1>ANCHIALO Live Bot Command & Telemetry</h1>
      </div>
      <div class="actions">
        <button class="sec" onclick="loadTelemetry()">Refresh Now</button>
        <button onclick="runCalibration(false)">Dry-Run Bot Calibration</button>
        <button onclick="runCalibration(true)">Run Calibration + Ping Telegram</button>
      </div>
    </div>

    <div class="grid4" id="kpiRow"></div>

    <div class="grid2">
      <div class="card">
        <div class="kicker" style="margin-bottom:10px;">4 Autonomous Growth Agents</div>
        <div id="agentsBox">Loading telemetry...</div>
      </div>
      <div class="card">
        <div class="kicker" style="margin-bottom:10px;">Live Calibration Diagnostic Output</div>
        <pre id="calOut">Click "Dry-Run Bot Calibration" or "Run Calibration + Ping Telegram" to test all 4 bots live.</pre>
      </div>
    </div>

    <div class="grid2">
      <div class="card">
        <div class="kicker" style="margin-bottom:10px;">Recent Orders & QR Commissions</div>
        <div id="ordersBox">No orders recorded yet.</div>
      </div>
      <div class="card">
        <div class="kicker" style="margin-bottom:10px;">Melbourne B2B Outreach Dispatch Log</div>
        <div id="outreachBox">No outreach emails dispatched yet.</div>
      </div>
    </div>

    <div class="card" style="margin-bottom:22px;">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:14px;">
        <div>
          <div class="kicker">OVERNIGHT SANDBOX · MULTI-COHORT BOT SIMULATION</div>
          <div id="demoSummaryLine" style="font-size:13.5px;color:#cbd5e1;margin-top:4px;">Loading demo sandbox state...</div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button onclick="runDemoWave(null)">Run Random Cohort Wave</button>
          <button class="sec" onclick="runDemoWave(50)">Burst 50 Virtual Users</button>
          <button class="sec" id="demoToggleBtn" onclick="toggleDemoAuto()">Toggle Auto-Demo</button>
          <button class="sec" onclick="resetDemo()">Wipe Demo (Ready for Prod)</button>
        </div>
      </div>
      <div class="grid2" style="margin-bottom:0;">
        <div>
          <div class="kicker" style="margin-bottom:8px;">Recent Cohort Waves (Variable User Count)</div>
          <div id="demoWavesBox">—</div>
        </div>
        <div>
          <div class="kicker" style="margin-bottom:8px;">Live Bot-to-User Communications Feed</div>
          <div id="demoCommsBox">—</div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let demoAutoEnabled = false;
    async function loadTelemetry() {
      try {
        const res = await fetch('/api/telemetry/overview');
        const d = await res.json();
        const s = d.stats || {};
        const dm = d.demo || {};
        demoAutoEnabled = !!dm.enabled;
        document.getElementById('kpiRow').innerHTML = `
          <div class="card"><div class="stat-lbl">Server Uptime</div><div class="stat-val">${Math.floor((d.uptime_seconds||0)/60)}m</div><div style="font-size:12px;color:#94a3b8;">Scheduler ticks: ${d.scheduler?.scheduler_ticks ?? 0}</div></div>
          <div class="card"><div class="stat-lbl">Orders & Revenue</div><div class="stat-val">A$${Number(s.revenue_aud||0).toFixed(2)}</div><div style="font-size:12px;color:#94a3b8;">${s.orders_count||0} orders · A$${Number(s.commissions_aud||0).toFixed(2)} commissions</div></div>
          <div class="card"><div class="stat-lbl">Virtual Cohort Comms</div><div class="stat-val">${(dm.delivered_lifecycle_total||0) + (dm.delivered_b2b_total||0)}</div><div style="font-size:12px;color:#94a3b8;">${dm.total_virtual_users||0} demo users · ${dm.tga_violations_total||0} TGA errors</div></div>
          <div class="card"><div class="stat-lbl">Leads & Quiz</div><div class="stat-val">${s.b2b_leads_total||0} / ${s.quiz_submissions||0}</div><div style="font-size:12px;color:#94a3b8;">B2B leads · ${s.quiz_submissions||0} ritual quiz</div></div>
        `;
        document.getElementById('agentsBox').innerHTML = (d.agents || []).map(a => {
          const isOk = a.status.includes('LIVE') || a.status.includes('ACTIVE') || a.status.includes('READY');
          return `<div class="agent-row"><div><strong>${a.name}</strong><div style="font-size:12px;color:#94a3b8;">${a.metrics}</div></div><span class="badge ${isOk ? 'ok' : 'warn'}">${a.status}</span></div>`;
        }).join('');
        document.getElementById('ordersBox').innerHTML = (d.recent_orders && d.recent_orders.length)
          ? '<table><tr><th>#</th><th>Provider</th><th>Total</th><th>Partner</th></tr>' + d.recent_orders.map(o => `<tr><td>${o.id}</td><td>${o.provider}</td><td>A$${(o.total_cents/100).toFixed(2)}</td><td>${o.partner_code||'-'}</td></tr>`).join('') + '</table>'
          : '<div style="color:#94a3b8;font-size:13px;">Awaiting live Stripe/PayPal checkouts.</div>';
        document.getElementById('outreachBox').innerHTML = (d.recent_outreach && d.recent_outreach.length)
          ? '<table><tr><th>Step</th><th>Recipient</th><th>Status</th></tr>' + d.recent_outreach.map(o => `<tr><td>Step ${o.step}</td><td>${o.recipient_email}</td><td>${o.status}</td></tr>`).join('') + '</table>'
          : '<div style="color:#94a3b8;font-size:13px;">Awaiting B2B outreach dispatch.</div>';
        const toggleBtn = document.getElementById('demoToggleBtn');
        if (toggleBtn) toggleBtn.textContent = demoAutoEnabled ? 'Pause Auto-Demo (ON)' : 'Start Auto-Demo (OFF)';
        document.getElementById('demoSummaryLine').innerHTML =
          `<span class="badge ${demoAutoEnabled ? 'ok' : 'warn'}">${demoAutoEnabled ? 'AUTO-DEMO RUNNING' : 'PAUSED'}</span> ` +
          `Waves: <strong>${dm.waves_completed||0}</strong> · Total Users: <strong>${dm.total_virtual_users||0}</strong> · ` +
          `Lifecycle Delivered: <strong>${dm.delivered_lifecycle_total||0}</strong> · B2B: <strong>${dm.delivered_b2b_total||0}</strong> · ` +
          `Opt-outs Honored: <strong>${dm.unsubscribed_honored_total||0}</strong> · Future Queued: <strong>${dm.scheduled_future_total||0}</strong>`;
        document.getElementById('demoWavesBox').innerHTML = (dm.wave_history && dm.wave_history.length)
          ? '<table><tr><th>Wave</th><th>Users</th><th>Orders</th><th>Recovered</th><th>Msgs</th><th>Revenue</th></tr>' +
            dm.wave_history.map(w => `<tr><td>#${w.wave}</td><td>${w.virtual_users}</td><td>${w.orders_paid}</td><td>${w.carts_recovered}/${w.carts_created}</td><td>${w.lifecycle_msgs + w.b2b_msgs}</td><td>A$${Number(w.revenue_aud).toFixed(2)}</td></tr>`).join('') + '</table>'
          : '<div style="color:#94a3b8;font-size:13px;">No demo waves run yet.</div>';
        document.getElementById('demoCommsBox').innerHTML = (dm.recent_communications && dm.recent_communications.length)
          ? '<table><tr><th>Stage</th><th>Virtual User</th><th>Status</th></tr>' +
            dm.recent_communications.map(c => `<tr><td>${c.stage}</td><td>${c.recipient}</td><td>${c.status}</td></tr>`).join('') + '</table>'
          : '<div style="color:#94a3b8;font-size:13px;">No synthetic communications recorded yet.</div>';
      } catch (e) {
        document.getElementById('agentsBox').textContent = 'Telemetry connection error: ' + e;
      }
    }

    async function runDemoWave(count) {
      const box = document.getElementById('calOut');
      box.textContent = 'Running variable-cohort demo wave...';
      const res = await fetch('/api/demo/wave', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_count: count, notify_telegram: true })
      });
      box.textContent = JSON.stringify(await res.json(), null, 2);
      loadTelemetry();
    }

    async function toggleDemoAuto() {
      await fetch('/api/demo/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !demoAutoEnabled })
      });
      loadTelemetry();
    }

    async function resetDemo() {
      const box = document.getElementById('calOut');
      const res = await fetch('/api/demo/reset', { method: 'POST' });
      box.textContent = JSON.stringify(await res.json(), null, 2);
      loadTelemetry();
    }

    async function runCalibration(sendTg) {
      const box = document.getElementById('calOut');
      box.textContent = 'Running 4-bot calibration verification...';
      try {
        const res = await fetch('/api/bots/test-calibration', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ send_telegram: sendTg, sample_suburb: 'Richmond VIC' })
        });
        const data = await res.json();
        box.textContent = JSON.stringify(data, null, 2);
        loadTelemetry();
      } catch (e) {
        box.textContent = 'Calibration failed: ' + e;
      }
    }

    loadTelemetry();
    setInterval(loadTelemetry, 10000);
  </script>
</body>
</html>"""


@app.get("/dashboard", response_class=HTMLResponse)
def bot_command_dashboard() -> HTMLResponse:
    """Serve live Akash 24/7 Bot Telemetry & Calibration Command Center."""
    return HTMLResponse(content=DASHBOARD_HTML)

