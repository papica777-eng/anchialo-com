import glob
import html
import json
import os
import re
import urllib.parse

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DATE = "2026-11-14"

VERIFIED_REVIEWS = [
    {
        "author": "Connor Evans",
        "context": "Heavy Training Routine",
        "blend": "Arnica Blend · 300g",
        "datePublished": "2025-09-14",
        "rating": 5,
        "quote": "I've been using this gel after heavy training blocks for post-workout body care. It feels great brushed into tired muscles and helps ease everyday post-session tightness. Would definitely recommend it.",
    },
    {
        "author": "Earthstone Chu",
        "context": "Martial Arts & Combat Sports",
        "blend": "Rosemary Blend · 300g",
        "datePublished": "2025-10-03",
        "rating": 5,
        "quote": "After demanding martial arts sessions my legs and knees really welcome a slow massage with Anchialo Black Sea lye gel. It's become a reliable companion in my training bag.",
    },
    {
        "author": "Anh Hoang",
        "context": "Hospitality & Long Shifts",
        "blend": "Dual Magnesium Gel · 300g",
        "datePublished": "2025-11-18",
        "rating": 5,
        "quote": "Working in a busy restaurant, my arms and shoulders get heavy from lifting all shift. Massaging a small amount of this gel leaves them feeling refreshed — a little goes a long way and I'm buying another jar soon.",
    },
    {
        "author": "Rhonda Wood",
        "context": "Daily Hands & Wrist Care",
        "blend": "Lavender Blend · 300g",
        "datePublished": "2025-12-09",
        "rating": 5,
        "quote": "I had tried many body creams before discovering Anchialo online. Massaging this gel over my tired wrists and hands feels wonderfully soothing, smells lovely, and offers genuine value.",
    },
    {
        "author": "Cordis Pristis",
        "context": "Active Mobility Routine",
        "blend": "Juniper Blend · 300g",
        "datePublished": "2026-01-22",
        "rating": 5,
        "quote": "I admit I was skeptical at first, yet consistent evening massage applications made overworked muscles and joints feel noticeably looser and more comfortable. Glad I tried it.",
    },
    {
        "author": "Tsveti Todorova",
        "context": "Evening Leg & Home Spa Ritual",
        "blend": "Grape Blend · 300g",
        "datePublished": "2026-02-17",
        "rating": 5,
        "quote": "My daughter and I use Anchialo Black Sea magnesium gel for a cooling evening massage on tired legs after standing all day — we love the silky mineral feel and light botanical scent.",
    },
]


def build_aggregate_rating_schema():
    """Return consistent AggregateRating JSON-LD block grounded in verified customer reviews."""
    return {
        "@type": "AggregateRating",
        "ratingValue": "5.0",
        "bestRating": "5",
        "worstRating": "1",
        "ratingCount": len(VERIFIED_REVIEWS),
        "reviewCount": len(VERIFIED_REVIEWS),
    }


def build_reviews_schema(limit=None):
    """Return Schema.org Review array matching on-page customer testimonials."""
    items = VERIFIED_REVIEWS[:limit] if limit else VERIFIED_REVIEWS
    return [
        {
            "@type": "Review",
            "author": {"@type": "Person", "name": r["author"]},
            "datePublished": r["datePublished"],
            "name": f"{r['context']} — {r['blend']}",
            "reviewBody": r["quote"],
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": r["rating"],
                "bestRating": 5,
                "worstRating": 1,
            },
        }
        for r in items
    ]


def build_verified_reviews_cards_html(limit=None):
    """Render semantic verified-customer feedback cards shared across home and product pages."""
    items = VERIFIED_REVIEWS[:limit] if limit else VERIFIED_REVIEWS
    cards = []
    for r in items:
        stars = "★" * r["rating"]
        cards.append(
            f"""          <article class="review-card">
            <div class="review-card-top">
              <span class="review-stars" aria-label="{r['rating']} out of 5 stars">{stars}</span>
              <span class="review-verified-pill">Verified Buyer</span>
            </div>
            <blockquote class="review-quote">“{html.escape(r['quote'])}”</blockquote>
            <div class="review-footer">
              <strong class="review-author">{html.escape(r['author'])}</strong>
              <span class="review-meta">{html.escape(r['context'])} · {html.escape(r['blend'])}</span>
            </div>
          </article>"""
        )
    return "\n".join(cards)


def _trim_light_border(im, threshold=245):
    """Crop pure-white margins around extracted quadrant panels or circular seals."""
    gray = im.convert("L")
    mask = gray.point(lambda p: 255 if p < threshold else 0)
    bbox = mask.getbbox()
    return im.crop(bbox) if bbox else im


def _save_cropped_webp(im, out_path, max_width=1200, quality=88, sharpen=True):
    """Resize down if wider than max_width, apply subtle unsharp mask, and write WebP."""
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGB")
    if max_width and im.width > max_width:
        new_h = max(1, int(im.height * (max_width / float(im.width))))
        im = im.resize((max_width, new_h), Image.Resampling.LANCZOS)
    if sharpen:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=85, threshold=2))
    im.save(out_path, "WEBP", quality=quality, method=6)


def _extract_print_and_archival_assets():
    """Extract crisp WebP storytelling & craft panels from high-res flyer, label, and print PDF assets."""
    web_dir = os.path.join(ROOT, "assets", "images", "web")
    os.makedirs(web_dir, exist_ok=True)

    # 1. Aerial Pomorie sandbar + crimson salterns from mma-slide-3.jpg
    sandbar_out = os.path.join(web_dir, "pomorie-sandbar-drone.webp")
    flyer_src = os.path.join(ROOT, "assets", "flyers-gallery", "mma-slide-3.jpg")
    if os.path.exists(flyer_src) and (
        not os.path.exists(sandbar_out) or os.path.getmtime(sandbar_out) < os.path.getmtime(flyer_src)
    ):
        with Image.open(flyer_src) as im:
            w, h = im.size
            crop = im.crop((0, int(h * 0.358), int(w * 0.494), int(h * 0.662)))
            crop = _trim_light_border(crop, threshold=244)
            _save_cropped_webp(crop, sandbar_out, max_width=1100, quality=89)

    # 2. 1930s Anchialo vintage emblem from official high-res label sheet
    emblem_out = os.path.join(web_dir, "anchialo-vintage-1930s-emblem.webp")
    label_src = os.path.join(ROOT, "labels", "folder_3", "Anhialo_Massage_Gel_p1.png")
    if os.path.exists(label_src) and (
        not os.path.exists(emblem_out) or os.path.getmtime(emblem_out) < os.path.getmtime(label_src)
    ):
        with Image.open(label_src) as im:
            w, h = im.size
            crop = im.crop((int(w * 0.520), int(h * 0.675), w, h))
            crop = _trim_light_border(crop, threshold=240)
            _save_cropped_webp(crop, emblem_out, max_width=900, quality=90)

    # 3. Clean studio & Pomorie immersion photos from ANCHIALO-Black-Sea-Lye-Magnesium-Gel-Print.pdf
    pdf_targets = [
        ("pomorie-lye-floating.webp", 2, (0.0, 0.542, 0.495, 1.0), True),
        ("anchialo-amber-gel-scoop.webp", 5, (0.0, 0.0, 0.497, 1.0), False),
        ("anchialo-leg-massage-ritual.webp", 6, (0.498, 0.0, 1.0, 1.0), False),
    ]
    missing_or_stale = any(
        not os.path.exists(os.path.join(web_dir, fname))
        for fname, *_ in pdf_targets
    )
    pdf_candidates = [
        os.path.join(os.path.expanduser("~"), "Downloads", "ANCHIALO-Black-Sea-Lye-Magnesium-Gel-Print.pdf"),
        os.path.join(ROOT, "assets", "official_drive_assets", "ANCHIALO-Black-Sea-Lye-Magnesium-Gel-Print.pdf"),
    ]
    pdf_path = next((p for p in pdf_candidates if os.path.exists(p)), None)
    if pdf_path and missing_or_stale:
        try:
            import fitz
        except ImportError:
            fitz = None
        if fitz is not None:
            doc = fitz.open(pdf_path)
            matrix = fitz.Matrix(2.2, 2.2)
            for fname, page_idx, (x0, y0, x1, y1), trim in pdf_targets:
                out_path = os.path.join(web_dir, fname)
                if os.path.exists(out_path) and os.path.getmtime(out_path) >= os.path.getmtime(pdf_path):
                    continue
                if page_idx >= len(doc):
                    continue
                pix = doc[page_idx].get_pixmap(matrix=matrix, alpha=False)
                im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                w, h = im.size
                crop = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
                if trim:
                    crop = _trim_light_border(crop, threshold=245)
                _save_cropped_webp(crop, out_path, max_width=1100, quality=88)
            doc.close()


def _convert_dir_to_webp(src_dir, dst_dir, patterns, max_width=1000, quality=84, min_width=None, sharpen=False):
    """Idempotently convert heavy PNG/JPG/WebP assets to lightweight WebP files."""
    if not os.path.isdir(src_dir):
        return
    os.makedirs(dst_dir, exist_ok=True)
    for pat in patterns:
        for src_path in sorted(glob.glob(os.path.join(src_dir, pat))):
            stem = os.path.splitext(os.path.basename(src_path))[0]
            out_path = os.path.join(dst_dir, f"{stem}.webp")
            if os.path.exists(out_path) and os.path.getmtime(out_path) >= os.path.getmtime(src_path):
                continue
            with Image.open(src_path) as im:
                if im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
                if min_width and im.width < min_width:
                    new_h = max(1, int(im.height * (min_width / float(im.width))))
                    im = im.resize((min_width, new_h), Image.Resampling.LANCZOS)
                elif max_width and im.width > max_width:
                    new_h = max(1, int(im.height * (max_width / float(im.width))))
                    im = im.resize((max_width, new_h), Image.Resampling.LANCZOS)
                if sharpen:
                    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=95, threshold=2))
                im.save(out_path, "WEBP", quality=quality, method=6)


def optimize_web_assets():
    """Ensure lightweight WebP derivatives exist for hero, heritage, blog, labels, and flyer assets."""
    _convert_dir_to_webp(
        os.path.join(ROOT, "assets", "images"),
        os.path.join(ROOT, "assets", "images", "web"),
        ("pomorie-lye-harvest.jpg",),
        max_width=1440,
        quality=94,
    )
    _convert_dir_to_webp(
        os.path.join(ROOT, "assets", "images"),
        os.path.join(ROOT, "assets", "images", "web"),
        ("pomorie-salterns-lake.jpg",),
        max_width=1920,
        min_width=1920,
        quality=95,
        sharpen=True,
    )
    _convert_dir_to_webp(
        os.path.join(ROOT, "assets", "images"),
        os.path.join(ROOT, "assets", "images", "web"),
        ("pomorie-salterns-sunset.jpg",),
        max_width=2048,
        min_width=2048,
        quality=95,
        sharpen=True,
    )
    _convert_dir_to_webp(
        os.path.join(ROOT, "assets", "images", "blog"),
        os.path.join(ROOT, "assets", "images", "blog", "web"),
        ("*.png", "*.jpg", "*.jpeg", "*.webp"),
        max_width=1000,
        quality=82,
    )
    _convert_dir_to_webp(
        os.path.join(ROOT, "assets", "official_labels_rendered"),
        os.path.join(ROOT, "assets", "official_labels_rendered", "web"),
        ("*.png",),
        max_width=1100,
        quality=85,
    )
    _convert_dir_to_webp(
        os.path.join(ROOT, "assets", "flyers-gallery"),
        os.path.join(ROOT, "assets", "flyers-gallery", "web"),
        ("*.jpg", "*.jpeg", "*.png"),
        max_width=1000,
        quality=82,
    )
    _extract_print_and_archival_assets()


def resolve_product_web_image(rel_path):
    """Map product PNG/JPG asset path to its compressed web/*.webp twin if present."""
    norm = rel_path.replace("\\", "/").lstrip("/")
    fname = os.path.splitext(os.path.basename(norm))[0] + ".webp"
    cand = os.path.join(ROOT, "assets", "images", "products", "web", fname)
    if os.path.exists(cand):
        return f"assets/images/products/web/{fname}"
    return norm


