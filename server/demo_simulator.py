"""Autonomous multi-cohort Demo Simulator for overnight verification of ANCHIALO bots."""

import json
import os
import random
import re
import sqlite3
import time
from typing import Any

from db import DEFAULT_PARTNERS, get_conn
from notifications import build_unsubscribe_url, render_lifecycle_template, send_telegram_alert, sign_unsubscribe_token
from outreach_agent import build_b2b_pitch

DEMO_DOMAIN = "anchialo-sandbox.invalid"

FIRST_NAMES = [
    "Liam", "Noah", "Oliver", "Jack", "William", "Charlotte", "Amelia", "Olivia",
    "Mia", "Isla", "Lucas", "Henry", "Leo", "Chloe", "Grace", "Ethan", "Marcus",
    "Sofia", "Elena", "Nikos", "Georgi", "Lachlan", "Toby", "Hannah",
]
LAST_NAMES = [
    "Smith", "Jones", "Williams", "Brown", "Taylor", "Wilson", "Anderson", "Papadopoulos",
    "Dimitrov", "Georgiev", "Nguyen", "Kelly", "Murphy", "Martin", "White", "Thompson",
]
SUBURBS = [
    ("Melbourne", "VIC", "3000"),
    ("Richmond", "VIC", "3121"),
    ("South Yarra", "VIC", "3141"),
    ("Fitzroy", "VIC", "3065"),
    ("Collingwood", "VIC", "3066"),
    ("Oakleigh", "VIC", "3166"),
    ("Brighton", "VIC", "3186"),
    ("St Kilda", "VIC", "3182"),
    ("Kensington", "VIC", "3031"),
    ("Brunswick", "VIC", "3056"),
]
GOALS = ["sport", "sleep", "stress", "skin", "everyday"]
SKUS = [
    ("gel-arnica", "Dual Magnesium Gel | Arnica Blend (300g)", 4900),
    ("gel-lavender", "Dual Magnesium Gel | Lavender Blend (300g)", 4900),
    ("gel-rosemary", "Dual Magnesium Gel | Rosemary Blend (300g)", 4900),
    ("gel-juniper", "Dual Magnesium Gel | Juniper Blend (300g)", 4900),
    ("gel-grape", "Dual Magnesium Gel | Grape Blend (300g)", 4900),
    ("oil-pure", "Dual Magnesium Oil | Pure Topical Brine (300ml)", 4900),
    ("combo-starter", "Starter Combo | Dual Magnesium Gel (2-Pack)", 8900),
    ("combo-best-value", "Best Value Combo | Dual Magnesium Gel (3-Pack)", 12900),
]
B2B_SYNTHETIC_VENUES = [
    ("Melbourne Ironhouse MMA", "combat_gym", "Richmond"),
    ("Bayside Myotherapy Studio", "myotherapy", "Brighton"),
    ("Fitzroy Reformer Collective", "pilates", "Fitzroy"),
    ("Oakleigh Hellenic Athletics", "greek_hub", "Oakleigh"),
    ("Yarra Contrast & Float House", "float_sauna", "South Yarra"),
    ("Collingwood Muay Thai Lab", "combat_gym", "Collingwood"),
    ("Brunswick Sports Massage Clinic", "myotherapy", "Brunswick"),
    ("St Kilda Recovery & Cryo", "float_sauna", "St Kilda"),
]

TGA_GUARD = re.compile(
    r"\b(arthritis|cure|cures|cured|heal|heals|healing|treat|treats|treatment|disease|illness|fractures|neuritis|neuralgia|inflammation|sprains)\b",
    re.IGNORECASE,
)

DEMO_STATE: dict[str, Any] = {
    "enabled": (os.environ.get("DEMO_SIMULATION_ENABLED") or "false").strip().lower() in ("1", "true", "yes", "on"),
    "interval_seconds": max(60, int(os.environ.get("DEMO_WAVE_INTERVAL_SECONDS") or "600")),
    "waves_completed": 0,
    "total_virtual_users": 0,
    "last_wave_ts": 0,
    "last_wave_users": 0,
    "tga_violations_total": 0,
    "wave_history": [],
}


