"""Production eBay Australia (EBAY_AU) OAuth client, catalog publisher, and order synchronizer."""

from __future__ import annotations

import asyncio
import base64
from html import escape
import json
import logging
import os
import time
from typing import Any
import xml.etree.ElementTree as ET

import httpx

from db import get_conn

logger = logging.getLogger("anchialo.ebay")

EBAY_OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_TRADING_URL = "https://api.ebay.com/ws/api.dll"
EBAY_SELL_PRIVILEGE_URL = "https://api.ebay.com/sell/account/v1/privilege"
EBAY_SELL_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order"
EBAY_NS = "urn:ebay:apis:eBLBaseComponents"

_TOKEN_CACHE: dict[str, Any] = {
    "access_token": "",
    "expires_at": 0,
}

_SUMMARY_CACHE: dict[str, Any] = {
    "data": None,
    "fetched_at": 0,
}

# TGA & ACCC compliant cosmetic catalog for EBAY_AU (titles strictly <= 80 chars)
EBAY_AU_CATALOG: list[dict[str, Any]] = [
    {
        "sku": "ANCHIALO-GEL-ARNICA",
        "title": "ANCHIALO Dual Magnesium Gel Arnica 300g | Lake Pomorie Black Sea Lye AU",
        "price_aud": "49.00",
        "qty": 25,
        "formulation": "Gel",
        "size": "300g",
        "botanical": "Arnica Montana Flower Extract",
        "image_url": "https://anchialo.com/assets/images/products/06_file_transp.png",
        "subtitle": "Post-Training Body Ritual & Skin Comfort",
        "summary": "Fast-absorbing cosmetic topical body gel with 253.14 g/L Magnesium Chloride and 70.36 g/L Magnesium Sulfate from Lake Pomorie, enriched with Arnica Montana flower extract.",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA FLOWER EXTRACT.",
    },
    {
        "sku": "ANCHIALO-GEL-LAVENDER",
        "title": "ANCHIALO Dual Magnesium Gel Lavender 300g | Lake Pomorie Black Sea Lye",
        "price_aud": "49.00",
        "qty": 25,
        "formulation": "Gel",
        "size": "300g",
        "botanical": "Lavandula Angustifolia Flower Extract",
        "image_url": "https://anchialo.com/assets/images/products/01_file_transp.png",
        "subtitle": "Calming Evening Ritual & Skin Nourishment",
        "summary": "Calming cosmetic topical body gel combining Lake Pomorie Black Sea magnesium salts with Bulgarian Lavender flower extract for evening massage and skin hydration.",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT.",
    },
    {
        "sku": "ANCHIALO-GEL-ROSEMARY",
        "title": "ANCHIALO Dual Magnesium Gel Rosemary 300g | Lake Pomorie Black Sea Lye",
        "price_aud": "49.00",
        "qty": 25,
        "formulation": "Gel",
        "size": "300g",
        "botanical": "Rosmarinus Officinalis Leaf Extract",
        "image_url": "https://anchialo.com/assets/images/products/04_file_transp.png",
        "subtitle": "Invigorating Massage & Morning Skin Refresh",
        "summary": "Invigorating cosmetic body massage gel uniting 253.14 g/L Magnesium Chloride and 70.36 g/L Magnesium Sulfate with Garden Rosemary extract.",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ROSMARINUS OFFICINALIS LEAF POWDER EXTRACT.",
    },
    {
        "sku": "ANCHIALO-GEL-JUNIPER",
        "title": "ANCHIALO Dual Magnesium Gel Juniper 300g | Lake Pomorie Black Sea Lye AU",
        "price_aud": "49.00",
        "qty": 25,
        "formulation": "Gel",
        "size": "300g",
        "botanical": "Juniperus Chinensis Leaf Extract",
        "image_url": "https://anchialo.com/assets/images/products/07_file_transp.png",
        "subtitle": "Crisp Botanical Massage & Body Refreshment",
        "summary": "Refreshing cosmetic body gel with concentrated Lake Pomorie magnesium salts and Alpine Juniper extract for post-shower and sauna skin care.",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE, JUNIPERUS CHINENSIS LEAF EXTRACT.",
    },
    {
        "sku": "ANCHIALO-GEL-GRAPE",
        "title": "ANCHIALO Dual Magnesium Gel Red Grape 300g | Lake Pomorie Black Sea Lye",
        "price_aud": "49.00",
        "qty": 25,
        "formulation": "Gel",
        "size": "300g",
        "botanical": "Vitis Vinifera Seed Polyphenol Extract",
        "image_url": "https://anchialo.com/assets/images/products/03_file_transp.png",
        "subtitle": "Skin Softness & Antioxidant Body Care",
        "summary": "Revitalizing cosmetic topical body gel formulated with Lake Pomorie dual magnesium minerals and subtle red grape aroma for smooth, hydrated skin.",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE.",
    },
    {
        "sku": "ANCHIALO-OIL-PURE",
        "title": "ANCHIALO Pure Dual Magnesium Oil 300ml | Unscented Black Sea Brine AU",
        "price_aud": "49.00",
        "qty": 25,
        "formulation": "Oil",
        "size": "300ml",
        "botanical": "100% Pure Unscented Black Sea Mineral Brine",
        "image_url": "https://anchialo.com/assets/images/products/08_file.jpg",
        "subtitle": "100% Pure Liquid Mineral Brine",
        "summary": "Unscented, concentrated liquid Black Sea mineral brine (luga) from Lake Pomorie. Silky natural glide for body massage or evening mineral foot soaks.",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE).",
    },
    {
        "sku": "ANCHIALO-COMBO-STARTER",
        "title": "ANCHIALO Dual Magnesium Gel 2-Pack 600g | Arnica + Lavender Day & Night",
        "price_aud": "89.00",
        "qty": 15,
        "formulation": "Gel",
        "size": "600g (2 x 300g)",
        "botanical": "Arnica Montana + Bulgarian Lavender",
        "image_url": "https://anchialo.com/assets/images/products/05_file.png",
        "subtitle": "Day & Night 2-Pack · Save $9 AUD",
        "summary": "Complete 600g cosmetic body care pair: Arnica Blend (300g) for post-training massage and Lavender Blend (300g) for your calming evening ritual.",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA / LAVANDULA ANGUSTIFOLIA.",
    },
    {
        "sku": "ANCHIALO-COMBO-VALUE",
        "title": "ANCHIALO Dual Magnesium Gel 3-Pack 900g | Arnica Lavender Rosemary AU",
        "price_aud": "129.00",
        "qty": 15,
        "formulation": "Gel",
        "size": "900g (3 x 300g)",
        "botanical": "Arnica + Lavender + Rosemary",
        "image_url": "https://anchialo.com/assets/images/products/09_file.png",
        "subtitle": "Best Value 3-Pack · Save $18 AUD",
        "summary": "Best value 900g cosmetic set featuring Arnica (300g), Lavender (300g), and Rosemary (300g) dual magnesium gels crafted under ISO 22716 GMP.",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, BOTANICAL EXTRACTS.",
    },
]


