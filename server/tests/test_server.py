"""Automated unit & integration tests for the ANCHIALO Melbourne Akash server stack."""

import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

SERVER_DIR = str(Path(__file__).resolve().parents[1])
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

import app as server_app  # noqa: E402
from db import get_conn, init_db  # noqa: E402
from notifications import send_resend_email, sign_unsubscribe_token  # noqa: E402
from outreach_agent import run_daily_b2b_outreach  # noqa: E402
from places_crawler import check_and_increment_places_quota, extract_suburb_from_address  # noqa: E402
from qr_poster_generator import generate_brand_usp_brochures, generate_qr_partner_poster  # noqa: E402


@pytest.fixture()
def test_client(tmp_path, monkeypatch):
    """Provide an isolated SQLite DB and FastAPI TestClient per test."""
    db_file = str(tmp_path / "test_anchialo.db")
    monkeypatch.setenv("ANCHIALO_DB_PATH", db_file)
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret_123")
    monkeypatch.setenv("UNSUBSCRIBE_SECRET", "test_hmac_secret_abc")
    for var in ("RESEND_API_KEY", "SMTP_USER", "SMTP_PASS", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        monkeypatch.delenv(var, raising=False)
    init_db(db_file)
    with TestClient(server_app.app) as client:
        yield client, db_file


def test_authoritative_pricing_and_shipping_cents():
    """Verify server-side integer-cents math for single jar, 2-pack with 10% code, and 3-pack."""
    single = server_app.calculate_order_cents([{"id": "gel-arnica", "qty": 1}], None, None)
    assert single["raw_subtotal_cents"] == 4900
    assert single["discount_cents"] == 0
    assert single["shipping_cents"] == 1500
    assert single["total_cents"] == 6400

    # Starter 2-pack (A$89) with 10% partner code = A$80.10 -> still clears A$80 free shipping threshold!
    two_pack_partner = server_app.calculate_order_cents(
        [{"id": "combo-starter", "qty": 1}], promo_code=None, partner_code="CPT15"
    )
    assert two_pack_partner["raw_subtotal_cents"] == 8900
    assert two_pack_partner["discount_cents"] == 890
    assert two_pack_partner["final_subtotal_cents"] == 8010
    assert two_pack_partner["shipping_cents"] == 0
    assert two_pack_partner["total_cents"] == 8010

    trio = server_app.calculate_order_cents([{"id": "combo-best-value", "qty": 1}], "QUIZ10", None)
    assert trio["raw_subtotal_cents"] == 12900
    assert trio["discount_cents"] == 1290
    assert trio["shipping_cents"] == 0
    assert trio["total_cents"] == 11610


def test_stripe_webhook_records_order_commission_and_lifecycle(test_client):
    """Verify signed Stripe webhook accrues QR commission, recovers cart, and queues D1/D14/D25."""
    client, db_file = test_client

    # Capture an abandoned cart first for the same customer
    res_cart = client.post(
        "/api/cart/capture",
        json={
            "email": "fighter@example.com",
            "cart": [{"id": "combo-starter", "qty": 1}],
            "subtotal_aud": 89.0,
            "partner_code": "CPT15",
            "postcode": "3121",
        },
    )
    assert res_cart.status_code == 200

    mock_event = {
        "id": "evt_test_1",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_999",
                "amount_total": 8010,
                "customer_email": "fighter@example.com",
                "customer_details": {"name": "Alex Fighter", "email": "fighter@example.com"},
                "client_reference_id": "CPT15",
                "metadata": {
                    "partner_code": "CPT15",
                    "promo_code": "CPT15",
                    "subtotal_cents": "8900",
                    "discount_cents": "890",
                    "shipping_cents": "0",
                    "items_json": json.dumps([{"id": "combo-starter", "name": "Starter 2-Pack", "qty": 1}]),
                    "locality_json": json.dumps({"location": "RICHMOND", "state": "VIC", "postcode": "3121"}),
                },
            }
        },
    }

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        res_wh = client.post(
            "/api/webhooks/stripe",
            content=b"{}",
            headers={"Stripe-Signature": "t=123,v1=abc"},
        )
        assert res_wh.status_code == 200
        body = res_wh.json()
        assert body["duplicate"] is False
        # CPT15 is seeded at 20% commission: 8010 * 0.20 = 1602 cents (A$16.02)
        assert body["commission_cents"] == 1602

        # Replay must be idempotent
        res_dup = client.post(
            "/api/webhooks/stripe",
            content=b"{}",
            headers={"Stripe-Signature": "t=123,v1=abc"},
        )
        assert res_dup.status_code == 200
        assert res_dup.json()["duplicate"] is True

    stats_res = client.get("/api/partners/CPT15/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["orders"] == 1
    assert stats["gross_aud"] == 80.10
    assert stats["commission_aud"] == 16.02

    with get_conn(db_file) as conn:
        cart_row = conn.execute("SELECT recovered FROM abandoned_carts WHERE email = 'fighter@example.com'").fetchone()
        assert cart_row["recovered"] == 1
        cancelled = conn.execute(
            "SELECT COUNT(*) FROM lifecycle_queue WHERE email = 'fighter@example.com' AND status = 'cancelled_recovered'"
        ).fetchone()[0]
        assert cancelled == 2
        post_jobs = conn.execute(
            "SELECT stage FROM lifecycle_queue WHERE email = 'fighter@example.com' AND status = 'pending'"
        ).fetchall()
        assert {r["stage"] for r in post_jobs} == {"post_d1_usage", "post_d14_review", "post_d25_reorder"}


def test_spam_act_unsubscribe_and_lifecycle_runner(test_client):
    """Verify HMAC opt-out rejects forged tokens and blocks future queued emails."""
    client, _db = test_client

    bad_res = client.get("/unsubscribe?email=clinic@melbourne.com.au&token=forged123")
    assert bad_res.status_code == 403

    client.post(
        "/api/quiz/submit",
        json={"email": "clinic@melbourne.com.au", "goal": "sport", "recommended_id": "gel-arnica"},
    )

    valid_tok = sign_unsubscribe_token("clinic@melbourne.com.au", secret="test_hmac_secret_abc")
    ok_res = client.get(f"/unsubscribe?email=clinic@melbourne.com.au&token={valid_tok}")
    assert ok_res.status_code == 200
    assert "unsubscribed" in ok_res.text.lower()

    run_res = client.post("/api/lifecycle/run")
    assert run_res.status_code == 200
    assert run_res.json()["sent"] == 0


@pytest.mark.asyncio
async def test_b2b_outreach_respects_unsubscribe_and_quota(tmp_path, monkeypatch):
    """Verify B2B outreach honors daily quota cap and skips unsubscribed addresses."""
    db_file = str(tmp_path / "outreach.db")
    monkeypatch.setenv("ANCHIALO_DB_PATH", db_file)
    monkeypatch.setenv("MAX_DAILY_B2B_EMAILS", "1")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)
    init_db(db_file)

    now = int(time.time())
    with get_conn(db_file) as conn:
        conn.execute(
            """
            INSERT INTO b2b_leads (place_id, name, category, suburb, address, phone, website, email, score, status, created_at)
            VALUES ('p1', 'Opted Out Clinic', 'myotherapy', 'Richmond VIC', '1 Swan St', '', '', 'optout@clinic.com.au', 99, 'new', ?)
            """,
            (now,),
        )
        conn.execute("INSERT INTO unsubscribes (email, reason, created_at) VALUES ('optout@clinic.com.au', 'optout', ?)", (now,))
        conn.execute(
            """
            INSERT INTO b2b_leads (place_id, name, category, suburb, address, phone, website, email, score, status, created_at)
            VALUES ('p2', 'Richmond BJJ', 'combat_gym', 'Richmond VIC', '22 Church St', '', '', 'coach@richmondbjj.com.au', 95, 'new', ?)
            """,
            (now,),
        )
        conn.execute(
            """
            INSERT INTO b2b_leads (place_id, name, category, suburb, address, phone, website, email, score, status, created_at)
            VALUES ('p3', 'Oakleigh Pilates', 'pilates', 'Oakleigh VIC', '9 Eaton Mall', '', '', 'hello@oakleighpilates.com.au', 90, 'new', ?)
            """,
            (now,),
        )

    res = await run_daily_b2b_outreach(db_path=db_file)
    assert res["sent"] == 1
    assert res["remaining_quota"] == 0
    with get_conn(db_file) as conn:
        sent_emails = [
            r["recipient_email"]
            for r in conn.execute("SELECT recipient_email FROM b2b_outreach_log").fetchall()
        ]
        assert sent_emails == ["coach@richmondbjj.com.au"]


