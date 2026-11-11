"""Automated TGA/ACCC compliance, cart fix, JSON-LD, and SEO integrity audit for anchialo-com."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Prohibited therapeutic / disease terms under Australian TGA advertising rules
PROHIBITED_TGA_PATTERNS = [
    re.compile(r"\barthritis\b", re.IGNORECASE),
    re.compile(r"\barthritic\b", re.IGNORECASE),
    re.compile(r"\barthrosis\b", re.IGNORECASE),
    re.compile(r"\bfibromyalgia\b", re.IGNORECASE),
    re.compile(r"\bdisc hernia\b", re.IGNORECASE),
    re.compile(r"\bdiscopathy\b", re.IGNORECASE),
    re.compile(r"\bneuritis\b", re.IGNORECASE),
    re.compile(r"\bneuralgia\b", re.IGNORECASE),
    re.compile(r"\bplexitis\b", re.IGNORECASE),
    re.compile(r"\brestless leg(s| syndrome)?\b", re.IGNORECASE),
    re.compile(r"\bjoint inflammation\b", re.IGNORECASE),
    re.compile(r"\binflamed joint\b", re.IGNORECASE),
    re.compile(r"\banti-inflammatory\b", re.IGNORECASE),
    re.compile(r"\bsprains\b", re.IGNORECASE),
    re.compile(r"\bfractures\b", re.IGNORECASE),
    re.compile(r"\beczema\b", re.IGNORECASE),
    re.compile(r"\bpsoriasis\b", re.IGNORECASE),
    re.compile(r"\bhemorrhoids\b", re.IGNORECASE),
    re.compile(r"\bdiarrhea\b", re.IGNORECASE),
    re.compile(r"\bpainkiller(s)?\b", re.IGNORECASE),
    re.compile(r"\bopiate\b", re.IGNORECASE),
    re.compile(r"\bpain relief\b", re.IGNORECASE),
    re.compile(r"\bchronic pain\b", re.IGNORECASE),
    re.compile(r"\bjoint pain\b", re.IGNORECASE),
    re.compile(r"\bnerve pain\b", re.IGNORECASE),
    re.compile(r"\btherapeutic action\b", re.IGNORECASE),
    re.compile(r"\btherapeutic indications\b", re.IGNORECASE),
]


def scan_text_for_tga(label: str, text: str, errors: list[str]) -> None:
    """Assert zero matches for prohibited TGA terms."""
    for pat in PROHIBITED_TGA_PATTERNS:
        if pat.search(text):
            errors.append(f"TGA violation in {label}: matched {pat.pattern}")


def verify_all() -> None:
    """Execute complete static compliance, schema, cart, and sitemap checks."""
    errors: list[str] = []

    # 1. Core files: index.html, app.js, data/blog_posts.json
    index_text = (ROOT / "index.html").read_text(encoding="utf-8")
    app_text = (ROOT / "app.js").read_text(encoding="utf-8")
    posts_data = json.loads((ROOT / "data" / "blog_posts.json").read_text(encoding="utf-8"))

    scan_text_for_tga("index.html", index_text, errors)
    scan_text_for_tga("app.js", app_text, errors)
    for idx, post in enumerate(posts_data):
        for field in ("url", "slug", "title", "headline", "description", "body_text"):
            scan_text_for_tga(f"data/blog_posts.json[{idx}].{field}", str(post.get(field, "")), errors)

    # Check ACCC unverified review count removed
    if "420+ Australian wellness" in index_text or '"ratingCount": "420"' in index_text:
        errors.append("ACCC violation: unverified 420 review rating still in index.html")

    # Check cart fixes & ATO/GST default
    if "subtotalAUD === 125" in app_text or "subtotalAUD === 245" in app_text:
        errors.append("Cart bug: obsolete subtotalAUD === 125/245 checks remain in app.js")
    if "gstRegistered: false" not in app_text:
        errors.append("ATO safety: MERCHANT_CONFIG.gstRegistered default must be false")
    if 'id="ritualQuizContainer"' not in index_text:
        errors.append("Missing 30s Ritual Quiz container in index.html")
    if 'id="bagUpsellSlot"' not in index_text or 'id="bagSaveEmailInput"' not in index_text:
        errors.append("Missing Bag Upsell or Save Bag email capture in index.html")

    # Validate index.html JSON-LD
    ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', index_text, re.DOTALL)
    if not ld_matches:
        errors.append("Missing JSON-LD in index.html")
    else:
        for block in ld_matches:
            json.loads(block)

    # 2. Scan generated product pages, blog posts, and Melbourne pages
    product_htmls = list((ROOT / "product-page").glob("*.html"))
    post_htmls = list((ROOT / "post").glob("*.html"))
    melbourne_htmls = list((ROOT / "melbourne").glob("*.html"))

    if len(product_htmls) < 9:
        errors.append(f"Expected >= 9 product HTML files, found {len(product_htmls)}")
    if len(post_htmls) < 16:
        errors.append(f"Expected >= 16 blog HTML files, found {len(post_htmls)}")
    if len(melbourne_htmls) < 100:
        errors.append(f"Expected >= 100 Melbourne SEO pages, found {len(melbourne_htmls)}")

    for path in product_htmls + post_htmls + melbourne_htmls:
        content = path.read_text(encoding="utf-8")
        if 'meta name="robots" content="noindex, follow"' in content:
            continue  # Redirect stub for legacy URL
        scan_text_for_tga(str(path.relative_to(ROOT)), content, errors)
        if '"ratingCount": "420"' in content:
            errors.append(f"ACCC 420 review count found in {path.relative_to(ROOT)}")
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL):
            json.loads(block)

    # 3. Validate sitemap.xml completeness and uniqueness
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = [el.text for el in tree.getroot().findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if el.text]
    if len(locs) != len(set(locs)):
        errors.append("Duplicate URLs found in sitemap.xml")
    if len(locs) < 130:
        errors.append(f"Expected >= 130 URLs in sitemap.xml, found {len(locs)}")

    if errors:
        raise AssertionError("\n".join(errors))

    print(
        f"PASS: 0 TGA/ACCC issues | index.html + app.js + {len(product_htmls)} product pages + "
        f"{len(post_htmls)} blog files + {len(melbourne_htmls)} Melbourne pages + {len(locs)} sitemap URLs verified."
    )


if __name__ == "__main__":
    verify_all()