def is_ebay_configured() -> bool:
    """Return True when Production eBay App ID, Cert ID, and Refresh/User token are set."""
    app_id = (os.environ.get("EBAY_PRD_APP_ID") or "").strip()
    cert_id = (os.environ.get("EBAY_PRD_CERT_ID") or "").strip()
    refresh = (os.environ.get("EBAY_PRD_REFRESH_TOKEN") or "").strip()
    user_tok = (os.environ.get("EBAY_PRD_USER_TOKEN") or "").strip()
    return bool(app_id and cert_id and (refresh or user_tok))


async def get_ebay_access_token(force_refresh: bool = False) -> str:
    """Return a valid eBay Production User Access Token, refreshing automatically via refresh_token."""
    now = int(time.time())
    if not force_refresh and _TOKEN_CACHE["access_token"] and now < int(_TOKEN_CACHE["expires_at"]) - 120:
        return str(_TOKEN_CACHE["access_token"])

    app_id = (os.environ.get("EBAY_PRD_APP_ID") or "").strip()
    cert_id = (os.environ.get("EBAY_PRD_CERT_ID") or "").strip()
    refresh_token = (os.environ.get("EBAY_PRD_REFRESH_TOKEN") or "").strip()
    fallback_user_token = (os.environ.get("EBAY_PRD_USER_TOKEN") or "").strip()

    if not refresh_token:
        if fallback_user_token:
            _TOKEN_CACHE["access_token"] = fallback_user_token
            _TOKEN_CACHE["expires_at"] = now + 3600
            return fallback_user_token
        raise RuntimeError("EBAY_PRD_REFRESH_TOKEN is not configured")

    basic = base64.b64encode(f"{app_id}:{cert_id}".encode("ascii")).decode("ascii")
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            EBAY_OAUTH_URL,
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        if resp.status_code != 200:
            if fallback_user_token and not force_refresh:
                return fallback_user_token
            raise RuntimeError(f"eBay token refresh failed ({resp.status_code}): {resp.text[:300]}")
        payload = resp.json()
        token = str(payload.get("access_token") or "")
        expires_in = int(payload.get("expires_in") or 7200)
        _TOKEN_CACHE["access_token"] = token
        _TOKEN_CACHE["expires_at"] = now + expires_in
        os.environ["EBAY_PRD_USER_TOKEN"] = token
        return token