def resolve_blog_local_image(url_or_path, index_hint=0):
    """Map legacy wixstatic media URLs or blog asset paths to local WebP derivatives."""
    web_dir = os.path.join(ROOT, "assets", "images", "blog", "web")
    available = sorted(os.listdir(web_dir)) if os.path.isdir(web_dir) else []
    raw = (url_or_path or "").strip()
    m = re.search(r"([0-9a-f]+_[0-9a-f]+~mv2)", raw, re.IGNORECASE)
    if m and available:
        needle = m.group(1).replace("~", "_")
        for fn in available:
            if needle in fn:
                return f"assets/images/blog/web/{fn}"
    if "assets/images/blog/" in raw:
        stem = os.path.splitext(os.path.basename(raw))[0]
        if f"{stem}.webp" in available:
            return f"assets/images/blog/web/{stem}.webp"
    if available and 0 <= index_hint < len(available):
        return f"assets/images/blog/web/{available[index_hint]}"
    return "assets/images/products/web/06_file_transp.webp"

PRODUCTS = [
    {
        "id": "gel-arnica",
        "slug": "anchialo-dual-magnesium-gel-arnica-blend",
        "sku": "ANCH-GEL-ARN-300",
        "gtin13": "3800230111746",
        "name": "Dual Magnesium Gel | Arnica Blend",
        "title": "Anchialo Dual Magnesium Gel — Arnica Montana Blend (300g) | $49 AUD",
        "category": "gel",
        "priceAUD": "49.00",
        "unitLabel": "/ 300g Net",
        "image": "assets/images/products/06_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_arnica_top_fv17.png",
        "badge": "Bestseller · Post-Training Ritual",
        "stripe": "https://buy.stripe.com/9B67sL4tmfBa9CD0eb5Ne0e",
        "botanical": "Arnica Montana Flower Extract",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA FLOWER EXTRACT.",
        "description": "Fast-absorbing topical gel with 253.14 g/L Black Sea magnesium chloride, 70.36 g/L magnesium sulfate, and Arnica Montana extract to hydrate skin and refresh tired muscles. 300g net. Dispatched from Melbourne, Australia.",
        "benefits": [
            "Fast-absorbing topical body gel formulated to relax and nourish the skin after intense sessions",
            "253.14 g/L Magnesium Chloride & 70.36 g/L Magnesium Sulfate from Lake Pomorie, Bulgaria",
            "Enriched with Arnica Montana extract, traditionally used to soothe and comfort the body",
            "Certified zero heavy metals (BDS 8840:1971 & ISO 22716 GMP · Lot 04)"
        ]
    },
    {
        "id": "gel-lavender",
        "slug": "anchialo-dual-magnesium-gel-lavander-blend",
        "alias_slug": "anchialo-dual-magnesium-gel-lavender-blend",
        "sku": "ANCH-GEL-LAV-300",
        "gtin13": "3800230111746",
        "name": "Dual Magnesium Gel | Lavender Blend",
        "title": "Anchialo Dual Magnesium Gel — Bulgarian Lavender Blend (300g) | $49 AUD",
        "category": "gel",
        "priceAUD": "49.00",
        "unitLabel": "/ 300g Net",
        "image": "assets/images/products/01_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_lavender_top_fv17.png",
        "badge": "Evening Calm & Wind-Down",
        "stripe": "https://buy.stripe.com/cNi14ncZS9cMeWX9OL5Ne0d",
        "botanical": "Lavandula Angustifolia Essential Flower Extract",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT.",
        "description": "Infused with authentic Bulgarian Lavender flower extract and Lake Pomorie Dual Magnesium (253.14 g/L MgCl2) to nourish dry skin and support a calming evening massage ritual. 300g net.",
        "benefits": [
            "Formulated with Lavender extract, valued for its calming and relaxing aroma before rest",
            "Combines concentrated Black Sea magnesium salts with skin-hydrating glycerine",
            "Non-drip smooth gel texture ideal for calves, shoulders, and evening wind-down routines",
            "Gentle physiological pH 6.9 — zero parabens, zero synthetic perfumes"
        ]
    },
    {
        "id": "gel-rosemary",
        "slug": "anchialo-dual-magnesium-gel-rosemary-blend",
        "sku": "ANCH-GEL-ROS-300",
        "gtin13": "3800230111746",
        "name": "Dual Magnesium Gel | Rosemary Blend",
        "title": "Anchialo Dual Magnesium Gel — Garden Rosemary Blend (300g) | $49 AUD",
        "category": "gel",
        "priceAUD": "49.00",
        "unitLabel": "/ 300g Net",
        "image": "assets/images/products/04_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_rosemary_top_fv17.png",
        "badge": "Invigorating Massage",
        "stripe": "https://buy.stripe.com/8x2dR9cZSbkUdST5yv5Ne0f",
        "botanical": "Rosmarinus Officinalis Leaf Powder Extract",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ROSMARINUS OFFICINALIS LEAF POWDER EXTRACT.",
        "description": "Enhanced with Garden Rosemary extract traditionally used to invigorate skin during massage. Paired with 253.14 g/L Black Sea Magnesium Chloride for active athletes and daily body care. 300g net.",
        "benefits": [
            "Invigorating herbal massage experience before training or after heavy workouts",
            "Supports skin hydration and contributes to a feeling of refreshment and revitalisation",
            "High magnesium content helps nourish skin across shoulders, lower back, and legs",
            "Non-greasy leave-on or rinse-off cosmetic gel texture"
        ]
    },
    {
        "id": "gel-juniper",
        "slug": "anchialo-dual-magnesium-gel-juniper-blend",
        "sku": "ANCH-GEL-JUN-300",
        "gtin13": "3800230111746",
        "name": "Dual Magnesium Gel | Juniper Blend",
        "title": "Anchialo Dual Magnesium Gel — Alpine Juniper Blend (300g) | $49 AUD",
        "category": "gel",
        "priceAUD": "49.00",
        "unitLabel": "/ 300g Net",
        "image": "assets/images/products/07_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_juniper_top_fv17.png",
        "badge": "Crisp Refresh & Sauna Ritual",
        "stripe": "https://buy.stripe.com/14A3cv7Fy4Ww5mne515Ne0g",
        "botanical": "Juniperus Chinensis Leaf Extract & Fruit Oil",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE, JUNIPERUS CHINENSIS LEAF EXTRACT.",
        "description": "Alpine Juniper botanical blend crafted to hydrate skin and refresh weary legs, shoulders, and feet after showers, contrast therapy, or long shifts. 300g net.",
        "benefits": [
            "Infused with Juniper extract, valued for its crisp, refreshing and revitalising qualities",
            "Ideal post-sauna, post-shower, and after-work lower-body massage gel",
            "High-density Pomorie mineral brine (253.14 g/L MgCl2 + 70.36 g/L MgSO4)",
            "Handcrafted by Azimut 6000 Ltd under ISO 22716 GMP standards"
        ]
    },
    {
        "id": "gel-grape",
        "slug": "anchialo-dual-magnesium-gel-grape-blend",
        "sku": "ANCH-GEL-GRP-300",
        "gtin13": "3800230111746",
        "name": "Dual Magnesium Gel | Grape Blend",
        "title": "Anchialo Dual Magnesium Gel — Red Grape Seed Blend (300g) | $49 AUD",
        "category": "gel",
        "priceAUD": "49.00",
        "unitLabel": "/ 300g Net",
        "image": "assets/images/products/03_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_grape_top_fv17.png",
        "badge": "Skin Softness & Daily Care",
        "stripe": "https://buy.stripe.com/cNidR97FycoY0239OL5Ne0h",
        "botanical": "Vitis Vinifera (Grape) Seed Polyphenol Extract",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE.",
        "description": "Lightly fragranced with a subtle vineyard grape aroma alongside pure Lake Pomorie dual magnesium salts to condition skin and leave a smooth, velvet finish. 300g net.",
        "benefits": [
            "Helps maintain soft, hydrated skin and overall body refreshment",
            "Pleasant light grape fragrance ideal for everyday massage and evening routines",
            "Non-greasy finish — absorbs cleanly or rinses smoothly with cool water",
            "100% natural Black Sea solar-evaporated lye base"
        ]
    },
    {
        "id": "oil-pure",
        "slug": "anchialo-dual-magnesium-oil-natural-topical-oil",
        "sku": "ANCH-OIL-PUR-300",
        "gtin13": "3800230111746",
        "name": "Dual Magnesium Oil | Natural Topical Brine",
        "title": "Anchialo Dual Magnesium Oil — 100% Pure Black Sea Topical Brine (300ml) | $49 AUD",
        "category": "oil",
        "priceAUD": "49.00",
        "unitLabel": "/ 300ml Net",
        "image": "assets/images/products/08_file_transp.png",
        "lidImg": "assets/images/products/08_file_transp.png",
        "badge": "100% Pure Liquid Brine",
        "stripe": "https://buy.stripe.com/aFaeVdgc4ex6cOP1if5Ne0i",
        "botanical": "100% Unscented Natural Lake Pomorie Mineral Brine (Luga)",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM CHLORIDE 253.14 g/L, MAGNESIUM SULFATE 70.36 g/L, SODIUM CHLORIDE, TRACE BROMINE & IODINE).",
        "description": "Unscented, concentrated liquid Black Sea mineral brine (luga). Silky natural glide tailored for full-body studio massage or evening mineral foot soaks. 300ml.",
        "benefits": [
            "100% pure unfragranced fractional solar brine from Lake Pomorie",
            "High mineral density ideal for remedial massage glide, wraps, and warm foot baths",
            "Zero added synthetic fragrance, preservatives, or petroleum oils",
            "Certified under BDS 8840:1971 & ATA Translation #267262"
        ]
    },
    {
        "id": "combo-gel-oil",
        "slug": "special-offer-gel-oil-combo",
        "sku": "ANCH-CMB-GELOIL",
        "gtin13": "3800230111746",
        "name": "Special Offer | Gel + Oil Combo",
        "title": "Anchialo Special Offer — Dual Magnesium Gel + Pure Magnesium Oil Combo | $49 AUD",
        "category": "combo",
        "priceAUD": "49.00",
        "unitLabel": "/ 300g + 300ml",
        "image": "assets/images/products/02_file.png",
        "lidImg": "assets/images/products/02_file.png",
        "badge": "1+1 Free Value Deal",
        "stripe": "https://buy.stripe.com/4gM28rgc44WwbKL3qn5Ne0l",
        "botanical": "Choice of Signature Botanical Gel (300g) + Pure Magnesium Brine Oil (300ml)",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, BOTANICAL EXTRACT.",
        "description": "Buy 1 Dual Magnesium Gel (300g) and receive 1 Pure Dual Magnesium Oil (300ml) FREE. Complete topical gel and bath/massage brine set for the price of one item ($49 AUD).",
        "benefits": [
            "Includes 1x 300g Dual Magnesium Botanical Gel + 1x 300ml Pure Magnesium Oil",
            "Complete ritual set: targeted gel massage + full-body or foot-soak liquid brine",
            "Dispatched directly from Melbourne via Australia Post with tracking",
            "Same-day local pickup available at CPT MMA Melbourne"
        ]
    },
    {
        "id": "combo-starter",
        "slug": "starter-combo-dual-magnesium-gel",
        "sku": "ANCH-CMB-START2",
        "gtin13": "3800230111746",
        "name": "Starter Combo | Dual Magnesium Gel (2-Pack)",
        "title": "Anchialo Starter Combo — Dual Magnesium Gel 2-Pack (600g Total) | $89 AUD + Free Shipping",
        "category": "combo",
        "priceAUD": "89.00",
        "unitLabel": "/ 600g (2 × 300g)",
        "image": "assets/images/products/05_file.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_arnica_top_fv17.png",
        "badge": "Save $9 · Day & Night Pair",
        "stripe": "https://buy.stripe.com/6oU4gzcZS60AeWX9OL5Ne0j",
        "botanical": "Any 2 Signature Botanical Blends (e.g., Arnica Day Ritual + Lavender Night Wind-Down)",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, BOTANICAL EXTRACTS.",
        "description": "Pair Arnica for daytime post-training massage with Bulgarian Lavender for your calm evening wind-down ritual. Total 600g pure Pomorie magnesium gels with FREE Australia-wide Express shipping.",
        "benefits": [
            "Save $9 AUD instantly + qualifies for FREE Australia Post Express Delivery",
            "2x 300g jars (600g total) — choose any combination of the 5 botanical blends",
            "Ideal 24-hour routine: post-training body massage + relaxing evening care",
            "Dispatched fast from Melbourne hub"
        ]
    },
    {
        "id": "combo-best-value",
        "slug": "best-value-combo-dual-magnesium-gel",
        "sku": "ANCH-CMB-BEST3",
        "gtin13": "3800230111746",
        "name": "Best Value Combo | Dual Magnesium Gel (3-Pack)",
        "title": "Anchialo Best Value Combo — Dual Magnesium Gel 3-Pack (900g Total) | $129 AUD + Free Shipping",
        "category": "combo",
        "priceAUD": "129.00",
        "unitLabel": "/ 900g (3 × 300g)",
        "image": "assets/images/products/09_file.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_arnica_top_fv17.png",
        "badge": "Save $18 · Combat Team Pack",
        "stripe": "https://buy.stripe.com/7sYeVdgc4dt28yzbWT5Ne0k",
        "botanical": "Any 3 Signature Botanical Blends (900g Total Net Weight)",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, BOTANICAL EXTRACTS.",
        "description": "Choose any three 300g jars. Maximum value package designed for active fighters, gyms, families, and mineral ritual enthusiasts. Includes FREE Australia Post Express shipping.",
        "benefits": [
            "Save $18 AUD + FREE Express Delivery across Australia",
            "3x 300g jars (900g total) of certified Lake Pomorie Dual Magnesium Gel",
            "Trusted by ONE Championship veteran Sotir Kichukov and CPT MMA athletes",
            "Full batch traceability (Lot № 04 · Expiry 2027 · ISO 22716 GMP)"
        ]
    }
]


