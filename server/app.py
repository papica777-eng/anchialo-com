"""FastAPI 24/7 Akash CPU Growth Engine: Dynamic Stripe Checkout, QR Commissions, Cart Recovery & Lifecycle Automation."""

from contextlib import asynccontextmanager
import json
import logging
import os
import re
import sqlite3
import time
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import stripe

from db import get_conn, init_db
from notifications import (
    normalize_email,
    render_lifecycle_template,
    send_resend_email,
    send_telegram_alert,
    verify_unsubscribe_token,
)

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


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize SQLite schema at startup."""
    init_db()
    yield


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