def _build_listing_html(item: dict[str, Any]) -> str:
    """Build clean, mobile-friendly, TGA-compliant HTML description for eBay AU."""
    return (
        "<div style=\"font-family:Arial,Helvetica,sans-serif;max-width:760px;margin:0 auto;color:#162820;line-height:1.6;\">"
        f"<h2 style=\"color:#1E3A2F;margin-bottom:6px;\">{escape(item['title'])}</h2>"
        f"<p style=\"color:#8F642B;font-weight:bold;margin-top:0;\">{escape(item['subtitle'])} · Stocked in Melbourne, VIC</p>"
        f"<p>{escape(item['summary'])}</p>"
        "<ul>"
        "<li><strong>Dual Mineral Complex:</strong> 253.14 g/L Magnesium Chloride + 70.36 g/L Magnesium Sulfate (Lake Pomorie Black Sea Lye)</li>"
        f"<li><strong>Botanical Profile:</strong> {escape(item['botanical'])}</li>"
        f"<li><strong>Net Content:</strong> {escape(item['size'])} · Manufactured under ISO 22716 GMP (EU)</li>"
        "<li><strong>Australian Dispatch:</strong> Fast shipping from Melbourne, VIC 3178 or free local pickup</li>"
        "</ul>"
        f"<p style=\"font-size:12px;color:#555;\"><strong>INCI:</strong> {escape(item['inci'])}</p>"
        "<p style=\"font-size:11px;color:#666;\">External cosmetic body care use only. Avoid contact with eyes or broken skin.</p>"
        "</div>"
    )