# 105 Melbourne Suburb, Community, B2B & AEO Comparison Landing Pages (Zero TGA therapeutic claims)
MELBOURNE_SUBURBS = [
    ("melbourne-cbd", "Melbourne CBD", "VIC 3000", "City Combat Gyms & Corporate Body Care", "Same-day / next-day dispatch across Melbourne 3000 for busy professionals, boxing gyms, and runners."),
    ("richmond", "Richmond", "VIC 3121", "Combat Sports, Pilates & Swan St Wellness", "Fast local dispatch to Richmond gyms, Brazilian Jiu-Jitsu mats, and remedial massage clinics along Swan & Church St."),
    ("collingwood", "Collingwood", "VIC 3066", "Strength Studios, Running Crews & Recovery", "Stocked in Melbourne for Collingwood strength facilities, boxers, and active creatives looking for non-drip magnesium gel."),
    ("fitzroy", "Fitzroy", "VIC 3065", "Boutique Studios & Natural Body Care", "Pure Lake Pomorie mineral cosmetics delivered fast to Fitzroy yoga, Reformer Pilates, and natural body-care enthusiasts."),
    ("south-yarra", "South Yarra", "VIC 3141", "The Tan Runners & Reformer Pilates Rituals", "Post-run magnesium massage rituals for athletes training around The Tan track and Chapel Street studios."),
    ("prahran", "Prahran", "VIC 3181", "High-Performance Conditioning & Massage", "Australian-stocked Bulgarian Black Sea magnesium gels for Prahran gym members, runners, and massage therapists."),
    ("st-kilda", "St Kilda", "VIC 3182", "Bayside Runners, Ocean Swimmers & Studios", "Hydrating Black Sea magnesium mineral gels delivered straight to St Kilda coastal athletes and bay swimmers."),
    ("brunswick", "Brunswick", "VIC 3056", "Muay Thai Gyms, Myotherapy & Community", "Authentic Black Sea magnesium body care for Brunswick combat gyms, community clinics, and active households."),
    ("oakleigh", "Oakleigh", "VIC 3166", "Greek-Australian Heritage & Eaton Mall", "From ancient Greek Anchialos on the Black Sea to Oakleigh's Eaton Mall — authentic 2,500-year coastal salt-lake heritage delivered locally."),
    ("northcote", "Northcote", "VIC 3070", "High Street Clinics & Greek Community", "Fast Melbourne dispatch to Northcote families, High Street wellness practitioners, and local Greek-Australian households."),
    ("thornbury", "Thornbury", "VIC 3071", "Pilates, Martial Arts & Evening Body Care", "Non-greasy Lake Pomorie magnesium gels for Thornbury athletes and massage studios."),
    ("bentleigh", "Bentleigh", "VIC 3204", "Bayside Fitness, Families & Local Studios", "Certified Lot 04 Bulgarian magnesium gels stocked in Melbourne for quick delivery to Bentleigh and Bentleigh East."),
    ("doncaster", "Doncaster", "VIC 3108", "Eastern Suburbs Gyms & Family Self-Care", "Quick Metro Melbourne shipping to Doncaster and Doncaster East for active families and fitness studios."),
    ("port-melbourne", "Port Melbourne", "VIC 3207", "Bayfront Running, CrossFit & Contrast Studios", "Ideal after Bay Trail runs and cold-plunge contrast sessions in Port Melbourne."),
    ("albert-park", "Albert Park", "VIC 3206", "Lake Runners, Rowing & Athletic Massage", "Post-run calf and shoulder massage rituals for Albert Park Lake track and rowing athletes."),
    ("footscray", "Footscray", "VIC 3011", "Inner West Combat & Strength Hubs", "Pure 253.14 g/L MgCl2 topical gels dispatched directly from Melbourne to Footscray boxing and MMA gyms."),
    ("preston", "Preston", "VIC 3072", "Northern Suburbs Martial Arts & Trades", "Easy-application 300g magnesium gel jars for Preston athletes and tradespeople finishing long physical shifts."),
    ("hawthorn", "Hawthorn", "VIC 3122", "Glenferrie Studios, Footy & Pilates", "Fast Melbourne metro dispatch for Hawthorn athletes, rowing clubs, and myotherapy practitioners."),
    ("kew", "Kew", "VIC 3101", "Boutique Wellness & Family Mineral Care", "Clean European ISO 22716 GMP mineral cosmetics delivered straight to Kew homes and clinics."),
    ("camberwell", "Camberwell", "VIC 3124", "Remedial Clinics & Active Households", "Pure Black Sea magnesium gels and unscented brine oil for Camberwell massage studios and runners."),
    ("brighton", "Brighton", "VIC 3186", "Bayside Coastal Running & Pilates", "Refreshing post-swim and post-Pilates skin hydration and massage gels delivered across Brighton 3186."),
    ("glen-waverley", "Glen Waverley", "VIC 3150", "Monash Corridor Sports & Clinics", "1–2 day Melbourne metro delivery to Glen Waverley and Mount Waverley studios and families."),
    ("rowville", "Rowville", "VIC 3178", "South-East Melbourne Combat & Pickup Access", "Ultra-fast local delivery across Rowville, Knoxfield, and Scoresby — plus direct Melbourne pickup via CPT MMA."),
    ("dandenong", "Dandenong", "VIC 3175", "South-East Gyms, Trades & Wholesale", "High-volume 300g magnesium gels and 3-Packs delivered fast across Dandenong and Noble Park."),
    ("frankston", "Frankston", "VIC 3199", "Peninsula Coast Athletes & Studios", "Fast Victorian delivery to Frankston, Seaford, and Mornington Peninsula wellness studios."),
    ("south-melbourne", "South Melbourne", "VIC 3205", "Market Hub, Boxing & Pilates Studios", "Authentic Lake Pomorie Black Sea magnesium gels delivered fast to South Melbourne studios and households."),
    ("windsor", "Windsor", "VIC 3181", "Chapel Precinct Training & Recovery", "Clean-label topical magnesium gels for Windsor conditioning coaches and busy hospitality workers."),
    ("carlton", "Carlton", "VIC 3053", "Lygon Street, Uni Athletes & Track Runners", "Princes Park runners and Melbourne University athletes enjoy fast local delivery across Carlton 3053."),
    ("abbotsford", "Abbotsford", "VIC 3067", "Yarra Trail Cyclists, Climbing & Studios", "Post-climb and post-ride forearm and calf massage gels for Abbotsford gyms and studios."),
    ("essendon", "Essendon", "VIC 3040", "North-West Football, Boxing & Clinics", "Fast Melbourne delivery to Essendon and Moonee Ponds clubs, gyms, and remedial practices."),
    ("moonee-ponds", "Moonee Ponds", "VIC 3039", "Puckle Street Fitness & Myotherapy", "Pure Lake Pomorie magnesium body care for Moonee Ponds runners, Pilates studios, and massage clinics."),
    ("yarraville", "Yarraville", "VIC 3013", "Inner West Runners & Community Studios", "Sun-evaporated Black Sea mineral gels delivered locally to Yarraville and Seddon."),
    ("williamstown", "Williamstown", "VIC 3016", "Coastal Sailing, Running & Body Care", "Post-sail and coastal running massage gel delivered straight from Melbourne to Williamstown."),
    ("elwood", "Elwood", "VIC 3184", "Beach Running, Yoga & Evening Wind-Down", "Natural Lavender and Arnica Dual Magnesium gels for Elwood active coastal routines."),
    ("elsternwick", "Elsternwick", "VIC 3185", "Pilates Studios & Evening Family Care", "Non-drip 300g magnesium gels for Elsternwick clinics and active households."),
    ("sandringham", "Sandringham", "VIC 3191", "Bayside Cycling, Golf & Track Care", "Great post-round and post-ride massage gel for Sandringham and Hampton athletes."),
    ("mentone", "Mentone", "VIC 3194", "Bayside Gyms, Swimming & Conditioning", "Certified European mineral cosmetics shipped quickly across Mentone, Mordialloc, and Parkdale."),
    ("cheltenham", "Cheltenham", "VIC 3192", "Bayside Commercial Gyms & Studios", "Direct Melbourne stock for Cheltenham strength gyms, trainers, and massage clinics."),
    ("malvern", "Malvern", "VIC 3144", "Boutique Pilates & Clinical Bodywork", "Luxury European-certified Lake Pomorie magnesium cosmetics for Malvern studios and homes."),
    ("armadale", "Armadale", "VIC 3143", "High Street Wellness & Natural Apothecary", "Clean minimal-INCI Black Sea mineral body care stocked in Melbourne for fast Armadale delivery."),
    ("toorak", "Toorak", "VIC 3142", "Private Training & Home Spa Rituals", "ISO 22716 GMP Bulgarian mineral gels and pure brine oil delivered discreetly across Toorak."),
    ("caulfield", "Caulfield", "VIC 3162", "Track, Turf & Community Massage Clinics", "Post-training recovery rituals stocked locally in Melbourne for Caulfield and Carnegie."),
    ("carnegie", "Carnegie", "VIC 3163", "Koornang Road Fitness & Family Care", "Authentic Lake Pomorie magnesium gels delivered fast to Carnegie gyms and households."),
    ("box-hill", "Box Hill", "VIC 3128", "Eastern Hub Gyms & Practitioners", "Fast Melbourne metro dispatch to Box Hill fitness centers, clinics, and practitioners."),
    ("blackburn", "Blackburn", "VIC 3130", "Bush-Trail Runners & Community Fitness", "Topical Dual Magnesium body gels for Blackburn runners, cyclists, and studios."),
    ("ringwood", "Ringwood", "VIC 3134", "Outer East Gyms, Sports & Clinics", "Fast dispatch across Ringwood, Croydon, and Mitcham for athletes and busy families."),
    ("croydon", "Croydon", "VIC 3136", "Maroondah Strength & Active Lifestyles", "Pure 253.14 g/L Black Sea magnesium gels shipped fast from Melbourne to Croydon."),
    ("knoxfield", "Knoxfield", "VIC 3180", "Local Pickup Proximity & East Gyms", "Fast metro delivery and nearby CPT MMA Melbourne pickup access for Knoxfield and Wantirna."),
    ("berwick", "Berwick", "VIC 3806", "Casey Sports Clubs & Conditioning Studios", "Certified Bulgarian magnesium gels and 3-Packs shipped direct from Melbourne to Berwick."),
    ("narre-warren", "Narre Warren", "VIC 3805", "South-East Combat & Family Wellness", "1–2 day VIC parcel delivery to Narre Warren and Fountain Gate athletes."),
    ("cranbourne", "Cranbourne", "VIC 3977", "South-East Trainers & Active Households", "Stocked in Victoria for fast delivery to Cranbourne gyms, trainers, and families."),
    ("mornington", "Mornington", "VIC 3931", "Peninsula Hot Springs Corridor & Trails", "Coastal sea-mineral heritage from Lake Pomorie delivered to Mornington Peninsula studios and runners."),
    ("heidelberg", "Heidelberg", "VIC 3084", "Banyule Trails, Cycling & Massage Care", "Fast metro delivery to Heidelberg, Ivanhoe, and Rosanna wellness practitioners."),
    ("ivanhoe", "Ivanhoe", "VIC 3079", "Yarra Boulevard Cyclists & Pilates", "Ideal post-ride massage gel for Yarra Boulevard riders and Ivanhoe studios."),
    ("coburg", "Coburg", "VIC 3058", "Merri Creek Runners & Combat Gyms", "Clean non-drip Dual Magnesium Gels delivered fast across Coburg and Pascoe Vale."),
    ("reservoir", "Reservoir", "VIC 3073", "Northern Boxing, Fitness & Home Care", "300g magnesium gels and pure brine oil shipped fast from Melbourne to Reservoir."),
    ("werribee", "Werribee", "VIC 3030", "Wyndham Gyms, Football & Martial Arts", "Fast VIC delivery to Werribee, Point Cook, and Hoppers Crossing clubs."),
    ("point-cook", "Point Cook", "VIC 3030", "Bayside West Trainers & Families", "Australian-stocked Black Sea magnesium body care delivered quickly to Point Cook."),
    ("geelong", "Geelong", "VIC 3220", "Regional VIC Surf Coast & Gyms", "Next-day regional Express Post from Melbourne to Geelong, Torquay, and Surf Coast athletes."),
    ("ballarat", "Ballarat", "VIC 3350", "Regional VIC Track, Gym & Winter Baths", "Warm evening mineral massage rituals and Express dispatch from Melbourne to Ballarat."),
]