def _demo_email(seq: int, wave: int, tag: str = "u") -> str:
    """Create RFC 2606 non-routable sandbox email so zero real external addresses are contacted."""
    fn = FIRST_NAMES[(seq + wave) % len(FIRST_NAMES)].lower()
    ln = LAST_NAMES[(seq * 3 + wave) % len(LAST_NAMES)].lower()
    return f"{fn}.{ln}.{tag}{wave}_{seq}@{DEMO_DOMAIN}"


def _audit_tga(subject: str, text: str) -> int:
    """Count any TGA/ACCC forbidden therapeutic terms in generated messages."""
    return len(TGA_GUARD.findall(f"{subject}\n{text}"))


def _seed_demo_b2b_venues(conn: sqlite3.Connection, now: int) -> None:
    """Ensure synthetic B2B sandbox venues exist for simulated B2B outreach."""
    for idx, (name, cat, suburb) in enumerate(B2B_SYNTHETIC_VENUES, start=1):
        place_id = f"demo_place_{idx}"
        email = f"hello.venue{idx}@{DEMO_DOMAIN}"
        conn.execute(
            """
            INSERT OR IGNORE INTO b2b_leads
                (place_id, name, category, suburb, address, phone, website, email, score, status, created_at)
            VALUES (?, ?, ?, ?, ?, '', ?, ?, ?, 'new', ?)
            """,
            (
                place_id,
                f"[DEMO] {name}",
                cat,
                suburb,
                f"{10 + idx * 7} High St, {suburb} VIC",
                f"https://venue{idx}.{DEMO_DOMAIN}",
                email,
                75 + (idx % 20),
                now,
            ),
        )


def _record_demo_order(
    conn: sqlite3.Connection,
    *,
    wave: int,
    seq: int,
    customer_email: str,
    customer_name: str,
    sku_tuple: tuple[str, str, int],
    qty: int,
    partner_code: str | None,
    promo_code: str | None,
    suburb_tuple: tuple[str, str, str],
    provider: str,
    now: int,
) -> tuple[int, int, int]:
    """Persist synthetic paid order + commission and enqueue D1/D14/D25 lifecycle jobs."""
    sku_id, sku_name, unit_cents = sku_tuple
    raw_sub = unit_cents * qty
    discount_pct = 10 if (promo_code or partner_code) else 0
    discount_cents = (raw_sub * discount_pct + 50) // 100
    final_sub = max(0, raw_sub - discount_cents)
    shipping_cents = 0 if final_sub >= 8000 else 1500
    total_cents = final_sub + shipping_cents
    tx_id = f"demo_{provider}_{wave}_{seq}_{now}"

    items = [{"id": sku_id, "name": sku_name, "qty": qty, "unit_cents": unit_cents, "line_cents": raw_sub}]
    locality = {"location": suburb_tuple[0], "state": suburb_tuple[1], "postcode": suburb_tuple[2]}

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
            tx_id,
            customer_email,
            customer_name,
            raw_sub,
            discount_cents,
            shipping_cents,
            total_cents,
            partner_code,
            promo_code,
            json.dumps(items),
            json.dumps(locality),
            now,
        ),
    )
    order_id = int(cur.lastrowid)

    commission_cents = 0
    if partner_code:
        p_row = conn.execute("SELECT commission_rate FROM partners WHERE code = ?", (partner_code,)).fetchone()
        rate = float(p_row["commission_rate"]) if p_row else 0.18
        basis = max(0, total_cents - shipping_cents)
        commission_cents = int(round(basis * rate))
        conn.execute(
            """
            INSERT INTO commissions (order_id, partner_code, order_total_cents, commission_rate, commission_cents, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'accrued', ?)
            """,
            (order_id, partner_code, basis, rate, commission_cents, now),
        )

    conn.execute(
        "UPDATE abandoned_carts SET recovered = 1 WHERE email = ? AND recovered = 0",
        (customer_email,),
    )
    conn.execute(
        "UPDATE lifecycle_queue SET status = 'cancelled_recovered' WHERE email = ? AND stage IN ('cart_2h', 'cart_24h') AND status = 'pending'",
        (customer_email,),
    )

    payload = json.dumps({"customer_name": customer_name, "promo_code": promo_code or "COMEBACK10", "order_id": order_id})
    # Stagger due timestamps: some D1 ready immediately in demo so retention bot delivers them this cycle
    d1_delay = 0 if (seq % 2 == 0) else 3600
    d14_delay = 0 if (seq % 5 == 0) else 14 * 86400
    d25_delay = 0 if (seq % 7 == 0) else 25 * 86400
    for stg, delay in (("post_d1_usage", d1_delay), ("post_d14_review", d14_delay), ("post_d25_reorder", d25_delay)):
        conn.execute(
            "INSERT INTO lifecycle_queue (email, stage, payload_json, send_after_ts, status) VALUES (?, ?, ?, ?, 'pending')",
            (customer_email, stg, payload, now + delay),
        )

    return order_id, total_cents, commission_cents