def _build_trading_item_xml(call_name: str, item: dict[str, Any], item_id: str | None = None) -> str:
    """Construct XML payload for AddFixedPriceItem, VerifyAddFixedPriceItem, or ReviseFixedPriceItem."""
    desc_html = _build_listing_html(item)
    item_id_xml = f"<ItemID>{escape(item_id)}</ItemID>" if item_id else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<{call_name}Request xmlns="{EBAY_NS}">
  <Item>
    {item_id_xml}
    <Title>{escape(item['title'][:80])}</Title>
    <SKU>{escape(item['sku'])}</SKU>
    <Description><![CDATA[{desc_html}]]></Description>
    <PrimaryCategory>
      <CategoryID>21205</CategoryID>
    </PrimaryCategory>
    <ConditionID>1000</ConditionID>
    <StartPrice currencyID="AUD">{escape(item['price_aud'])}</StartPrice>
    <CategoryMappingAllowed>true</CategoryMappingAllowed>
    <Country>AU</Country>
    <Currency>AUD</Currency>
    <DispatchTimeMax>2</DispatchTimeMax>
    <ListingDuration>GTC</ListingDuration>
    <ListingType>FixedPriceItem</ListingType>
    <Location>Rowville, VIC</Location>
    <PostalCode>3178</PostalCode>
    <Quantity>{int(item['qty'])}</Quantity>
    <Site>Australia</Site>
    <PictureDetails>
      <PictureURL>{escape(item['image_url'])}</PictureURL>
    </PictureDetails>
    <ItemSpecifics>
      <NameValueList><Name>Brand</Name><Value>ANCHIALO</Value></NameValueList>
      <NameValueList><Name>Type</Name><Value>Magnesium Body Care</Value></NameValueList>
      <NameValueList><Name>Formulation</Name><Value>{escape(item['formulation'])}</Value></NameValueList>
      <NameValueList><Name>Size</Name><Value>{escape(item['size'])}</Value></NameValueList>
      <NameValueList><Name>Body Area</Name><Value>Full Body</Value></NameValueList>
      <NameValueList><Name>Skin Type</Name><Value>All Skin Types</Value></NameValueList>
      <NameValueList><Name>Country/Region of Manufacture</Name><Value>Bulgaria</Value></NameValueList>
    </ItemSpecifics>
    <ReturnPolicy>
      <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
      <ReturnsWithinOption>Days_30</ReturnsWithinOption>
      <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
    </ReturnPolicy>
    <ShippingDetails>
      <ShippingType>Flat</ShippingType>
      <ShippingServiceOptions>
        <ShippingServicePriority>1</ShippingServicePriority>
        <ShippingService>AU_Regular</ShippingService>
        <ShippingServiceCost currencyID="AUD">0.00</ShippingServiceCost>
        <FreeShipping>true</FreeShipping>
      </ShippingServiceOptions>
      <ShippingServiceOptions>
        <ShippingServicePriority>2</ShippingServicePriority>
        <ShippingService>AU_Pickup</ShippingService>
        <ShippingServiceCost currencyID="AUD">0.00</ShippingServiceCost>
      </ShippingServiceOptions>
    </ShippingDetails>
  </Item>
</{call_name}Request>"""


async def _call_trading_api(call_name: str, xml_body: str, token: str) -> ET.Element:
    """Invoke eBay Trading API (SiteID 15 = EBAY_AU) with OAuth IAF token."""
    async with httpx.AsyncClient(timeout=25.0) as client:
        resp = await client.post(
            EBAY_TRADING_URL,
            headers={
                "X-EBAY-API-SITEID": "15",
                "X-EBAY-API-COMPATIBILITY-LEVEL": "1271",
                "X-EBAY-API-CALL-NAME": call_name,
                "X-EBAY-API-IAF-TOKEN": token,
                "Content-Type": "text/xml; charset=utf-8",
            },
            content=xml_body.encode("utf-8"),
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"eBay Trading API HTTP {resp.status_code}: {resp.text[:300]}")
        return ET.fromstring(resp.text)


def _xml_text(parent: ET.Element | None, path: str, default: str = "") -> str:
    if parent is None:
        return default
    ns = {"e": EBAY_NS}
    node = parent.find(path, ns)
    return (node.text or default).strip() if node is not None else default


def _parse_trading_errors(root: ET.Element) -> list[str]:
    ns = {"e": EBAY_NS}
    errs: list[str] = []
    for err in root.findall("e:Errors", ns):
        sev = _xml_text(err, "e:SeverityCode")
        code = _xml_text(err, "e:ErrorCode")
        msg = _xml_text(err, "e:LongMessage") or _xml_text(err, "e:ShortMessage")
        if sev == "Error":
            errs.append(f"[{code}] {msg}")
    return errs


async def fetch_active_listings(token: str) -> list[dict[str, Any]]:
    """Fetch active eBay AU fixed-price listings via GetMyeBaySelling."""
    xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
<GetMyeBaySellingRequest xmlns="{EBAY_NS}">
  <ActiveList>
    <Include>true</Include>
    <Pagination>
      <EntriesPerPage>50</EntriesPerPage>
      <PageNumber>1</PageNumber>
    </Pagination>
  </ActiveList>
</GetMyeBaySellingRequest>"""
    root = await _call_trading_api("GetMyeBaySelling", xml_req, token)
    ns = {"e": EBAY_NS}
    items: list[dict[str, Any]] = []
    for item in root.findall(".//e:ActiveList/e:ItemArray/e:Item", ns):
        items.append(
            {
                "item_id": _xml_text(item, "e:ItemID"),
                "sku": _xml_text(item, "e:SKU"),
                "title": _xml_text(item, "e:Title"),
                "price_aud": _xml_text(item, "e:SellingStatus/e:CurrentPrice"),
                "qty_sold": int(_xml_text(item, "e:SellingStatus/e:QuantitySold", "0") or 0),
                "qty_available": int(_xml_text(item, "e:QuantityAvailable", "0") or 0),
                "view_url": _xml_text(item, "e:ListingDetails/e:ViewItemURL"),
            }
        )
    return items