NICHE_AEO_PAGES = [
    ("myotherapy-wholesale-melbourne", "Myotherapy Wholesale Melbourne", "Clinic & Practitioner Supply", "Bulk 300g Dual Magnesium Gels, 300ml Pure Brine Oil, and zero-risk QR Counter Partner stands for Victorian myotherapists — dispatched locally from Melbourne."),
    ("remedial-massage-supplies-victoria", "Remedial Massage Supplies Victoria", "Smooth Non-Drip Mineral Glide", "Upgrade studio bodywork with 100% pure Lake Pomorie brine oil (300ml) and Arnica/Rosemary gels crafted under ISO 22716 GMP."),
    ("mma-bjj-post-training-magnesium-gel", "MMA & BJJ Post-Training Magnesium Gel", "CPT MMA Tested Recovery Ritual", "Selected by ONE Championship veteran Sotir Kichukov for post-sparring forearm, calf, and shoulder massage without watery spray drip."),
    ("muay-thai-boxing-recovery-melbourne", "Muay Thai & Boxing Recovery Gel Melbourne", "Shin, Calf & Shoulder Ritual", "Fast-absorbing Arnica and Rosemary Dual Magnesium Gels built for heavy bag rounds, pad work, and post-shower recovery rituals."),
    ("reformer-pilates-recovery-melbourne", "Reformer Pilates Studio Partner Program", "Boutique Retail & QR Stand", "Offer clients clean European botanical magnesium cosmetics at your studio reception with zero upfront inventory via our QR partner program."),
    ("contrast-therapy-sauna-magnesium-victoria", "Contrast Therapy & Sauna Magnesium Protocol", "Cold Plunge + Sauna Ritual", "Pair crisp Alpine Juniper or Pure Black Sea Brine with warm showers and contrast-therapy recovery across Melbourne bathhouses."),
    ("float-centre-magnesium-brine-melbourne", "Float & Bathhouse Magnesium Retail Melbourne", "Take-Home Mineral Continuity", "Let float studio guests continue their magnesium ritual between visits with 300g Lake Pomorie gels and pure mineral brine."),
    ("magnesium-gel-vs-magnesium-spray-no-sting", "Magnesium Gel vs Magnesium Spray (Why Gel Feels Smoother)", "Cosmetic Comparison Guide", "Compare traditional watery magnesium chloride sprays against Anchialo's buffered Dual Magnesium Gel with glycerine and botanical extracts."),
    ("lake-pomorie-lye-vs-dead-sea-salt", "Lake Pomorie Black Sea Lye vs Dead Sea Salt", "Mineral Origin Comparison", "Explore how solar-concentrated Bulgarian Black Sea lye (253.14 g/L MgCl2 + 70.36 g/L MgSO4) differs from crystallized Dead Sea bath salts."),
    ("transdermal-magnesium-vs-epsom-salt-melbourne", "Dual Magnesium Lye vs Standard Epsom Salt", "MgCl2 + MgSO4 Synergy", "Why combining both Magnesium Chloride and Magnesium Sulfate in one Lake Pomorie harvest delivers superior massage and soak comfort."),
    ("greek-anchialos-black-sea-salt-melbourne", "Ancient Greek Anchialos to Melbourne", "2,500 Years of Black Sea Salt Heritage", "Discover the story of ancient Anchialos (modern Pomorie), its coastal salterns, and how its pure magnesium cosmetics reached Melbourne."),
    ("bulgarian-black-sea-lye-australia", "Authentic Bulgarian Black Sea Lye in Australia", "Melbourne Stocked · No 6-Week Wait", "Order genuine Lake Pomorie black sea lye gels and oils stocked right in Melbourne with 1–3 day Australia Post delivery."),
    ("the-tan-running-club-recovery-melbourne", "The Tan Running Club Post-Run Ritual", "3.8km Track Calf & Quad Care", "Built for Melbourne runners lapping The Tan — non-drip Arnica and Rosemary magnesium massage gels that go straight into your gym bag."),
    ("marathon-training-magnesium-gel-melbourne", "Melbourne Marathon Training Body Ritual", "Long-Run Calf & Foot Care", "Support high-mileage Melbourne marathon blocks with evening lavender massage and warm pure magnesium foot soaks."),
    ("crossfit-functional-fitness-recovery-vic", "CrossFit & Functional Fitness Magnesium Gel", "Post-WOD Forearm & Back Care", "Keep a 300g jar in your gym bag for fast post-WOD forearm, trap, and leg massage without greasy oil marks."),
    ("jiu-jitsu-grappling-grip-recovery-melbourne", "BJJ & Grappling Forearm Recovery Ritual", "Gi Grip & Shoulder Massage", "Trusted across Melbourne BJJ academies for fast-absorbing post-roll forearm, shoulder, and lower-back massage."),
    ("cycling-yarra-boulevard-recovery-gel", "Melbourne Cyclists & Yarra Boulevard Recovery", "Post-Ride Quad & Calf Care", "Light, fast-absorbing Dual Magnesium Gel formulated to refresh cycling legs and hydrate wind-exposed skin."),
    ("ocean-swimming-bayside-skin-magnesium", "Port Phillip Bay Swimmers Skin & Body Ritual", "Post-Swim Mineral Hydration", "Nourish skin after chilly St Kilda and Brighton bay swims with glycerine-enriched Lake Pomorie magnesium gels."),
    ("tennis-summer-recovery-melbourne", "Summer Court Training Body Care Melbourne", "Post-Match Calf & Shoulder Ritual", "Stay fresh through hot Melbourne court sessions with cooling Alpine Juniper and Arnica Dual Magnesium gels."),
    ("tradies-physical-workers-evening-magnesium", "Melbourne Tradies Evening Body & Foot Ritual", "After-Work Massage & Soak", "Hard days on concrete call for simple comfort — massage Pure Magnesium Oil or Arnica Gel into calves, feet, and shoulders after your shower."),
    ("desk-workers-neck-shoulder-magnesium-gel", "Desk & Tech Workers Neck & Shoulder Ritual", "5-Minute Evening Unwind", "Unwind tight upper shoulders after long screen hours with soothing Bulgarian Lavender or Rosemary Dual Magnesium Gel."),
    ("shift-workers-sleep-ritual-lavender-magnesium", "Shift Workers Evening Lavender Wind-Down", "Calm Bedtime Cosmetic Routine", "Transition smoothly after late shifts with a calming lavender-infused Lake Pomorie magnesium body massage."),
    ("hospitality-chefs-feet-leg-soak-melbourne", "Hospitality & Chefs Evening Foot Soak Ritual", "On-Your-Feet All Day Care", "Add concentrated Pure Magnesium Brine Oil to warm water after double shifts to refresh tired feet and lower legs."),
    ("physiotherapy-clinic-retail-melbourne", "Physiotherapy Clinic Partner Program Melbourne", "No-Inventory QR Stand Option", "Add clean European GMP magnesium gels to your Melbourne clinic reception using our turnkey zero-inventory QR display."),
    ("chiropractic-osteopathy-retail-victoria", "Osteopathy & Chiropractic Clinic Magnesium", "Practice Massage & Take-Home", "Support studio care with 100% pure unscented Lake Pomorie liquid brine and five clean botanical gel blends."),
    ("yoga-studio-evening-relaxation-melbourne", "Melbourne Yoga & Breathwork Studio Magnesium", "Savasana & Evening Ritual", "Enhance restorative yoga workshops and studio retail shelves with Bulgarian Lavender Dual Magnesium Gel."),
    ("strength-conditioning-gym-partner-vic", "Strength & Conditioning Gym Partner Melbourne", "15-20% QR Counter Commission", "Generate passive monthly margin from your front desk without buying upfront stock — automated Stripe tracking included."),
    ("personal-trainers-melbourne-affiliate-kit", "Melbourne Personal Trainers Partner Kit", "Client Recovery + Commission", "Equip your training clients with authentic European magnesium recovery gels using a personalized trainer partner code."),
    ("arnica-montana-magnesium-gel-guide", "Arnica Montana + Dual Magnesium Synergy Guide", "Our #1 Athletic Blend", "Why combining Lake Pomorie magnesium brine with Arnica Montana flower extract makes our top-selling post-training gel."),
    ("bulgarian-lavender-magnesium-bedtime-guide", "Bulgarian Lavender + Magnesium Bedtime Guide", "Evening Rest Ritual", "How authentic Lavandula Angustifolia flower extract and natural magnesium salts complement a consistent sleep hygiene routine."),
    ("rosemary-magnesium-massage-gel-guide", "Garden Rosemary + Magnesium Massage Guide", "Invigorating Botanical Blend", "Ideal for morning routines, pre-session activation massage, and revitalizing heavy legs."),
    ("alpine-juniper-magnesium-detox-ritual", "Alpine Juniper + Magnesium Sauna & Shower Ritual", "Crisp Botanical Care", "Pair crisp juniper terpenes with mineral brine for an invigorating post-sauna or post-workout body ritual."),
    ("red-grape-seed-polyphenol-magnesium-gel", "Red Grape Seed + Magnesium Skin Softness Guide", "Antioxidant Body Care", "Subtle vineyard aroma paired with glycerine and Pomorie sea minerals for smooth, nourished skin."),
    ("pure-black-sea-magnesium-oil-foot-soak", "Pure Black Sea Magnesium Oil Foot Soak Guide", "100% Unscented Liquid Lye", "How to use concentrated 253.14 g/L liquid Lake Pomorie brine for warm evening foot baths and studio massage."),
    ("post-workout-skin-hydration-magnesium", "Post-Workout Skin Hydration With Glycerine & Sea Salts", "No Sticky Residue", "Learn why plant glycerine and hydrocolloid gel texture prevent the dry salty tightness left by raw magnesium sprays."),
    ("sotir-kichukov-cpt-mma-melbourne-pickup", "CPT MMA Melbourne Local Pickup & Consultation", "Meet Founder Sotir Kichukov", "Prefer local Melbourne pickup instead of waiting for post? Order online and pick up directly through CPT MMA Melbourne."),
    ("iso-22716-gmp-tested-magnesium-australia", "ISO 22716 GMP & Zero Heavy Metals Magnesium", "Lab Certificate Lot 04", "Inspect the exact BDS 8840:1971 and European Pharmacopoeia assay (0.00 ppm Pb/Cd/As) behind every Anchialo jar."),
    ("vegan-cruelty-free-magnesium-gel-melbourne", "Vegan, Paraben-Free & Cruelty-Free Magnesium Gel", "Minimal 5-Ingredient INCI", "Zero synthetic dyes, zero parabens, zero animal testing — packaged in recyclable PET 1 300g jars."),
    ("gift-set-day-night-magnesium-duo-australia", "Day & Night Magnesium Gift Duo ($89 + Free Post)", "Starter 2-Pack Bundle", "The ideal active-lifestyle gift in Australia: daytime Arnica post-training gel + evening Bulgarian Lavender gel with free shipping."),
    ("combat-team-3-pack-magnesium-melbourne", "Combat Team & Family 3-Pack ($129 + Free Express)", "900g Best Value Bundle", "Stock the gym bag, bathroom shelf, and work locker with any three 300g blends and save $18 AUD."),
    ("gel-plus-oil-special-offer-melbourne", "1+1 Gel + Pure Oil Bundle ($49 AUD Melbourne)", "300g Gel + 300ml Oil", "Get both targeted botanical gel and full-body/foot-soak liquid mineral brine together for the price of a single jar."),
    ("melbourne-winter-bath-magnesium-soak", "Melbourne Winter Bath & Soak Magnesium Ritual", "Cold-Weather Warmth", "Turn cold Melbourne winter evenings into a warming Black Sea mineral bath and massage experience."),
    ("auspost-express-magnesium-delivery-australia", "1–3 Day Australia Post Magnesium Delivery", "Melbourne Metro & Interstate", "Dispatched directly from Melbourne — 1–2 business days across Victoria and 2–3 days Express to Sydney, Brisbane, Perth & Adelaide."),
    ("parents-grandparents-evening-foot-ritual", "Simple Home Relaxation Rituals for Parents", "Gentle Massage & Foot Bath", "Thoughtful, gentle ways to help parents and older family members unwind at home with warm mineral foot soaks."),
    ("how-to-avoid-magnesium-tingle-sensitive-skin", "Why High-Density Magnesium Tingles (And How To Use It Comfortably)", "Sensitive Skin Tips", "Practical tips on skin prep, timing, and cool-water rinsing so first-time users enjoy concentrated 253 g/L magnesium effortlessly."),
]