def test_places_quota_and_qr_poster_generation(tmp_path):
    """Verify Places API daily quota guard and real PDF/PNG QR poster output."""
    db_file = str(tmp_path / "places.db")
    init_db(db_file)
    with get_conn(db_file) as conn:
        assert check_and_increment_places_quota(conn, 2) is True
        assert check_and_increment_places_quota(conn, 2) is True
        assert check_and_increment_places_quota(conn, 2) is False
    assert extract_suburb_from_address("100 Swan St, Richmond VIC 3121, Australia") == "Richmond VIC 3121"

    poster = generate_qr_partner_poster("CPT15", "CPT MMA Melbourne", output_dir=str(tmp_path))
    assert os.path.exists(poster["pdf_path"])
    assert os.path.exists(poster["poster_png_path"])
    assert poster["target_url"] == "https://anchialo.com/?ref=CPT15#collection"


def test_usp_brochures_generation_and_tga_compliance(tmp_path):
    """Verify customer and B2B USP brochure PDFs are generated cleanly with zero TGA medical claims."""
    import fitz

    brochures = generate_brand_usp_brochures(output_dir=str(tmp_path))
    assert os.path.exists(brochures["product_guide_pdf"])
    assert os.path.exists(brochures["partner_guide_pdf"])

    forbidden = ("arthritis", "neuritis", "neuralgia", "fractures", "inflammation", "sprains")
    for pdf_path in (brochures["product_guide_pdf"], brochures["partner_guide_pdf"]):
        doc = fitz.open(pdf_path)
        assert doc.page_count >= 1
        full_text = "\n".join(page.get_text("text").lower() for page in doc)
        doc.close()
        assert "323.5 g/l" in full_text
        for word in forbidden:
            assert word not in full_text, f"Forbidden TGA term '{word}' found in {pdf_path}"