async def publish_or_revise_catalog(dry_run: bool = False) -> dict[str, Any]:
    """Publish or revise all ANCHIALO products on EBAY_AU without duplicating existing SKUs."""
    token = await get_ebay_access_token()
    active = await fetch_active_listings(token)
    by_sku = {it["sku"]: it["item_id"] for it in active if it.get("sku")}

    results: list[dict[str, Any]] = []
    created = 0
    revised = 0
    failed = 0

    for entry in EBAY_AU_CATALOG:
        existing_id = by_sku.get(entry["sku"])
        if dry_run:
            call_name = "VerifyAddFixedPriceItem"
            xml_body = _build_trading_item_xml(call_name, entry)
        elif existing_id:
            call_name = "ReviseFixedPriceItem"
            xml_body = _build_trading_item_xml(call_name, entry, item_id=existing_id)
        else:
            call_name = "AddFixedPriceItem"
            xml_body = _build_trading_item_xml(call_name, entry)

        root = await _call_trading_api(call_name, xml_body, token)
        ack = _xml_text(root, "e:Ack")
        errs = _parse_trading_errors(root)
        item_id = _xml_text(root, "e:ItemID") or existing_id or ""

        if ack in ("Success", "Warning") and not errs:
            if not dry_run:
                if existing_id:
                    revised += 1
                else:
                    created += 1
            results.append(
                {
                    "sku": entry["sku"],
                    "title": entry["title"],
                    "action": call_name,
                    "ack": ack,
                    "item_id": item_id,
                    "url": f"https://www.ebay.com.au/itm/{item_id}" if item_id else "",
                }
            )
        else:
            failed += 1
            results.append(
                {
                    "sku": entry["sku"],
                    "title": entry["title"],
                    "action": call_name,
                    "ack": ack,
                    "errors": errs,
                }
            )

    _SUMMARY_CACHE["fetched_at"] = 0
    return {
        "dry_run": dry_run,
        "created": created,
        "revised": revised,
        "failed": failed,
        "results": results,
    }


def _is_anchialo_item(sku: str, title: str) -> bool:
    """Return True only for official ANCHIALO eBay AU SKUs/listings, excluding pre-existing seller items."""
    sku_norm = (sku or "").strip().upper()
    title_norm = (title or "").strip().lower()
    return sku_norm.startswith("ANCHIALO-") or "anchialo" in title_norm


def _is_anchialo_order(order: dict[str, Any]) -> bool:
    """Return True if at least one line item in an eBay order belongs to the ANCHIALO catalog."""
    return any(
        _is_anchialo_item(str(li.get("sku") or ""), str(li.get("title") or ""))
        for li in (order.get("lineItems") or [])
    )


def _sync_orders_into_sqlite(orders: list[dict[str, Any]], db_path: str | None = None) -> int:
    """Idempotently persist real ANCHIALO eBay AU orders into the local SQLite orders table."""
    inserted = 0
    with get_conn(db_path) as conn:
        for order in orders:
            if not _is_anchialo_order(order):
                continue
            order_id = str(order.get("orderId") or "").strip()
            if not order_id:
                continue
            ext_id = f"ebay_{order_id}"
            total_val = float(((order.get("pricingSummary") or {}).get("total") or {}).get("value") or 0.0)
            total_cents = int(round(total_val * 100))
            buyer = ((order.get("buyer") or {}).get("username") or "eBay AU Buyer")
            items = [
                {
                    "id": li.get("sku") or li.get("legacyItemId") or "ebay-item",
                    "name": li.get("title") or "eBay Item",
                    "qty": int(li.get("quantity") or 1),
                    "unit_cents": int(round(float(((li.get("lineItemCost") or {}).get("value") or 0.0)) * 100)),
                }
                for li in (order.get("lineItems") or [])
            ]
            import json

            cur = conn.execute(
                """
                INSERT OR IGNORE INTO orders (
                    provider, external_tx_id, customer_email, customer_name,
                    subtotal_cents, discount_cents, shipping_cents, total_cents,
                    partner_code, promo_code, items_json, locality_json, status, created_at
                ) VALUES ('ebay_au', ?, '', ?, ?, 0, 0, ?, NULL, NULL, ?, '{"country":"AU","channel":"ebay_au"}', ?, ?)
                """,
                (
                    ext_id,
                    str(buyer)[:120],
                    total_cents,
                    total_cents,
                    json.dumps(items),
                    str(order.get("orderFulfillmentStatus") or "paid").lower(),
                    int(time.time()),
                ),
            )
            if cur.rowcount:
                inserted += 1
    return inserted