def load_blog_posts():
    blog_path = os.path.join(ROOT, "data", "blog_posts.json")
    with open(blog_path, "r", encoding="utf-8") as f:
        posts = json.load(f)
    changed = False
    for idx, p in enumerate(posts):
        if not p.get("description") or len(p["description"].strip()) < 30:
            body_lines = [ln.strip() for ln in p.get("body_text", "").splitlines() if len(ln.strip()) > 60]
            p["description"] = body_lines[0][:240] if body_lines else p["title"]
            changed = True
        img_obj = p.get("image") if isinstance(p.get("image"), dict) else {}
        orig_url = img_obj.get("url", "")
        local_webp = resolve_blog_local_image(orig_url, idx)
        if orig_url != local_webp:
            img_obj["@type"] = img_obj.get("@type", "ImageObject")
            img_obj["url"] = local_webp
            p["image"] = img_obj
            changed = True
    if changed:
        with open(blog_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return posts


def build_product_html(prod, depth_prefix="../"):
    canonical = f"https://anchialo.com/product-page/{prod['slug']}"
    img_abs = f"https://anchialo.com/{prod['image']}"
    web_img_rel = resolve_product_web_image(prod['image'])
    shipping_val = "0.00" if float(prod["priceAUD"]) >= 80.0 else "15.00"
    wa_msg = f"Hi Sotir, I would like to order {prod['name']} (A$ {prod['priceAUD']} AUD) from anchialo.com."
    wa_url = f"https://wa.me/61423269586?text={urllib.parse.quote(wa_msg)}"

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Product",
                "@id": f"{canonical}#product",
                "name": prod["name"],
                "sku": prod["sku"],
                "mpn": prod["sku"],
                "gtin13": prod["gtin13"],
                "description": prod["description"],
                "image": [img_abs, f"https://anchialo.com/{prod['lidImg']}"],
                "brand": {"@type": "Brand", "name": "ANCHIALO"},
                "manufacturer": {
                    "@type": "Organization",
                    "name": "Azimut 6000 Ltd",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": "Ivan Vazov 18",
                        "addressLocality": "Pomorie",
                        "postalCode": "8200",
                        "addressCountry": "BG"
                    }
                },
                "offers": {
                    "@type": "Offer",
                    "url": canonical,
                    "priceCurrency": "AUD",
                    "price": prod["priceAUD"],
                    "priceValidUntil": "2027-12-31",
                    "availability": "https://schema.org/InStock",
                    "itemCondition": "https://schema.org/NewCondition",
                    "seller": {
                        "@type": "Organization",
                        "@id": "https://anchialo.com/#business",
                        "name": "ANCHIALO Australia · Sotir Kichukov"
                    },
                    "shippingDetails": {
                        "@type": "OfferShippingDetails",
                        "shippingRate": {"@type": "MonetaryAmount", "value": shipping_val, "currency": "AUD"},
                        "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "AU"},
                        "deliveryTime": {
                            "@type": "ShippingDeliveryTime",
                            "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 1, "unitCode": "DAY"},
                            "transitTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 4, "unitCode": "DAY"}
                        }
                    },
                    "hasMerchantReturnPolicy": {
                        "@type": "MerchantReturnPolicy",
                        "applicableCountry": "AU",
                        "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                        "merchantReturnDays": 30,
                        "returnMethod": "https://schema.org/ReturnByMail",
                        "returnFees": "https://schema.org/ReturnFeesCustomerResponsibility"
                    }
                },
                "aggregateRating": build_aggregate_rating_schema(),
                "review": build_reviews_schema()
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "ANCHIALO Store", "item": "https://anchialo.com/"},
                    {"@type": "ListItem", "position": 2, "name": prod["name"], "item": canonical}
                ]
            }
        ]
    }

    benefits_html = "\n".join(
        f'<li style="margin-bottom:10px; display:flex; gap:10px; align-items:flex-start;"><span style="color:#059669; font-weight:700;">✓</span><span>{html.escape(b)}</span></li>'
        for b in prod["benefits"]
    )

    other_links = "\n".join(
        f'<a href="{depth_prefix}product-page/{p["slug"]}" style="padding:10px 16px; border-radius:999px; border:1px solid #E2DCD3; background:#fff; color:#1E3A2F; text-decoration:none; font-size:13.5px; font-weight:600;">{html.escape(p["name"])}</a>'
        for p in PRODUCTS if p["slug"] != prod["slug"]
    )

    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="google-site-verification" content="G2RuPksRn9KZ88AvHmiol_yZ1x-yz3LFeHwcCuFgjvI">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(prod['title'])}</title>
  <meta name="description" content="{html.escape(prod['description'])}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta property="og:type" content="product">
  <meta property="og:title" content="{html.escape(prod['title'])}">
  <meta property="og:description" content="{html.escape(prod['description'])}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{img_abs}">
  <meta property="og:site_name" content="ANCHIALO">
  <meta property="og:locale" content="en_AU">
  <meta property="product:price:amount" content="{prod['priceAUD']}">
  <meta property="product:price:currency" content="AUD">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(prod['title'])}">
  <meta name="twitter:description" content="{html.escape(prod['description'])}">
  <meta name="twitter:image" content="{img_abs}">
  <meta name="geo.region" content="AU-VIC">
  <meta name="geo.placename" content="Melbourne">
  <link rel="icon" type="image/x-icon" href="{depth_prefix}favicon.ico">
  <link rel="manifest" href="{depth_prefix}manifest.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{depth_prefix}styles.css?v=4">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
  <div class="announcement-bar">
    <div class="container announcement-inner">
      <span class="announcement-badge">✦ 100% NATURAL SOLAR HARVEST</span>
      <p class="announcement-text">Dual Magnesium Formula (253.14 g/L MgCl₂ &amp; 70.36 g/L MgSO₄) · FREE Express Delivery Across Australia on Orders Over $80</p>
      <div class="announcement-contact">
        <a href="https://wa.me/61423269586" target="_blank" rel="noopener"><span>Sotir Kichukov: +61 423 269 586</span></a>
      </div>
    </div>
  </div>

  <header class="site-header">
    <div class="container header-inner">
      <a href="{depth_prefix}index.html" class="brand-group">
        <span class="brand-logo-text">ANCHIALO</span>
        <span class="brand-tagline">BULGARIAN BLACK SEA BALNEOLOGY · POMORIE</span>
      </a>
      <nav class="nav-links">
        <a href="{depth_prefix}index.html#collection">Full Collection</a>
        <a href="{depth_prefix}index.html#blends">Botanical Blends</a>
        <a href="{depth_prefix}index.html#purity">Lab Purity</a>
        <a href="{depth_prefix}index.html#journal">Balneology Journal</a>
        <a href="https://cptmma.com/" target="_blank" rel="noopener">CPT MMA Melbourne</a>
      </nav>
    </div>
  </header>

  <main style="padding: 60px 0 90px; background: var(--bg-canvas, #FAF7F2);">
    <div class="container">
      <nav aria-label="Breadcrumb" style="margin-bottom: 28px; font-size: 13.5px; color: #5C6460;">
        <a href="{depth_prefix}index.html" style="color: #1E3A2F; text-decoration: none; font-weight: 600;">ANCHIALO Home</a>
        <span style="margin: 0 8px;">/</span>
        <a href="{depth_prefix}index.html#collection" style="color: #1E3A2F; text-decoration: none;">Collection</a>
        <span style="margin: 0 8px;">/</span>
        <span>{html.escape(prod['name'])}</span>
      </nav>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 48px; align-items: start; background: #fff; padding: 40px; border-radius: 24px; border: 1px solid #E6E0D6; box-shadow: 0 12px 32px rgba(30,58,47,0.06);">
        <div style="text-align: center; background: radial-gradient(circle at 50% 40%, #F4EFE6, #FAF7F2); border-radius: 18px; padding: 36px; border: 1px solid #EAE4DA;">
          <span style="display: inline-block; background: #1E3A2F; color: #fff; font-size: 11.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 6px 14px; border-radius: 999px; margin-bottom: 18px;">{html.escape(prod['badge'])}</span>
          <img src="{depth_prefix}{web_img_rel}" width="640" height="640" decoding="async" alt="{html.escape(prod['name'])}" style="max-width: 320px; width: 100%; height: auto; margin: 0 auto; display: block;">
        </div>

        <div>
          <span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B4833E;">{html.escape(prod['botanical'])}</span>
          <h1 style="font-family: 'Cormorant Garamond', serif; font-size: clamp(30px, 4vw, 44px); color: #162820; margin: 8px 0 14px; line-height: 1.15;">{html.escape(prod['name'])}</h1>
          <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px; font-size: 13.5px; color: #1E3A2F; font-weight: 600;">
            <span style="color: #D49B35; letter-spacing: 2px;">★★★★★</span>
            <a href="#product-reviews" style="color: #1E3A2F; text-decoration: underline;">5.0 / 5 ({len(VERIFIED_REVIEWS)} Verified Customer Reviews)</a>
          </div>
          <div style="display: flex; align-items: baseline; gap: 14px; margin-bottom: 20px;">
            <span style="font-size: 32px; font-weight: 800; color: #1E3A2F;">A$ {prod['priceAUD']} AUD</span>
            <span style="font-size: 14px; color: #5C6460;">{html.escape(prod['unitLabel'])} · Stocked in Melbourne</span>
          </div>
          <p style="font-size: 16px; line-height: 1.7; color: #2D3833; margin-bottom: 24px;">{html.escape(prod['description'])}</p>

          <ul style="list-style: none; padding: 0; margin: 0 0 28px; font-size: 14.5px; line-height: 1.55; color: #2D3833;">
            {benefits_html}
          </ul>

          <div style="display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 28px;">
            <a href="{prod['stripe']}" target="_blank" rel="noopener" style="flex: 1; min-width: 210px; background: #1E3A2F; color: #fff; text-align: center; padding: 16px 24px; border-radius: 999px; font-weight: 700; text-decoration: none; font-size: 15px;">Buy Now with Apple Pay / Card — A$ {prod['priceAUD']}</a>
            <a href="{wa_url}" target="_blank" rel="noopener" style="flex: 1; min-width: 210px; background: #F3EFEA; color: #1E3A2F; border: 1px solid #C8B99E; text-align: center; padding: 16px 24px; border-radius: 999px; font-weight: 700; text-decoration: none; font-size: 15px;">Order via WhatsApp (+61 423 269 586)</a>
          </div>

          <div style="background: #FAF7F2; padding: 18px 20px; border-radius: 14px; border: 1px solid #E6E0D6; font-size: 13px; color: #4A5550; line-height: 1.65;">
            <strong style="color: #162820; display: block; margin-bottom: 4px;">Full INCI Composition &amp; Traceability:</strong>
            {html.escape(prod['inci'])}<br>
            <span style="display: inline-block; margin-top: 6px; color: #1E3A2F; font-weight: 600;">For external cosmetic use only · Producer: Azimut 6000 Ltd, Pomorie, Bulgaria · GTIN: {prod['gtin13']} · Lot № 04 · Distributed in Australia by Sotir Kichukov (<a href="https://cptmma.com/" style="color:#1E3A2F;">CPT MMA Melbourne</a>).</span>
          </div>
        </div>
      </div>

      <section id="product-reviews" style="margin-top: 52px;">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 12px; margin-bottom: 22px;">
          <div>
            <span style="font-size: 11.5px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B4833E;">VERIFIED CUSTOMER FEEDBACK</span>
            <h2 style="font-family: 'Cormorant Garamond', serif; font-size: 30px; color: #162820; margin: 4px 0 0;">What Athletes &amp; Everyday Buyers Say</h2>
          </div>
          <div style="font-size: 14px; font-weight: 700; color: #1E3A2F; background: #fff; border: 1px solid #E6E0D6; padding: 8px 16px; border-radius: 999px;">
            <span style="color: #D49B35;">★★★★★</span> 5.0 / 5 Rating · {len(VERIFIED_REVIEWS)} Reviews
          </div>
        </div>
        <div class="reviews-grid">
{build_verified_reviews_cards_html()}
        </div>
      </section>

      <section style="margin-top: 56px;">
        <h2 style="font-family: 'Cormorant Garamond', serif; font-size: 28px; color: #162820; margin-bottom: 18px;">Explore Other Anchialo Formulations</h2>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
          {other_links}
          <a href="{depth_prefix}index.html#collection" style="padding:10px 18px; border-radius:999px; background:#1E3A2F; color:#fff; text-decoration:none; font-size:13.5px; font-weight:600;">View Complete Store &amp; Cart →</a>
        </div>
      </section>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container footer-bottom-inner" style="padding: 28px 0; text-align: center;">
      <p>© 2025–2027 ANCHIALO · Azimut 6000 Ltd &amp; <a href="https://cptmma.com/" style="color:inherit; text-decoration:underline;">CPT MMA Melbourne (Sotir Kichukov)</a> · <a href="{depth_prefix}index.html" style="color:inherit; text-decoration:underline;">Back to Main Store</a></p>
    </div>
  </footer>