async def run_demo_wave(
    user_count: int | None = None,
    *,
    notify_telegram: bool = False,
) -> dict[str, Any]:
    """Run one variable-sized synthetic customer + B2B communication wave in sandbox mode."""
    wave_num = int(DEMO_STATE["waves_completed"]) + 1
    cohort = max(1, min(200, int(user_count))) if user_count is not None else random.randint(8, 34)
    now = int(time.time())
    rng = random.Random(now ^ (wave_num * 7919))

    partner_codes = [p[0] for p in DEFAULT_PARTNERS]
    quiz_users = 0
    carts_created = 0
    carts_recovered = 0
    orders_paid = 0
    revenue_cents = 0
    commissions_cents = 0
    lifecycle_dispatched = 0
    unsub_skipped = 0
    b2b_dispatched = 0
    tga_violations = 0

    with get_conn() as conn:
        _seed_demo_b2b_venues(conn, now)

        # 1. Generate varying cohort of virtual customers interacting with storefront/quiz/checkout
        for seq in range(1, cohort + 1):
            fname = FIRST_NAMES[(seq + wave_num) % len(FIRST_NAMES)]
            lname = LAST_NAMES[(seq * 5 + wave_num) % len(LAST_NAMES)]
            full_name = f"{fname} {lname}"
            email = _demo_email(seq, wave_num)
            suburb = SUBURBS[(seq + wave_num) % len(SUBURBS)]
            sku = SKUS[(seq * 3 + wave_num) % len(SKUS)]
            partner = partner_codes[seq % len(partner_codes)] if (seq % 3 != 0) else None
            goal = GOALS[seq % len(GOALS)]

            # Simulate ~4% Spam Act 2003 opt-outs verified via HMAC
            opted_out = (seq % 23 == 0)
            if opted_out:
                _tok = sign_unsubscribe_token(email)
                conn.execute(
                    "INSERT OR IGNORE INTO unsubscribes (email, reason, created_at) VALUES (?, 'demo_one_click', ?)",
                    (email, now),
                )

            role_roll = rng.random()
            if role_roll < 0.30:
                # Blend Finder Quiz user -> schedules immediate quiz_welcome
                quiz_users += 1
                conn.execute(
                    "INSERT INTO quiz_submissions (email, goal, recommended_id, partner_code, created_at) VALUES (?, ?, ?, ?, ?)",
                    (email, goal, sku[0], partner, now),
                )
                conn.execute(
                    "INSERT INTO lifecycle_queue (email, stage, payload_json, send_after_ts, status) VALUES (?, 'quiz_welcome', ?, ?, 'pending')",
                    (email, json.dumps({"customer_name": fname, "promo_code": "QUIZ10", "recommended_id": sku[0]}), now),
                )
            elif role_roll < 0.65:
                # Abandoned cart -> schedules cart_2h (due now in demo) & cart_24h; ~45% recover into paid order
                carts_created += 1
                cart_payload = json.dumps([{"id": sku[0], "name": sku[1], "qty": 1}])
                conn.execute(
                    "INSERT INTO abandoned_carts (email, cart_json, subtotal_cents, partner_code, promo_code, postcode, created_at) VALUES (?, ?, ?, ?, 'COMEBACK10', ?, ?)",
                    (email, cart_payload, sku[2], partner, suburb[2], now),
                )
                # Render & simulate 2h recovery outreach right away before potential conversion
                lfc_payload = {"customer_name": fname, "promo_code": "COMEBACK10"}
                subj, _html, txt = render_lifecycle_template("cart_2h", lfc_payload)
                unsub_url = build_unsubscribe_url(email)
                tga_violations += _audit_tga(subj, f"{txt}\n{unsub_url}")
                if opted_out:
                    unsub_skipped += 1
                    conn.execute(
                        "INSERT INTO lifecycle_queue (email, stage, payload_json, send_after_ts, sent_at, status) VALUES (?, 'cart_2h', ?, ?, ?, 'skipped_unsubscribed')",
                        (email, json.dumps(lfc_payload), now, now),
                    )
                else:
                    lifecycle_dispatched += 1
                    conn.execute(
                        "INSERT INTO lifecycle_queue (email, stage, payload_json, send_after_ts, sent_at, status) VALUES (?, 'cart_2h', ?, ?, ?, 'demo_delivered')",
                        (email, json.dumps(lfc_payload), now, now),
                    )
                    if rng.random() < 0.45:
                        carts_recovered += 1
                        orders_paid += 1
                        _oid, tot, comm = _record_demo_order(
                            conn,
                            wave=wave_num,
                            seq=seq,
                            customer_email=email,
                            customer_name=full_name,
                            sku_tuple=sku,
                            qty=1,
                            partner_code=partner,
                            promo_code="COMEBACK10",
                            suburb_tuple=suburb,
                            provider="stripe" if seq % 2 == 0 else "paypal",
                            now=now,
                        )
                        revenue_cents += tot
                        commissions_cents += comm
                    else:
                        conn.execute(
                            "INSERT INTO lifecycle_queue (email, stage, payload_json, send_after_ts, status) VALUES (?, 'cart_24h', ?, ?, 'pending')",
                            (email, json.dumps(lfc_payload), now + 22 * 3600),
                        )
            else:
                # Direct customer checkout (Stripe or PayPal)
                qty = 2 if (seq % 4 == 0 and sku[2] == 4900) else 1
                orders_paid += 1
                _oid, tot, comm = _record_demo_order(
                    conn,
                    wave=wave_num,
                    seq=seq,
                    customer_email=email,
                    customer_name=full_name,
                    sku_tuple=sku,
                    qty=qty,
                    partner_code=partner,
                    promo_code=partner or "FOUNDING10",
                    suburb_tuple=suburb,
                    provider="stripe" if seq % 2 == 0 else "paypal",
                    now=now,
                )
                revenue_cents += tot
                commissions_cents += comm

        # 2. Process due sandbox lifecycle communications (quiz_welcome, cart_2h, post_d1/d14/d25)
        due_rows = conn.execute(
            """
            SELECT id, email, stage, payload_json
            FROM lifecycle_queue
            WHERE status = 'pending' AND email LIKE ? AND send_after_ts <= ?
            ORDER BY id ASC
            LIMIT 60
            """,
            (f"%@{DEMO_DOMAIN}", now),
        ).fetchall()

        for job in due_rows:
            email_addr = job["email"]
            is_unsub = conn.execute("SELECT 1 FROM unsubscribes WHERE email = ?", (email_addr,)).fetchone() is not None
            payload = json.loads(job["payload_json"] or "{}")
            subj, _html, txt = render_lifecycle_template(job["stage"], payload)
            tga_violations += _audit_tga(subj, txt)
            if is_unsub:
                unsub_skipped += 1
                conn.execute(
                    "UPDATE lifecycle_queue SET status = 'skipped_unsubscribed', sent_at = ? WHERE id = ?",
                    (now, job["id"]),
                )
            else:
                lifecycle_dispatched += 1
                conn.execute(
                    "UPDATE lifecycle_queue SET status = 'demo_delivered', sent_at = ? WHERE id = ?",
                    (now, job["id"]),
                )

        # 3. Run synthetic B2B outreach communications (1-4 Melbourne venues per wave, RFC 2606 .invalid)
        b2b_target_count = min(len(B2B_SYNTHETIC_VENUES), max(1, cohort // 7))
        leads = conn.execute(
            "SELECT id, name, category, suburb, email FROM b2b_leads WHERE place_id LIKE 'demo_place_%' ORDER BY id ASC LIMIT ?",
            (b2b_target_count,),
        ).fetchall()
        step = ((wave_num - 1) % 3) + 1
        for lead in leads:
            subj, _html, txt = build_b2b_pitch(dict(lead), step=step)
            tga_violations += _audit_tga(subj, txt)
            b2b_dispatched += 1
            conn.execute(
                """
                INSERT INTO b2b_outreach_log (lead_id, step, recipient_email, subject, body, status, sent_at)
                VALUES (?, ?, ?, ?, ?, 'demo_sent', ?)
                """,
                (lead["id"], step, lead["email"], subj, txt[:2000], now),
            )

    DEMO_STATE["waves_completed"] = wave_num
    DEMO_STATE["total_virtual_users"] += cohort
    DEMO_STATE["last_wave_ts"] = now
    DEMO_STATE["last_wave_users"] = cohort
    DEMO_STATE["tga_violations_total"] += tga_violations

    wave_summary = {
        "wave": wave_num,
        "ts": now,
        "virtual_users": cohort,
        "quiz_users": quiz_users,
        "carts_created": carts_created,
        "carts_recovered": carts_recovered,
        "orders_paid": orders_paid,
        "revenue_aud": round(revenue_cents / 100.0, 2),
        "commissions_aud": round(commissions_cents / 100.0, 2),
        "lifecycle_msgs": lifecycle_dispatched,
        "b2b_msgs": b2b_dispatched,
        "unsubscribed": unsub_skipped,
        "tga_violations": tga_violations,
    }
    history = DEMO_STATE["wave_history"]
    history.insert(0, wave_summary)
    del history[15:]

    if notify_telegram:
        verdict = "READY FOR PRODUCTION" if tga_violations == 0 else "CHECK TGA FILTER"
        tg_msg = (
            f"[ANCHIALO DEMO WAVE #{wave_num}]\n"
            f"Virtual Cohort: {cohort} users (Total: {DEMO_STATE['total_virtual_users']})\n"
            f"Orders: {orders_paid} (A${revenue_cents / 100:.2f}) | QR Comm: A${commissions_cents / 100:.2f}\n"
            f"Carts: {carts_created} captured / {carts_recovered} recovered | Quiz: {quiz_users}\n"
            f"Bot Comms Sent: {lifecycle_dispatched} lifecycle + {b2b_dispatched} B2B ({unsub_skipped} opt-outs honored)\n"
            f"TGA/ACCC Audit: {tga_violations} violations | Status: {verdict}"
        )
        await send_telegram_alert(tg_msg)

    return wave_summary


def get_demo_telemetry() -> dict[str, Any]:
    """Read cumulative synthetic communication breakdown and recent bot-to-user log."""
    with get_conn() as conn:
        stage_rows = conn.execute(
            """
            SELECT stage, status, COUNT(*) AS cnt
            FROM lifecycle_queue
            WHERE email LIKE ?
            GROUP BY stage, status
            """,
            (f"%@{DEMO_DOMAIN}",),
        ).fetchall()
        b2b_demo_cnt = int(
            conn.execute(
                "SELECT COUNT(*) FROM b2b_outreach_log WHERE recipient_email LIKE ?",
                (f"%@{DEMO_DOMAIN}",),
            ).fetchone()[0]
        )
        recent_lfc = conn.execute(
            """
            SELECT stage, email AS recipient, status, COALESCE(sent_at, send_after_ts) AS ts
            FROM lifecycle_queue
            WHERE email LIKE ? AND status IN ('demo_delivered', 'skipped_unsubscribed')
            ORDER BY id DESC
            LIMIT 12
            """,
            (f"%@{DEMO_DOMAIN}",),
        ).fetchall()
        recent_b2b = conn.execute(
            """
            SELECT ('b2b_step_' || step) AS stage, recipient_email AS recipient, status, sent_at AS ts
            FROM b2b_outreach_log
            WHERE recipient_email LIKE ?
            ORDER BY id DESC
            LIMIT 6
            """,
            (f"%@{DEMO_DOMAIN}",),
        ).fetchall()

    stage_breakdown: dict[str, int] = {}
    delivered_total = 0
    unsub_total = 0
    pending_future = 0
    for r in stage_rows:
        cnt = int(r["cnt"])
        if r["status"] == "demo_delivered":
            stage_breakdown[r["stage"]] = stage_breakdown.get(r["stage"], 0) + cnt
            delivered_total += cnt
        elif r["status"] == "skipped_unsubscribed":
            unsub_total += cnt
        elif r["status"] == "pending":
            pending_future += cnt
    if b2b_demo_cnt:
        stage_breakdown["b2b_outreach"] = b2b_demo_cnt

    comms = [dict(r) for r in recent_lfc] + [dict(r) for r in recent_b2b]
    comms.sort(key=lambda x: int(x.get("ts") or 0), reverse=True)

    return {
        **DEMO_STATE,
        "delivered_lifecycle_total": delivered_total,
        "delivered_b2b_total": b2b_demo_cnt,
        "unsubscribed_honored_total": unsub_total,
        "scheduled_future_total": pending_future,
        "stage_breakdown": stage_breakdown,
        "recent_communications": comms[:14],
    }


def reset_demo_data() -> dict[str, int]:
    """Delete only synthetic sandbox records cleanly to switch database back to Production state."""
    with get_conn() as conn:
        c_orders = conn.execute(
            "DELETE FROM orders WHERE external_tx_id LIKE 'demo_%'"
        ).rowcount
        c_carts = conn.execute(
            "DELETE FROM abandoned_carts WHERE email LIKE ?", (f"%@{DEMO_DOMAIN}",)
        ).rowcount
        c_quiz = conn.execute(
            "DELETE FROM quiz_submissions WHERE email LIKE ?", (f"%@{DEMO_DOMAIN}",)
        ).rowcount
        c_lfc = conn.execute(
            "DELETE FROM lifecycle_queue WHERE email LIKE ?", (f"%@{DEMO_DOMAIN}",)
        ).rowcount
        c_unsub = conn.execute(
            "DELETE FROM unsubscribes WHERE email LIKE ?", (f"%@{DEMO_DOMAIN}",)
        ).rowcount
        c_b2b_log = conn.execute(
            "DELETE FROM b2b_outreach_log WHERE recipient_email LIKE ?", (f"%@{DEMO_DOMAIN}",)
        ).rowcount
        c_leads = conn.execute(
            "DELETE FROM b2b_leads WHERE place_id LIKE 'demo_place_%'"
        ).rowcount

    DEMO_STATE["waves_completed"] = 0
    DEMO_STATE["total_virtual_users"] = 0
    DEMO_STATE["last_wave_ts"] = 0
    DEMO_STATE["last_wave_users"] = 0
    DEMO_STATE["tga_violations_total"] = 0
    DEMO_STATE["wave_history"] = []

    return {
        "orders_removed": int(c_orders),
        "carts_removed": int(c_carts),
        "quiz_removed": int(c_quiz),
        "lifecycle_removed": int(c_lfc),
        "unsubscribes_removed": int(c_unsub),
        "b2b_logs_removed": int(c_b2b_log),
        "b2b_leads_removed": int(c_leads),
    }
