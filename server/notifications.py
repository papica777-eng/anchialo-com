"""Telegram dispatcher, Resend + SMTP email transport, Spam Act 2003 opt-out helpers, and cosmetic lifecycle templates."""

import asyncio
from email.message import EmailMessage
import hashlib
import hmac
import html
import logging
import os
import smtplib
import sqlite3
import ssl
import urllib.parse
import httpx

logger = logging.getLogger("anchialo.notifications")


def normalize_email(email: str) -> str:
    """Normalize email address safely."""
    return (email or "").strip().lower()


def sign_unsubscribe_token(email: str, secret: str | None = None) -> str:
    """Create deterministic HMAC-SHA256 opt-out verification token for Spam Act 2003 links."""
    key = (secret or os.environ.get("UNSUBSCRIBE_SECRET") or "anchialo-dev-unsubscribe-key").encode("utf-8")
    msg = normalize_email(email).encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()[:32]


def verify_unsubscribe_token(email: str, token: str, secret: str | None = None) -> bool:
    """Constant-time validation of unsubscribe link signature."""
    expected = sign_unsubscribe_token(email, secret)
    return hmac.compare_digest(expected, (token or "").strip())


def build_unsubscribe_url(email: str) -> str:
    """Construct signed 1-click unsubscribe URL hosted on PUBLIC_BASE_URL."""
    base = (os.environ.get("PUBLIC_BASE_URL") or "https://api.anchialo.com").rstrip("/")
    clean = normalize_email(email)
    tok = sign_unsubscribe_token(clean)
    return f"{base}/unsubscribe?email={urllib.parse.quote(clean)}&token={tok}"


def is_unsubscribed(conn: sqlite3.Connection, email: str) -> bool:
    """Return True if recipient has opted out."""
    clean = normalize_email(email)
    if not clean:
        return True
    row = conn.execute("SELECT 1 FROM unsubscribes WHERE email = ?", (clean,)).fetchone()
    return row is not None


async def send_telegram_alert(message: str) -> bool:
    """Push instant order or warm B2B lead alert to configured Telegram recipients."""
    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    raw_chat_ids = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    chat_ids = [cid.strip() for cid in raw_chat_ids.split(",") if cid.strip()]
    if not token or not chat_ids:
        logger.info("Telegram alert skipped (bot credentials unset): %s", message.replace("\n", " | "))
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    delivered = 0
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for chat_id in chat_ids:
                resp = await client.post(url, json={"chat_id": chat_id, "text": message})
                if resp.status_code >= 400:
                    logger.warning("Telegram API error for %s (%s): %s", chat_id, resp.status_code, resp.text)
                else:
                    delivered += 1
            return delivered > 0
    except httpx.HTTPError as exc:
        logger.warning("Telegram request failed: %s", exc)
        return False


def _send_smtp_sync(
    *,
    host: str,
    port: int,
    smtp_user: str,
    smtp_pass: str,
    from_addr: str,
    to_email: str,
    subject: str,
    html_full: str,
    text_full: str,
    unsub_url: str,
) -> tuple[bool, str]:
    """Send multipart HTML+text email synchronously via SSL or STARTTLS SMTP."""
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["List-Unsubscribe"] = f"<{unsub_url}>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.set_content(text_full)
    msg.add_alternative(html_full, subtype="html")

    tls_ctx = ssl.create_default_context()
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=15, context=tls_ctx) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=tls_ctx)
                server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        return True, "sent_smtp"
    except (smtplib.SMTPException, OSError) as exc:
        return False, f"smtp_error: {exc}"