@pytest.mark.asyncio
async def test_smtp_fallback_when_resend_unset(tmp_path, monkeypatch):
    """Verify SMTP fallback dispatches multipart email with Spam Act unsubscribe headers when Resend is unset."""
    db_file = str(tmp_path / "smtp.db")
    init_db(db_file)
    monkeypatch.setenv("RESEND_API_KEY", "re_replace_me")
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_USER", "sotirkichukov@cptmma.com")
    monkeypatch.setenv("SMTP_PASS", "test-app-password")
    monkeypatch.setenv("UNSUBSCRIBE_SECRET", "smtp_test_hmac_secret")

    sent_messages = []

    class DummySMTP:
        def __init__(self, host, port, timeout=15, context=None):
            self.host = host
            self.port = port

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def login(self, user, password):
            assert user == "sotirkichukov@cptmma.com"
            assert password == "test-app-password"

        def send_message(self, msg):
            sent_messages.append(msg)

    with patch("notifications.smtplib.SMTP_SSL", DummySMTP):
        with get_conn(db_file) as conn:
            ok, status = await send_resend_email(
                conn,
                "coach@melbournegym.com.au",
                "Test Anchialo Tester",
                "<p>Hello Melbourne</p>",
                "Hello Melbourne",
            )

    assert ok is True
    assert status == "sent_smtp"
    assert len(sent_messages) == 1
    msg = sent_messages[0]
    assert msg["To"] == "coach@melbournegym.com.au"
    assert "sotirkichukov@cptmma.com" in msg["From"]
    assert "List-Unsubscribe" in msg
    assert "Unsubscribe" in msg.get_body(preferencelist=("plain",)).get_content()


def test_telemetry_dashboard_and_bot_calibration(test_client):
    """Verify telemetry overview, live HTML command center, and zero-violation 4-bot calibration probe."""
    client, _db_file = test_client

    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "ANCHIALO Live Bot Command" in res_dash.text

    res_tel = client.get("/api/telemetry/overview")
    assert res_tel.status_code == 200
    tel = res_tel.json()
    assert tel["status"] == "ok"
    assert len(tel["agents"]) == 4
    assert tel["stats"]["partners_count"] >= 7

    res_cal = client.post(
        "/api/bots/test-calibration",
        json={"send_telegram": False, "sample_suburb": "South Yarra VIC"},
    )
    assert res_cal.status_code == 200
    cal = res_cal.json()
    assert cal["calibrated"] is True
    assert cal["checks"]["sqlite_and_partners"] is True
    assert cal["checks"]["integer_cents_pricing"] is True
    assert cal["checks"]["b2b_pitch_tga_violations"] == 0
    assert cal["checks"]["lifecycle_tga_violations"] == 0
    assert cal["checks"]["unsubscribe_hmac_valid"] is True