async def get_ebay_summary(force: bool = False) -> dict[str, Any]:
    """Return live EBAY_AU account privilege, active listings, and fulfillment orders (60s cache)."""
    if not is_ebay_configured():
        return {"configured": False, "status": "AWAITING_TOKEN"}

    now = int(time.time())
    if not force and _SUMMARY_CACHE["data"] and now - int(_SUMMARY_CACHE["fetched_at"]) < 60:
        return dict(_SUMMARY_CACHE["data"])

    try:
        token = await get_ebay_access_token()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=20.0) as client:
            priv_resp, ord_resp = await asyncio.gather(
                client.get(EBAY_SELL_PRIVILEGE_URL, headers=headers),
                client.get(f"{EBAY_SELL_ORDERS_URL}?limit=20", headers=headers),
            )

        if priv_resp.status_code == 401 or ord_resp.status_code == 401:
            token = await get_ebay_access_token(force_refresh=True)
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            async with httpx.AsyncClient(timeout=20.0) as client:
                priv_resp, ord_resp = await asyncio.gather(
                    client.get(EBAY_SELL_PRIVILEGE_URL, headers=headers),
                    client.get(f"{EBAY_SELL_ORDERS_URL}?limit=20", headers=headers),
                )

        priv_json = priv_resp.json() if priv_resp.status_code == 200 else {}
        ord_json = ord_resp.json() if ord_resp.status_code == 200 else {}
        all_orders = ord_json.get("orders") or []
        orders = [o for o in all_orders if _is_anchialo_order(o)]
        _sync_orders_into_sqlite(orders)
        all_active_listings = await fetch_active_listings(token)
        active_listings = [
            it for it in all_active_listings if _is_anchialo_item(str(it.get("sku") or ""), str(it.get("title") or ""))
        ]

        orders_to_ship = sum(
            1 for o in orders if str(o.get("orderFulfillmentStatus") or "") in ("NOT_STARTED", "IN_PROGRESS")
        )
        revenue_aud = round(
            sum(float(((o.get("pricingSummary") or {}).get("total") or {}).get("value") or 0.0) for o in orders),
            2,
        )
        limit_obj = (priv_json.get("sellingLimit") or {}).get("amount") or {}

        summary = {
            "configured": True,
            "status": "LIVE_EBAY_AU",
            "selling_limit_aud": float(limit_obj.get("value") or 0.0),
            "selling_limit_qty": int((priv_json.get("sellingLimit") or {}).get("quantity") or 0),
            "active_listings_count": len(active_listings),
            "active_listings": active_listings[:15],
            "orders_total": len(orders),
            "orders_to_ship": orders_to_ship,
            "revenue_aud": revenue_aud,
            "recent_orders": [
                {
                    "order_id": o.get("orderId"),
                    "created": o.get("creationDate"),
                    "status": o.get("orderFulfillmentStatus"),
                    "total_aud": float(((o.get("pricingSummary") or {}).get("total") or {}).get("value") or 0.0),
                    "items": [li.get("title") for li in (o.get("lineItems") or [])],
                }
                for o in orders[:8]
            ],
        }
        _SUMMARY_CACHE["data"] = summary
        _SUMMARY_CACHE["fetched_at"] = now
        return summary
    except Exception as exc:
        logger.warning("eBay summary fetch failed: %s", exc)
        return {"configured": True, "status": "ERROR", "error": str(exc)}