async def send_resend_email(
    conn: sqlite3.Connection,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str,
) -> tuple[bool, str]:
    """Send transactional or lifecycle email via Resend (or SMTP fallback) while honoring unsubscribes."""
    clean_to = normalize_email(to_email)
    if not clean_to or "@" not in clean_to:
        return False, "invalid_email"
    if is_unsubscribed(conn, clean_to):
        return False, "unsubscribed"

    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    from_addr = (os.environ.get("OUTREACH_FROM_EMAIL") or "Anchialo Australia <hello@anchialoau.com>").strip()
    unsub_url = build_unsubscribe_url(clean_to)
    sender_addr = (os.environ.get("SENDER_PHYSICAL_ADDRESS") or "CPT MMA / Anchialo Australia, Melbourne VIC 3000").strip()

    footer_html = (
        f'<hr style="margin:24px 0;border:none;border-top:1px solid #e5e7eb;">'
        f'<p style="font-size:12px;color:#6b7280;">ANCHIALO Australia · {html.escape(sender_addr)} · '
        f'<a href="{html.escape(unsub_url)}">Unsubscribe instantly</a></p>'
    )
    footer_text = f"\n\n---\nANCHIALO Australia | {sender_addr}\nUnsubscribe: {unsub_url}\n"
    full_html = f"{html_body}{footer_html}"
    full_text = f"{text_body}{footer_text}"

    if api_key and not api_key.startswith("re_replace"):
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": from_addr,
                        "to": [clean_to],
                        "subject": subject,
                        "html": full_html,
                        "text": full_text,
                        "headers": {
                            "List-Unsubscribe": f"<{unsub_url}>",
                            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                        },
                    },
                )
                if resp.status_code >= 400:
                    return False, f"resend_{resp.status_code}: {resp.text[:200]}"
                return True, "sent"
        except httpx.HTTPError as exc:
            return False, f"http_error: {exc}"

    smtp_user = (os.environ.get("SMTP_USER") or "").strip()
    smtp_pass = (os.environ.get("SMTP_PASS") or "").strip()
    if smtp_user and smtp_pass and "replace" not in smtp_pass.lower():
        smtp_host = (os.environ.get("SMTP_HOST") or "smtp.gmail.com").strip()
        try:
            smtp_port = int((os.environ.get("SMTP_PORT") or "465").strip())
        except ValueError:
            smtp_port = 465
        smtp_from = (
            os.environ.get("SMTP_FROM_EMAIL")
            or (from_addr if smtp_user.lower() in from_addr.lower() else f"Sotir at Anchialo <{smtp_user}>")
        ).strip()
        return await asyncio.to_thread(
            _send_smtp_sync,
            host=smtp_host,
            port=smtp_port,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            from_addr=smtp_from,
            to_email=clean_to,
            subject=subject,
            html_full=full_html,
            text_full=full_text,
            unsub_url=unsub_url,
        )

    logger.info("Email dry-run (Resend and SMTP credentials unset) -> to=%s | subject=%s", clean_to, subject)
    return True, "dry_run_logged"