def test_100_virtual_clients_stress_load(test_client):
    """Simulate 100 concurrent-style Melbourne virtual clients across quiz, cart recovery, and checkout bots."""
    client, db_file = test_client
    suburbs = [
        ("ST KILDA", "3182"),
        ("RICHMOND", "3121"),
        ("SOUTH YARRA", "3141"),
        ("OAKLEIGH", "3166"),
        ("CARLTON", "3053"),
        ("BRUNSWICK", "3056"),
        ("DOCKLANDS", "3008"),
        ("FITZROY", "3065"),
        ("BRIGHTON", "3186"),
        ("GEELONG", "3220"),
    ]
    partners = ["CPT15", "RENEGADE15", "ABSOLUTE15", "OAKLEIGH15", "MYO15", "PILATES15", "FLOAT15"]
    skus = [
        ("gel-arnica", 49.0),
        ("gel-lavender", 49.0),
        ("combo-starter", 89.0),
        ("combo-best-value", 129.0),
        ("oil-pure", 49.0),
    ]

    t_start = time.perf_counter()
    for i in range(100):
        suburb, postcode = suburbs[i % len(suburbs)]
        partner = partners[i % len(partners)]
        sku, price = skus[i % len(skus)]
        email = f"melbourne.client.{i}@example.com"

        r_quiz = client.post(
            "/api/quiz/submit",
            json={"email": email, "goal": "sport", "recommended_id": sku, "partner_code": partner},
        )
        assert r_quiz.status_code == 200

        r_cart = client.post(
            "/api/cart/capture",
            json={
                "email": email,
                "cart": [{"id": sku, "qty": 1}],
                "subtotal_aud": price,
                "partner_code": partner,
                "postcode": postcode,
            },
        )
        assert r_cart.status_code == 200

        r_order = client.post(
            "/api/orders/paypal",
            json={
                "tx_id": f"STRESS_TX_{i:04d}",
                "customer_name": f"Virtual Client {i}",
                "customer_email": email,
                "amount_aud": price,
                "partner_code": partner,
                "promo_code": partner,
                "locality": {"location": suburb, "state": "VIC", "postcode": postcode},
                "items": [{"id": sku, "name": sku, "qty": 1}],
            },
        )
        assert r_order.status_code == 200
        assert r_order.json()["duplicate"] is False

    # Process lifecycle welcome + post-order emails cleanly in memory via mocked SMTP
    with patch("notifications.send_resend_email", return_value=(True, "sent_mock")):
        r_lfc = client.post("/api/lifecycle/run?limit=200")
        assert r_lfc.status_code == 200

    elapsed_ms = int((time.perf_counter() - t_start) * 1000)

    tel = client.get("/api/telemetry/overview").json()
    stats = tel["stats"]
    assert stats["quiz_submissions"] == 100
    assert stats["orders_count"] == 100
    assert stats["commissions_count"] == 100
    assert stats["revenue_aud"] > 6000.0
    assert stats["commissions_aud"] > 1000.0
    assert elapsed_ms < 15000, f"100-client stress test took too long: {elapsed_ms}ms"
    print(
        f"\n[STRESS TEST 100 CLIENTS] Time={elapsed_ms}ms | Orders={stats['orders_count']} | "
        f"Revenue=A${stats['revenue_aud']:.2f} | Commissions=A${stats['commissions_aud']:.2f}"
    )


def test_demo_sandbox_variable_cohorts_and_reset(test_client):
    """Verify overnight demo simulator handles varying virtual user counts, dispatches comms, and resets cleanly."""
    client, _db_file = test_client

    r1 = client.post("/api/demo/wave", json={"user_count": 12, "notify_telegram": False})
    assert r1.status_code == 200
    w1 = r1.json()["wave"]
    assert w1["virtual_users"] == 12
    assert w1["tga_violations"] == 0
    assert (w1["lifecycle_msgs"] + w1["b2b_msgs"]) >= 1

    r2 = client.post("/api/demo/wave", json={"user_count": 27, "notify_telegram": False})
    assert r2.status_code == 200
    d2 = r2.json()["demo"]
    assert d2["waves_completed"] == 2
    assert d2["total_virtual_users"] == 39
    assert len(d2["recent_communications"]) >= 1

    r_tog = client.post("/api/demo/toggle", json={"enabled": True})
    assert r_tog.status_code == 200
    assert r_tog.json()["enabled"] is True

    tel = client.get("/api/telemetry/overview").json()
    assert tel["demo"]["enabled"] is True
    assert tel["demo"]["total_virtual_users"] == 39

    r_rst = client.post("/api/demo/reset")
    assert r_rst.status_code == 200
    assert r_rst.json()["status"] == "clean_for_production"

    tel_after = client.get("/api/telemetry/overview").json()
    assert tel_after["demo"]["total_virtual_users"] == 0
    assert tel_after["stats"]["orders_count"] == 0
    assert tel_after["stats"]["partners_count"] >= 7
    client.post("/api/demo/toggle", json={"enabled": False})