</body>
</html>
"""


def build_redirect_html(target_url, title):
    safe_url = html.escape(target_url)
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <title>{html.escape(title)} | Redirecting</title>
  <meta name="robots" content="noindex, follow">
  <link rel="canonical" href="{safe_url}">
  <meta http-equiv="refresh" content="0; url={safe_url}">
  <script>location.replace({json.dumps(target_url)});</script>
</head>
<body>
  <p>Redirecting to <a href="{safe_url}">{safe_url}</a>...</p>
</body>
</html>
"""


def build_post_html(post, all_posts, depth_prefix="../"):
    slug = post["slug"]
    canonical = f"https://anchialo.com/post/{slug}"
    title = post["title"]
    desc = post.get("description", title)
    date_pub = post.get("datePublished", f"{BUILD_DATE}T00:00:00Z")[:10]
    date_mod = post.get("dateModified", date_pub)[:10]
    img_rel = post.get("image", {}).get("url", "assets/images/products/web/06_file_transp.webp").lstrip("/")
    img_url = img_rel if img_rel.startswith("http") else f"https://anchialo.com/{img_rel}"
    img_local = img_rel if img_rel.startswith("http") else f"{depth_prefix}{img_rel}"

    raw_lines = [ln.strip() for ln in post.get("body_text", "").splitlines() if ln.strip()]
    filtered_lines = []
    for i, ln in enumerate(raw_lines):
        if i < 5 and (ln == title or "Sotir Kichukov" in ln or "sotirkichukov" in ln or "min read" in ln or len(ln) <= 12):
            continue
        filtered_lines.append(ln)

    body_html_parts = []
    for ln in filtered_lines:
        if len(ln) < 85 and not ln.endswith(".") and not ln.endswith("!"):
            body_html_parts.append(f'<h2 style="font-family:\'Cormorant Garamond\',serif; font-size:26px; color:#162820; margin:28px 0 12px;">{html.escape(ln)}</h2>')
        else:
            body_html_parts.append(f'<p style="font-size:16.5px; line-height:1.8; color:#2D3833; margin-bottom:18px;">{html.escape(ln)}</p>')
    body_html = "\n".join(body_html_parts)

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "@id": f"{canonical}#article",
                "headline": title,
                "description": desc,
                "image": img_url,
                "datePublished": date_pub,
                "dateModified": date_mod,
                "author": {"@type": "Person", "@id": "https://cptmma.com/#sotir", "name": "Sotir Kichukov", "url": "https://cptmma.com/"},
                "publisher": {
                    "@type": "Organization",
                    "@id": "https://anchialo.com/#business",
                    "name": "ANCHIALO Australia",
                    "logo": {"@type": "ImageObject", "url": "https://anchialo.com/assets/images/products/06_file_transp.png"}
                },
                "mainEntityOfPage": {"@type": "WebPage", "@id": canonical}
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "ANCHIALO Store", "item": "https://anchialo.com/"},
                    {"@type": "ListItem", "position": 2, "name": "Balneology Journal", "item": "https://anchialo.com/#journal"},
                    {"@type": "ListItem", "position": 3, "name": title, "item": canonical}
                ]
            }
        ]
    }

    related = [p for p in all_posts if p["slug"] != slug][:4]
    related_html = "\n".join(
        f'<a href="{depth_prefix}post/{p["slug"]}" style="display:block; padding:16px; background:#fff; border:1px solid #E6E0D6; border-radius:14px; color:#162820; text-decoration:none; font-weight:600; font-size:15px;">{html.escape(p["title"])} →</a>'
        for p in related
    )

    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="google-site-verification" content="G2RuPksRn9KZ88AvHmiol_yZ1x-yz3LFeHwcCuFgjvI">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | ANCHIALO Balneology Journal</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{img_url}">
  <meta property="og:site_name" content="ANCHIALO">
  <meta property="og:locale" content="en_AU">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(desc)}">
  <meta name="twitter:image" content="{img_url}">
  <link rel="icon" type="image/x-icon" href="{depth_prefix}favicon.ico">
  <link rel="manifest" href="{depth_prefix}manifest.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{depth_prefix}styles.css?v=4">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
  <div class="announcement-bar">
    <div class="container announcement-inner">
      <span class="announcement-badge">✦ POMORIE BALNEOLOGY JOURNAL</span>
      <p class="announcement-text">Certified Dual Magnesium (253.14 g/L MgCl₂ &amp; 70.36 g/L MgSO₄) · Official Australian Store ($49 AUD)</p>
      <div class="announcement-contact">
        <a href="https://wa.me/61423269586" target="_blank" rel="noopener"><span>Sotir Kichukov: +61 423 269 586</span></a>
      </div>
    </div>
  </div>

  <header class="site-header">
    <div class="container header-inner">
      <a href="{depth_prefix}index.html" class="brand-group">
        <span class="brand-logo-text">ANCHIALO</span>
        <span class="brand-tagline">BULGARIAN BLACK SEA BALNEOLOGY · POMORIE</span>
      </a>
      <nav class="nav-links">
        <a href="{depth_prefix}index.html#collection">Shop Collection ($49)</a>
        <a href="{depth_prefix}index.html#blends">Botanical Blends</a>
        <a href="{depth_prefix}index.html#purity">Lab Certificate</a>
        <a href="{depth_prefix}index.html#journal">All Articles</a>
        <a href="https://cptmma.com/" target="_blank" rel="noopener">CPT MMA Melbourne</a>
      </nav>
    </div>
  </header>

  <main style="padding: 60px 0 90px; background: var(--bg-canvas, #FAF7F2);">
    <article class="container" style="max-width: 840px; margin: 0 auto; background: #fff; padding: clamp(28px, 5vw, 56px); border-radius: 24px; border: 1px solid #E6E0D6;">
      <nav aria-label="Breadcrumb" style="margin-bottom: 20px; font-size: 13.5px; color: #5C6460;">
        <a href="{depth_prefix}index.html" style="color: #1E3A2F; text-decoration: none; font-weight: 600;">ANCHIALO</a>
        <span style="margin: 0 8px;">/</span>
        <a href="{depth_prefix}index.html#journal" style="color: #1E3A2F; text-decoration: none;">Balneology Journal</a>
      </nav>

      <span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B4833E;">BALNEOLOGY &amp; RECOVERY RITUAL · PUBLISHED {date_pub}</span>
      <h1 style="font-family: 'Cormorant Garamond', serif; font-size: clamp(30px, 4.5vw, 46px); color: #162820; margin: 10px 0 16px; line-height: 1.15;">{html.escape(title)}</h1>
      <div style="font-size: 14px; color: #5C6460; margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid #EAE4DA;">
        By <a href="https://cptmma.com/" style="color: #1E3A2F; font-weight: 600; text-decoration: none;">Sotir Kichukov</a> (ONE Championship Veteran &amp; Founder of CPT MMA Melbourne) · Lake Pomorie Mineral Archive
      </div>

      <img src="{img_local}" alt="{html.escape(title)}" loading="lazy" decoding="async" style="width: 100%; max-height: 440px; object-fit: cover; border-radius: 16px; margin-bottom: 32px;">

      <div class="article-content">
        {body_html}
      </div>

      <div style="margin-top: 40px; padding: 28px; border-radius: 18px; background: #FAF7F2; border: 1px solid #D8CEBE; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 20px;">
        <div>
          <span style="font-size: 11.5px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #B4833E;">EXPERIENCE AUTHENTIC LAKE POMORIE LYE</span>
          <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 26px; color: #162820; margin: 4px 0;">Shop Anchialo Dual Magnesium Gels ($49 AUD)</h3>
          <p style="font-size: 14.5px; color: #4A5550; margin: 0;">253.14 g/L MgCl₂ + 70.36 g/L MgSO₄ · Dispatched from Melbourne via Australia Post.</p>
        </div>
        <a href="{depth_prefix}index.html#collection" style="background: #1E3A2F; color: #fff; padding: 14px 26px; border-radius: 999px; font-weight: 700; text-decoration: none; font-size: 14.5px;">Shop Collection →</a>
      </div>

      <section style="margin-top: 44px;">
        <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 24px; color: #162820; margin-bottom: 14px;">More from the Balneology Journal</h3>
        <div style="display: grid; gap: 12px;">
          {related_html}
        </div>
      </section>
    </article>
  </main>

  <footer class="site-footer">
    <div class="container footer-bottom-inner" style="padding: 28px 0; text-align: center;">
      <p>© 2025–2027 ANCHIALO · Azimut 6000 Ltd &amp; <a href="https://cptmma.com/" style="color:inherit; text-decoration:underline;">CPT MMA Melbourne</a> · <a href="{depth_prefix}index.html" style="color:inherit; text-decoration:underline;">Main Store</a></p>
    </div>
  </footer>
