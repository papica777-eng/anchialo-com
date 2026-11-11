"""SQLite persistence layer for ANCHIALO Melbourne sales, QR commissions, lifecycle emails, and B2B leads."""

from contextlib import contextmanager
import os
import sqlite3
import time
from typing import Iterator

DEFAULT_PARTNERS = [
    ("CPT15", "CPT MMA Melbourne", "combat_gym", "Melbourne", "", 0.20),
    ("RENEGADE15", "Renegade MMA Partner", "combat_gym", "Kensington / Melbourne", "", 0.18),
    ("ABSOLUTE15", "Absolute MMA Partner", "combat_gym", "Melbourne CBD / Collingwood", "", 0.18),
    ("OAKLEIGH15", "Oakleigh Community Partner", "greek_hub", "Oakleigh VIC 3166", "", 0.18),
    ("MYO15", "Melbourne Myotherapy Partner", "myotherapy", "Greater Melbourne", "", 0.20),
    ("PILATES15", "Melbourne Pilates Partner", "pilates", "Greater Melbourne", "", 0.18),
    ("FLOAT15", "Melbourne Float & Contrast Partner", "float_sauna", "Greater Melbourne", "", 0.18),
]


def resolve_db_path(explicit_path: str | None = None) -> str:
    """Resolve SQLite database path and ensure parent folder exists."""
    path = explicit_path or os.environ.get("ANCHIALO_DB_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "anchialo.db"
    )
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    return path


@contextmanager
def get_conn(db_path: str | None = None) -> Iterator[sqlite3.Connection]:
    """Yield a WAL-mode SQLite connection with Row factory and safe commit/close."""
    resolved = resolve_db_path(db_path)
    conn = sqlite3.connect(resolved, timeout=15.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str | None = None) -> str:
    """Initialize schema tables and seed default Melbourne QR partner codes."""
    resolved = resolve_db_path(db_path)
    now = int(time.time())
    with get_conn(resolved) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS partners (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'gym',
                suburb TEXT NOT NULL DEFAULT 'Melbourne',
                contact_email TEXT NOT NULL DEFAULT '',
                commission_rate REAL NOT NULL DEFAULT 0.18,
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                external_tx_id TEXT NOT NULL UNIQUE,
                customer_email TEXT NOT NULL DEFAULT '',
                customer_name TEXT NOT NULL DEFAULT '',
                subtotal_cents INTEGER NOT NULL,
                discount_cents INTEGER NOT NULL DEFAULT 0,
                shipping_cents INTEGER NOT NULL DEFAULT 0,
                total_cents INTEGER NOT NULL,
                partner_code TEXT,
                promo_code TEXT,
                items_json TEXT NOT NULL,
                locality_json TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'paid',
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL UNIQUE,
                partner_code TEXT NOT NULL,
                order_total_cents INTEGER NOT NULL,
                commission_rate REAL NOT NULL,
                commission_cents INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'accrued',
                created_at INTEGER NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS abandoned_carts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                cart_json TEXT NOT NULL,
                subtotal_cents INTEGER NOT NULL,
                partner_code TEXT,
                promo_code TEXT,
                postcode TEXT NOT NULL DEFAULT '3000',
                recovered INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS quiz_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                goal TEXT NOT NULL,
                recommended_id TEXT NOT NULL,
                partner_code TEXT,
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS lifecycle_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                stage TEXT NOT NULL,
                payload_json TEXT NOT NULL DEFAULT '{}',
                send_after_ts INTEGER NOT NULL,
                sent_at INTEGER,
                status TEXT NOT NULL DEFAULT 'pending',
                error_msg TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS b2b_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                place_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                suburb TEXT NOT NULL DEFAULT 'Melbourne',
                address TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                website TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                score INTEGER NOT NULL DEFAULT 50,
                status TEXT NOT NULL DEFAULT 'new',
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS b2b_outreach_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                step INTEGER NOT NULL,
                recipient_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'sent',
                sent_at INTEGER NOT NULL,
                FOREIGN KEY(lead_id) REFERENCES b2b_leads(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS unsubscribes (
                email TEXT PRIMARY KEY,
                reason TEXT NOT NULL DEFAULT 'user_opt_out',
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS api_usage_counters (
                usage_date TEXT NOT NULL,
                metric TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (usage_date, metric)
            );
            """
        )
        for code, name, cat, suburb, email, rate in DEFAULT_PARTNERS:
            conn.execute(
                """
                INSERT OR IGNORE INTO partners (code, name, category, suburb, contact_email, commission_rate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (code, name, cat, suburb, email, rate, now),
            )
    return resolved