def render_lifecycle_template(stage: str, payload: dict) -> tuple[str, str, str]:
    """Return TGA-compliant (subject, html_body, text_body) for each automated customer stage."""
    store_url = (os.environ.get("STOREFRONT_URL") or "https://anchialo.com").rstrip("/")
    promo = payload.get("promo_code") or "COMEBACK10"
    name = html.escape(str(payload.get("customer_name") or "there"))

    if stage == "cart_2h":
        subject = "Your ANCHIALO Magnesium Bag is Waiting (10% Code Inside)"
        txt = (
            f"Hi {name},\n\nYou left Lake Pomorie Dual Magnesium formulations in your bag on {store_url}.\n"
            f"Use code {promo} for 10% off — and remember orders over A$80 unlock FREE Express dispatch from Melbourne.\n"
            f"Finish anytime: {store_url}/?code={promo}#collection"
        )
        body = (
            f"<p>Hi {name},</p>"
            f"<p>You left authentic Lake Pomorie Dual Magnesium body care in your bag. "
            f"Use code <strong>{html.escape(promo)}</strong> for 10% off — orders over A$80 include FREE Express delivery from Melbourne.</p>"
            f'<p><a href="{store_url}/?code={urllib.parse.quote(promo)}#collection">Return to Your Bag →</a></p>'
        )
        return subject, body, txt

    if stage == "cart_24h":
        subject = "Skip the Watery Spray Drip — Save 10% on Lake Pomorie Gel"
        txt = (
            f"Hi {name},\n\nUnlike watery magnesium sprays that run or crust, ANCHIALO 300g gels glide smoothly for post-training massage and skin hydration.\n"
            f"Use {promo} at {store_url}/?code={promo}#collection or message Sotir on WhatsApp (+61 423 269 586) for CPT MMA pickup."
        )
        body = (
            f"<p>Hi {name},</p>"
            f"<p>Unlike watery sprays that drip, ANCHIALO 300g Dual Magnesium Gels massage smoothly into clean skin and stay put. "
            f"Enjoy 10% off with <strong>{html.escape(promo)}</strong> — dispatched directly from Melbourne.</p>"
            f'<p><a href="{store_url}/?code={urllib.parse.quote(promo)}#collection">Complete Your Order →</a></p>'
        )
        return subject, body, txt

    if stage == "post_d1_usage":
        subject = "How to Get the Best Experience From Your ANCHIALO Dual Magnesium"
        txt = (
            f"Hi {name},\n\nQuick 3-step ritual guide for your Lake Pomorie Dual Magnesium:\n"
            "1. Apply onto clean, dry skin after your shower.\n"
            "2. Massage gently for 30-60 seconds across calves, shoulders, or lower back.\n"
            "3. A light warming tingle from the 253.14 g/L sea brine is normal — leave on 30 mins or overnight, then rinse lightly if any salt crystals remain."
        )
        body = (
            f"<p>Hi {name},</p>"
            "<p>Welcome to your Lake Pomorie mineral ritual. Three quick tips for best comfort:</p>"
            "<ul><li>Apply onto clean, dry skin after a warm shower.</li>"
            "<li>Massage 30–60 seconds into calves, shoulders, or forearms.</li>"
            "<li>Because of the 253.14 g/L mineral density, a light warming feel is normal — leave 30 min or overnight and rinse lightly if desired.</li></ul>"
        )
        return subject, body, txt

    if stage == "post_d14_review":
        subject = "Share Your ANCHIALO Ritual Photo -> Get A$10 Towards Your Next Jar"
        txt = (
            f"Hi {name},\n\nYou have been using ANCHIALO for two weeks. Reply with a quick photo or honest note about how you use it post-training or at night and receive a A$10 gift credit."
        )
        body = (
            f"<p>Hi {name},</p>"
            "<p>It has been two weeks with your Lake Pomorie Dual Magnesium! "
            "Reply to this email with a quick photo or honest note on your ritual and we will send you a <strong>A$10 reward code</strong> for your next jar.</p>"
        )
        return subject, body, txt

    # post_d25_reorder (and quiz_welcome fallback)
    if stage == "quiz_welcome":
        subject = "Your ANCHIALO Blend Match + 10% Welcome Privilege"
        txt = (
            f"Hi {name},\n\nThanks for taking the 30-second ANCHIALO Blend Finder. Use code {promo} for 10% off at {store_url}/?code={promo}#collection."
        )
        body = (
            f"<p>Hi {name},</p>"
            f"<p>Here is your 10% welcome privilege code from the 30-second ANCHIALO Blend Finder: <strong>{html.escape(promo)}</strong>.</p>"
            f'<p><a href="{store_url}/?code={urllib.parse.quote(promo)}#collection">Shop Your Recommended Blend →</a></p>'
        )
        return subject, body, txt

    subject = "Running Low on Magnesium Gel? Restock Today With 10% Off"
    txt = (
        f"Hi {name},\n\nMost athletes finish a 300g jar around Day 25–30. Restock with code {promo} (or grab the 2-Pack for A$89 + Free Express Shipping) at {store_url}/?code={promo}#collection."
    )
    body = (
        f"<p>Hi {name},</p>"
        f"<p>Most daily users finish a 300g jar right around Day 25–30. Restock today using <strong>{html.escape(promo)}</strong> "
        f"or grab the Starter 2-Pack (A$89 + Free Express delivery from Melbourne).</p>"
        f'<p><a href="{store_url}/?code={urllib.parse.quote(promo)}#collection">Restock in 1 Click →</a></p>'
    )
    return subject, body, txt