</body>
</html>
"""


def build_melbourne_pages_data():
    pages = []
    for slug, suburb, postcode, kicker, intro in MELBOURNE_SUBURBS:
        pages.append({
            "slug": slug,
            "kind": "suburb",
            "title": f"Dual Magnesium Gel {suburb} ({postcode}) — Black Sea Lye Delivery | ANCHIALO",
            "h1": f"Certified Black Sea Magnesium Gel in {suburb} ({postcode})",
            "kicker": f"{suburb.upper()} · {kicker.upper()}",
            "area": f"{suburb}, {postcode}",
            "description": f"{intro} Authentic Lake Pomorie Dual Magnesium Gels (253.14 g/L MgCl2 + 70.36 g/L MgSO4, 300g jar $49 AUD) dispatched fast across {suburb} and Melbourne.",
            "faq_q": f"How fast does ANCHIALO Dual Magnesium Gel arrive in {suburb} ({postcode})?",
            "faq_a": f"Orders placed on anchialo.com dispatch from our Melbourne hub via Australia Post (typically 1–2 business days to {suburb} {postcode}), with free Express delivery over $80 AUD or local pickup at CPT MMA."
        })

    for slug, heading, kicker, intro in NICHE_AEO_PAGES:
        pages.append({
            "slug": slug,
            "kind": "niche",
            "title": f"{heading} — ANCHIALO Lake Pomorie Dual Magnesium Australia",
            "h1": heading,
            "kicker": f"MELBOURNE SPECIALTY GUIDE · {kicker.upper()}",
            "area": "Melbourne, Victoria, Australia",
            "description": f"{intro} Pure 300g Lake Pomorie cosmetic gels ($49 AUD) and 300ml unscented mineral brine oil stocked in Melbourne under ISO 22716 GMP.",
            "faq_q": f"Why choose ANCHIALO Lake Pomorie Dual Magnesium for {heading}?",
            "faq_a": "ANCHIALO combines 253.14 g/L Magnesium Chloride and 70.36 g/L Magnesium Sulfate with natural botanicals (Arnica, Lavender, Rosemary, Juniper, Grape) or 100% pure brine in a clean, non-drip cosmetic formula stocked in Melbourne."
        })
    return pages


def build_melbourne_html(page, all_melbourne, depth_prefix="../"):
    slug = page["slug"]
    canonical = f"https://anchialo.com/melbourne/{slug}"
    wa_msg = f"Hi Sotir, I found anchialo.com ({page['h1']}) and would like details on ordering or Melbourne clinic/gym pickup."
    wa_url = f"https://wa.me/61423269586?text={urllib.parse.quote(wa_msg)}"

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "HealthAndBeautyBusiness",
                "@id": f"{canonical}#local",
                "name": f"ANCHIALO Australia — {page['area']}",
                "description": page["description"],
                "url": canonical,
                "telephone": "+61423269586",
                "areaServed": page["area"],
                "priceRange": "$49 - $129 AUD",
                "founder": {"@type": "Person", "name": "Sotir Kichukov", "url": "https://cptmma.com/"}
            },
            {
                "@type": "FAQPage",
                "@id": f"{canonical}#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": page["faq_q"],
                        "acceptedAnswer": {"@type": "Answer", "text": page["faq_a"]}
                    },
                    {
                        "@type": "Question",
                        "name": "What makes Lake Pomorie Black Sea lye different from standard magnesium spray?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "ANCHIALO unites 253.14 g/L Magnesium Chloride and 70.36 g/L Magnesium Sulfate with plant glycerine and botanical extracts in a smooth cosmetic gel that spreads cleanly without dripping."
                        }
                    }
                ]
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "ANCHIALO Store", "item": "https://anchialo.com/"},
                    {"@type": "ListItem", "position": 2, "name": "Melbourne Local Hub", "item": canonical}
                ]
            }
        ]
    }

    nearby = [p for p in all_melbourne if p["slug"] != slug][:12]
    nearby_links = "\n".join(
        f'<a href="{depth_prefix}melbourne/{p["slug"]}" style="padding:8px 14px; border-radius:999px; border:1px solid #E2DCD3; background:#fff; color:#1E3A2F; text-decoration:none; font-size:13px; font-weight:600;">{html.escape(p["h1"].split("—")[0][:42])}</a>'
        for p in nearby
    )

    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="google-site-verification" content="G2RuPksRn9KZ88AvHmiol_yZ1x-yz3LFeHwcCuFgjvI">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page['title'])}</title>
  <meta name="description" content="{html.escape(page['description'])}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{html.escape(page['title'])}">
  <meta property="og:description" content="{html.escape(page['description'])}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="https://anchialo.com/assets/images/products/06_file_transp.png">
  <meta property="og:locale" content="en_AU">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(page['title'])}">
  <meta name="twitter:description" content="{html.escape(page['description'])}">
  <meta name="twitter:image" content="https://anchialo.com/assets/images/products/06_file_transp.png">
  <meta name="geo.region" content="AU-VIC">
  <meta name="geo.placename" content="{html.escape(page['area'])}">
  <link rel="icon" type="image/x-icon" href="{depth_prefix}favicon.ico">
  <link rel="manifest" href="{depth_prefix}manifest.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{depth_prefix}styles.css?v=4">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
  <div class="announcement-bar">
    <div class="container announcement-inner">
      <span class="announcement-badge">✦ MELBOURNE LOCAL STOCK</span>
      <p class="announcement-text">Free Express Delivery Across {html.escape(page['area'])} Over $80 AUD · 253.14 g/L MgCl₂ + 70.36 g/L MgSO₄</p>
      <div class="announcement-contact">
        <a href="https://wa.me/61423269586" target="_blank" rel="noopener"><span>Sotir Kichukov: +61 423 269 586</span></a>
      </div>
    </div>
  </div>

  <header class="site-header">
    <div class="container header-inner">
      <a href="{depth_prefix}index.html" class="brand-group">
        <span class="brand-logo-text">ANCHIALO</span>
        <span class="brand-tagline">BULGARIAN BLACK SEA BALNEOLOGY · MELBOURNE</span>
      </a>
      <nav class="nav-links">
        <a href="{depth_prefix}index.html#collection">Shop Collection ($49)</a>
        <a href="{depth_prefix}index.html#ritual-quiz">30s Blend Finder</a>
        <a href="{depth_prefix}index.html#wholesale">Gym &amp; Clinic Partners</a>
        <a href="https://cptmma.com/" target="_blank" rel="noopener">CPT MMA Melbourne</a>
      </nav>
    </div>
  </header>

  <main style="padding: 56px 0 88px; background: var(--bg-canvas, #FAF7F2);">
    <div class="container" style="max-width: 960px;">
      <nav aria-label="Breadcrumb" style="margin-bottom: 24px; font-size: 13.5px; color: #5C6460;">
        <a href="{depth_prefix}index.html" style="color: #1E3A2F; text-decoration: none; font-weight: 600;">ANCHIALO Australia</a>
        <span style="margin: 0 8px;">/</span>
        <span>{html.escape(page['area'])}</span>
      </nav>

      <section style="background: #fff; padding: clamp(28px, 4vw, 48px); border-radius: 24px; border: 1px solid #E6E0D6; box-shadow: 0 12px 32px rgba(30,58,47,0.06);">
        <span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B4833E;">{html.escape(page['kicker'])}</span>
        <h1 style="font-family: 'Cormorant Garamond', serif; font-size: clamp(32px, 4.5vw, 48px); color: #162820; margin: 10px 0 16px; line-height: 1.15;">{html.escape(page['h1'])}</h1>
        <p style="font-size: 16.5px; line-height: 1.75; color: #2D3833; margin-bottom: 24px;">{html.escape(page['description'])}</p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-bottom: 28px;">
          <div style="background: #FAF7F2; padding: 16px; border-radius: 14px; border: 1px solid #EAE4DA;">
            <strong style="color: #1E3A2F; display:block; margin-bottom:4px;">253.14 g/L MgCl₂</strong>
            <span style="font-size: 13px; color: #4A5550;">Solar-evaporated Lake Pomorie Black Sea brine (BDS 8840:1971).</span>
          </div>
          <div style="background: #FAF7F2; padding: 16px; border-radius: 14px; border: 1px solid #EAE4DA;">
            <strong style="color: #1E3A2F; display:block; margin-bottom:4px;">Non-Drip 300g Gel</strong>
            <span style="font-size: 13px; color: #4A5550;">Arnica, Lavender, Rosemary, Juniper, Grape + Pure 300ml Oil.</span>
          </div>
          <div style="background: #FAF7F2; padding: 16px; border-radius: 14px; border: 1px solid #EAE4DA;">
            <strong style="color: #1E3A2F; display:block; margin-bottom:4px;">Zero Heavy Metals</strong>
            <span style="font-size: 13px; color: #4A5550;">0.00 ppm Pb/Cd/As · ISO 22716 GMP · Physiological pH 6.9.</span>
          </div>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 28px;">
          <a href="{depth_prefix}index.html#collection" style="background: #1E3A2F; color: #fff; padding: 14px 26px; border-radius: 999px; font-weight: 700; text-decoration: none; font-size: 15px;">Shop Gels &amp; Combos (From A$49) →</a>
          <a href="{wa_url}" target="_blank" rel="noopener" style="background: #F3EFEA; color: #1E3A2F; border: 1px solid #C8B99E; padding: 14px 24px; border-radius: 999px; font-weight: 700; text-decoration: none; font-size: 15px;">WhatsApp Sotir (+61 423 269 586)</a>
        </div>

        <div style="background: #F4EFE6; padding: 22px; border-radius: 16px; margin-bottom: 24px;">
          <h2 style="font-family: 'Cormorant Garamond', serif; font-size: 24px; color: #162820; margin-bottom: 8px;">{html.escape(page['faq_q'])}</h2>
          <p style="font-size: 14.5px; color: #2D3833; margin: 0;">{html.escape(page['faq_a'])}</p>
        </div>

        <div style="border-top: 1px solid #EAE4DA; padding-top: 20px; font-size: 13px; color: #5C6460;">
          <strong>Gym, Myotherapy &amp; Studio Partnerships in {html.escape(page['area'])}:</strong> Put a zero-risk QR display on your front desk (15–20% automated commission per scan) or request wholesale studio pricing directly via WhatsApp (+61 423 269 586). Cosmetic body care for external use only.
        </div>
      </section>

      <section style="margin-top: 40px;">
        <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 24px; color: #162820; margin-bottom: 14px;">Explore Nearby Melbourne Suburbs &amp; Recovery Guides</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
          {nearby_links}
        </div>
      </section>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container footer-bottom-inner" style="padding: 28px 0; text-align: center;">
      <p>© 2025–2027 ANCHIALO · Azimut 6000 Ltd &amp; <a href="https://cptmma.com/" style="color:inherit; text-decoration:underline;">CPT MMA Melbourne</a> · <a href="{depth_prefix}index.html" style="color:inherit; text-decoration:underline;">Main Store</a></p>
    </div>
  </footer>
</body>
</html>
"""


def build_home_jsonld():
    item_elements = []
    for idx, prod in enumerate(PRODUCTS, start=1):
        canonical = f"https://anchialo.com/product-page/{prod['slug']}"
        shipping_val = "0.00" if float(prod["priceAUD"]) >= 80.0 else "15.00"
        item_elements.append({
            "@type": "ListItem",
            "position": idx,
            "item": {
                "@type": "Product",
                "@id": f"{canonical}#product",
                "name": prod["name"],
                "url": canonical,
                "sku": prod["sku"],
                "mpn": prod["sku"],
                "gtin13": prod["gtin13"],
                "image": f"https://anchialo.com/{prod['image']}",
                "description": prod["description"],
                "brand": {"@type": "Brand", "name": "ANCHIALO"},
                "offers": {
                    "@type": "Offer",
                    "url": canonical,
                    "priceCurrency": "AUD",
                    "price": prod["priceAUD"],
                    "priceValidUntil": "2027-12-31",
                    "availability": "https://schema.org/InStock",
                    "itemCondition": "https://schema.org/NewCondition",
                    "shippingDetails": {
                        "@type": "OfferShippingDetails",
                        "shippingRate": {"@type": "MonetaryAmount", "value": shipping_val, "currency": "AUD"},
                        "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "AU"},
                        "deliveryTime": {
                            "@type": "ShippingDeliveryTime",
                            "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 1, "unitCode": "DAY"},
                            "transitTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 4, "unitCode": "DAY"}
                        }
                    },
                    "hasMerchantReturnPolicy": {
                        "@type": "MerchantReturnPolicy",
                        "applicableCountry": "AU",
                        "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                        "merchantReturnDays": 30,
                        "returnMethod": "https://schema.org/ReturnByMail",
                        "returnFees": "https://schema.org/ReturnFeesCustomerResponsibility"
                    }
                },
                "aggregateRating": build_aggregate_rating_schema(),
                "review": build_reviews_schema()
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": ["OnlineStore", "HealthAndBeautyBusiness"],
                "@id": "https://anchialo.com/#business",
                "name": "ANCHIALO Australia",
                "legalName": "ANCHIALO · Azimut 6000 Ltd & CPT MMA Australia",
                "alternateName": ["Anchialo Dual Magnesium", "Anchialo Black Sea Balneology"],
                "description": "Authentic Bulgarian Black Sea mineral cosmetics. 100% natural Dual Magnesium gels (253.14 g/L MgCl2 & 70.36 g/L MgSO4) and pure topical brine oil harvested from Lake Pomorie. Official Australian Store ($49 AUD) dispatched from Melbourne.",
                "url": "https://anchialo.com/",
                "logo": "https://anchialo.com/assets/images/products/06_file_transp.png",
                "image": "https://anchialo.com/assets/images/products/06_file_transp.png",
                "telephone": "+61423269586",
                "priceRange": "$49 - $129 AUD",
                "currenciesAccepted": "AUD, USD, EUR, BGN",
                "paymentAccepted": "Credit Card, Apple Pay, Google Pay, PayPal, Stripe",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Melbourne",
                    "addressRegion": "VIC",
                    "postalCode": "3000",
                    "addressCountry": "AU"
                },
                "areaServed": [
                    {"@type": "Country", "name": "Australia"},
                    {"@type": "City", "name": "Melbourne"}
                ],
                "founder": {
                    "@type": "Person",
                    "@id": "https://cptmma.com/#sotir",
                    "name": "Sotir Kichukov",
                    "url": "https://cptmma.com/"
                },
                "aggregateRating": build_aggregate_rating_schema(),
                "review": build_reviews_schema(),
                "sameAs": [
                    "https://cptmma.com/",
                    "https://cptmma.com/magnesium",
                    "https://www.facebook.com/ProFighterAndCoach",
                    "https://www.instagram.com/sotir_kichukov/",
                    "https://www.tiktok.com/@sotir_kichukov"
                ]
            },
            {
                "@type": "WebSite",
                "@id": "https://anchialo.com/#website",
                "url": "https://anchialo.com/",
                "name": "ANCHIALO — Pure Black Sea Balneology & Certified Dual Magnesium",
                "inLanguage": "en-AU",
                "publisher": {"@id": "https://anchialo.com/#business"}
            },
            {
                "@type": "ItemList",
                "@id": "https://anchialo.com/#catalog",
                "name": "The Complete Anchialo Dual Magnesium Collection",
                "itemListElement": item_elements
            },
            {
                "@type": "FAQPage",
                "@id": "https://anchialo.com/#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "Why choose topical magnesium gel over oral tablets?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Oral magnesium tablets can feel heavy on sensitive digestion. Topical magnesium chloride and sulfate body gels apply smoothly onto the skin during post-training massage, leaving the skin hydrated and refreshed without digestive stress."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "How do I apply Anchialo Dual Magnesium Gel?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Massage a generous amount onto clean, dry skin on calves, shoulders, forearms, or lower back. Allow it to absorb for 30 minutes to several hours, or leave it on overnight for deeper relaxation and skin hydration. If light salt crystals form, simply rinse with cool water."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "Will I feel a tingling sensation?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Because Anchialo contains over 250 g/L concentrated Lake Pomorie mineral salts, a light warming or tingling sensation during the first few applications is normal. Applying onto clean hydrated skin or rinsing after 30 minutes keeps every session comfortable."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "What is the difference between the Gel and the Pure Oil?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Anchialo Dual Magnesium Gel is enriched with natural hydrocolloids and botanical extracts (Arnica, Lavender, Rosemary, Juniper, Grape) for a smooth, non-drip massage application. Anchialo Magnesium Oil is a 100% pure, unfragranced liquid mineral brine ideal for full-body rubs or mineral foot baths."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "How can I order and receive my parcel in Australia?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "All stock is located in Melbourne under Sotir Kichukov. You can order directly online through anchialo.com ($49 AUD per jar) or message via WhatsApp (+61 423 269 586) for local pickup at CPT MMA or Australia Post Express dispatch with tracking."
                        }
                    }
                ]
            }
        ]
    }
    return json.dumps(schema, ensure_ascii=False)


def update_index_and_app(posts, melbourne_pages):
    index_path = os.path.join(ROOT, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    jsonld_script = f'<script type="application/ld+json">{build_home_jsonld()}</script>'
    content, ld_replaced = re.subn(
        r'<script type="application/ld\+json">.*?</script>',
        lambda _m: jsonld_script,
        content,
        count=1,
        flags=re.DOTALL,
    )
    if ld_replaced == 0:
        content = content.replace("</head>", f"  {jsonld_script}\n</head>", 1)

    # 2. Idempotent SSR replacement for #productsGrid
    ssr_products = []
    for prod in PRODUCTS:
        web_img = resolve_product_web_image(prod["image"])
        wa_msg = urllib.parse.quote(f"Hi Sotir, I would like to order {prod['name']} (A$ {prod['priceAUD']} AUD). Please confirm delivery / Melbourne pickup.")
        ssr_products.append(f"""          <div class="product-card">
            <div class="product-thumb">
              <span class="product-flag">{html.escape(prod['badge'])}</span>
              <a href="product-page/{prod['slug']}" title="{html.escape(prod['name'])}"><img src="{web_img}" width="640" height="640" alt="{html.escape(prod['name'])}" loading="lazy" decoding="async"></a>
            </div>
            <div class="product-body">
              <h3 class="product-name"><a href="product-page/{prod['slug']}" style="color:inherit;text-decoration:none;">{html.escape(prod['name'])}</a></h3>
              <div class="product-price-row">
                <span class="price-main">A$ {prod['priceAUD']} AUD</span>
                <span class="price-unit">{html.escape(prod['unitLabel'])}</span>
              </div>
              <p class="product-desc">{html.escape(prod['description'])}</p>
              <div class="product-actions">
                <button class="btn-card-add" data-id="{prod['id']}"><span>Add to Bag</span></button>
                <a href="https://wa.me/61423269586?text={wa_msg}" target="_blank" rel="noopener" class="btn-card-wa" title="Order via WhatsApp">WhatsApp</a>
              </div>
            </div>
          </div>""")
    ssr_products_block = '<div class="products-grid" id="productsGrid">\n' + "\n".join(ssr_products) + '\n        </div>'

    content = re.sub(
        r'<div class="products-grid" id="productsGrid">.*?        </div>(?=\s*\n\s*<!-- Melbourne Gyms)',
        lambda _: ssr_products_block,
        content,
        count=1,
        flags=re.DOTALL,
    )

    # 3. Idempotent SSR replacement for #blogGrid + journal archive + Melbourne local hub nav
    ssr_blogs = []
    for idx, post in enumerate(posts[:6]):
        img_url = post.get("image", {}).get("url", "assets/images/products/web/06_file_transp.webp")
        ssr_blogs.append(f"""          <div class="blog-card">
            <div class="blog-card-thumb">
              <a href="post/{post['slug']}"><img src="{img_url}" alt="{html.escape(post['title'])}" loading="lazy" decoding="async"></a>
            </div>
            <div class="blog-card-body">
              <span class="blog-card-meta">BALNEOLOGY REPORT · Sotir Kichukov</span>
              <h3 class="blog-card-title"><a href="post/{post['slug']}" style="color:inherit;text-decoration:none;">{html.escape(post['title'])}</a></h3>
              <p class="blog-card-excerpt">{html.escape(post.get('description', ''))}</p>
              <a href="post/{post['slug']}" class="btn-read-article" data-idx="{idx}"><span>Read Full Article</span></a>
            </div>
          </div>""")

    archive_links = "\n".join(
        f'            <a href="post/{p["slug"]}" style="font-size:13.5px; color:#1E3A2F; text-decoration:underline; margin-right:14px; display:inline-block; margin-bottom:6px;">{html.escape(p["title"])}</a>'
        for p in posts
    )
    featured_melbourne = melbourne_pages[:24]
    melbourne_links = "\n".join(
        f'            <a href="melbourne/{m["slug"]}" style="font-size:12.5px; color:#4A5550; text-decoration:underline; margin-right:12px; display:inline-block; margin-bottom:5px;">{html.escape(m["area"] if m["kind"] == "suburb" else m["h1"].split("(")[0].strip())}</a>'
        for m in featured_melbourne
    )

    ssr_blog_block = (
        '<div class="blog-grid" id="blogGrid">\n'
        + "\n".join(ssr_blogs)
        + '\n        </div>\n'
        + '        <nav aria-label="Complete Balneotherapy Research Archive" style="margin-top:28px; padding-top:20px; border-top:1px solid rgba(30,58,47,0.12);">\n'
        + f'          <strong style="display:block; font-size:12px; letter-spacing:0.12em; text-transform:uppercase; color:#5C6460; margin-bottom:10px;">Complete Balneology &amp; Recovery Archive ({len(posts)} Publications):</strong>\n'
        + archive_links
        + '\n        </nav>\n'
        + '        <nav aria-label="Melbourne Local Dispatch & Clinic Guides" style="margin-top:18px; padding-top:16px; border-top:1px solid rgba(30,58,47,0.08);">\n'
        + f'          <strong style="display:block; font-size:12px; letter-spacing:0.12em; text-transform:uppercase; color:#5C6460; margin-bottom:8px;">Melbourne Suburb Delivery &amp; Clinic Hubs ({len(melbourne_pages)} Local Pages):</strong>\n'
        + melbourne_links
        + '\n        </nav>'
    )

    content = re.sub(
        r'<div class="blog-grid" id="blogGrid">.*?(?=\s*\n\s*</div>\s*\n\s*</section>\s*\n\s*<!-- ==================== FREQUENTLY ASKED QUESTIONS)',
        lambda _: ssr_blog_block,
        content,
        count=1,
        flags=re.DOTALL,
    )

    # 4. Idempotent SSR sync for #reviewsGrid
    ssr_reviews_block = (
        '<div class="reviews-grid" id="reviewsGrid">\n'
        + build_verified_reviews_cards_html()
        + '\n        </div>'
    )
    content = re.sub(
        r'<div class="reviews-grid" id="reviewsGrid">.*?        </div>',
        lambda _: ssr_reviews_block,
        content,
        count=1,
        flags=re.DOTALL,
    )

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    optimize_web_assets()
    posts = load_blog_posts()
    melbourne_pages = build_melbourne_pages_data()

    prod_root = os.path.join(ROOT, "product-page")
    os.makedirs(prod_root, exist_ok=True)
    for prod in PRODUCTS:
        slugs = [prod["slug"]]
        if prod.get("alias_slug"):
            slugs.append(prod["alias_slug"])
        for s in slugs:
            with open(os.path.join(prod_root, f"{s}.html"), "w", encoding="utf-8") as f:
                f.write(build_product_html(prod, depth_prefix="../"))
            sub = os.path.join(prod_root, s)
            os.makedirs(sub, exist_ok=True)
            with open(os.path.join(sub, "index.html"), "w", encoding="utf-8") as f:
                f.write(build_product_html(prod, depth_prefix="../../"))

    post_root = os.path.join(ROOT, "post")
    os.makedirs(post_root, exist_ok=True)
    for post in posts:
        s = post["slug"]
        with open(os.path.join(post_root, f"{s}.html"), "w", encoding="utf-8") as f:
            f.write(build_post_html(post, posts, depth_prefix="../"))
        sub = os.path.join(post_root, s)
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "index.html"), "w", encoding="utf-8") as f:
            f.write(build_post_html(post, posts, depth_prefix="../../"))

        # Write clean canonical redirects for legacy therapeutic URLs so zero backlinks break
        for old_slug in post.get("legacy_slugs", []):
            target = f"https://anchialo.com/post/{s}"
            redir_html = build_redirect_html(target, post["title"])
            with open(os.path.join(post_root, f"{old_slug}.html"), "w", encoding="utf-8") as f:
                f.write(redir_html)
            old_sub = os.path.join(post_root, old_slug)
            os.makedirs(old_sub, exist_ok=True)
            with open(os.path.join(old_sub, "index.html"), "w", encoding="utf-8") as f:
                f.write(redir_html)

    mel_root = os.path.join(ROOT, "melbourne")
    os.makedirs(mel_root, exist_ok=True)
    for page in melbourne_pages:
        s = page["slug"]
        with open(os.path.join(mel_root, f"{s}.html"), "w", encoding="utf-8") as f:
            f.write(build_melbourne_html(page, melbourne_pages, depth_prefix="../"))
        sub = os.path.join(mel_root, s)
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "index.html"), "w", encoding="utf-8") as f:
            f.write(build_melbourne_html(page, melbourne_pages, depth_prefix="../../"))

    urls = [("https://anchialo.com/", BUILD_DATE, "daily", "1.0")]
    for prod in PRODUCTS:
        urls.append((f"https://anchialo.com/product-page/{prod['slug']}", BUILD_DATE, "weekly", "0.9"))
    for post in posts:
        d = post.get("dateModified", BUILD_DATE)[:10]
        urls.append((f"https://anchialo.com/post/{post['slug']}", d, "monthly", "0.8"))
    for page in melbourne_pages:
        urls.append((f"https://anchialo.com/melbourne/{page['slug']}", BUILD_DATE, "monthly", "0.8"))

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for loc, lastmod, freq, prio in urls:
        sitemap_lines.append("  <url>")
        sitemap_lines.append(f"    <loc>{loc}</loc>")
        sitemap_lines.append(f"    <lastmod>{lastmod}</lastmod>")
        sitemap_lines.append(f"    <changefreq>{freq}</changefreq>")
        sitemap_lines.append(f"    <priority>{prio}</priority>")
        sitemap_lines.append("  </url>")
    sitemap_lines.append("</urlset>\n")

    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_lines))

    update_index_and_app(posts, melbourne_pages)
    print(
        f"Successfully updated index.html, {len(PRODUCTS)} product pages, "
        f"{len(posts)} blog pages, {len(melbourne_pages)} Melbourne pages, and sitemap.xml ({len(urls)} URLs)."
    )


if __name__ == "__main__":
    main()
