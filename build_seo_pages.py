import json
import os
import html
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))

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
        "image": "assets/images/products/06_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_arnica_top_fv17.png",
        "badge": "Bestseller · Muscle Relief",
        "stripe": "https://buy.stripe.com/9B67sL4tmfBa9CD0eb5Ne0e",
        "botanical": "Arnica Montana Flower Extract",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA FLOWER EXTRACT.",
        "description": "Fast-absorbing topical gel enriched with Arnica Montana and 253.14 g/L natural Black Sea magnesium chloride plus 70.36 g/L magnesium sulfate. Relieves acute muscle aches, bruises, joint inflammation, and spasms. 300g net. Dispatched from Melbourne, Australia.",
        "benefits": [
            "Rapid transdermal relief for muscle cramps, spasms, and post-combat or athletic soreness",
            "253.14 g/L Magnesium Chloride & 70.36 g/L Magnesium Sulfate from Lake Pomorie, Bulgaria",
            "Infused with genuine Arnica Montana flower extract to soothe bruised tissues and tendons",
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
        "image": "assets/images/products/01_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_lavender_top_fv17.png",
        "badge": "Deep Sleep & Calming",
        "stripe": "https://buy.stripe.com/cNi14ncZS9cMeWX9OL5Ne0d",
        "botanical": "Lavandula Angustifolia Essential Flower Extract",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT.",
        "description": "Infused with authentic Bulgarian Lavender and Lake Pomorie Dual Magnesium (253.14 g/L MgCl2). Calms central nervous excitability, alleviates restless legs, and supports deep restorative night sleep. 300g net.",
        "benefits": [
            "Calms neuromuscular excitability and overactive nervous system after evening training",
            "Synergizes transdermal magnesium ions with soothing Bulgarian Lavandula Angustifolia",
            "Supports deeper, uninterrupted REM and slow-wave sleep cycles without oral melatonin",
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
        "image": "assets/images/products/04_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_rosemary_top_fv17.png",
        "badge": "Joint Mobility & Warm-Up",
        "stripe": "https://buy.stripe.com/8x2dR9cZSbkUdST5yv5Ne0f",
        "botanical": "Rosmarinus Officinalis Leaf Powder Extract",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ROSMARINUS OFFICINALIS LEAF POWDER EXTRACT.",
        "description": "Invigorating rosemary extract stimulates thermal microcirculation and speeds tendon warm-up. Combined with 253.14 g/L Black Sea Magnesium Chloride for active athletes and post-workout recovery. 300g net.",
        "benefits": [
            "Stimulates localized capillary blood flow and thermal microcirculation",
            "Ideal for pre-fight / pre-training tendon warm-up and morning joint stiffness",
            "Revives cold extremities and fatigued lower-back or shoulder musculature",
            "Direct osmotic transdermal absorption — zero digestive upset"
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
        "image": "assets/images/products/07_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_juniper_top_fv17.png",
        "badge": "Deep Tissue Detox",
        "stripe": "https://buy.stripe.com/14A3cv7Fy4Ww5mne515Ne0g",
        "botanical": "Juniperus Chinensis Leaf Extract & Fruit Oil",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE, JUNIPERUS CHINENSIS LEAF EXTRACT.",
        "description": "Alpine juniper fruit terpenes assist lymphatic drainage and ease chronic morning joint stiffness, arthritis discomfort, and heavy congested limbs. 300g net.",
        "benefits": [
            "Assists osmotic tissue drainage and flushing of metabolic lactic acid residues",
            "Targeted relief for arthritic stiffness, sprains, and congested joints",
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
        "image": "assets/images/products/03_file_transp.png",
        "lidImg": "assets/official_labels_rendered/anhialo_massage_gel_grape_top_fv17.png",
        "badge": "Antioxidant & Skin Tone",
        "stripe": "https://buy.stripe.com/cNidR97FycoY0239OL5Ne0h",
        "botanical": "Vitis Vinifera (Grape) Seed Polyphenol Extract",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE.",
        "description": "Rich in grape seed polyphenols and resveratrol antioxidants. Promotes skin elasticity, shields dermal collagen, and feeds transdermal magnesium to tired muscles. 300g net.",
        "benefits": [
            "Rich in proanthocyanidins and resveratrol antioxidants for dermal elasticity",
            "Replenishes cellular magnesium while hydrating and toning dry skin",
            "Soothes muscle tension with a delicate, refreshing vineyard finish",
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
        "image": "assets/images/products/08_file_transp.png",
        "lidImg": "assets/images/products/08_file_transp.png",
        "badge": "100% Pure Liquid Brine",
        "stripe": "https://buy.stripe.com/aFaeVdgc4ex6cOP1if5Ne0i",
        "botanical": "100% Unscented Natural Lake Pomorie Mineral Brine (Luga)",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM CHLORIDE 253.14 g/L, MAGNESIUM SULFATE 70.36 g/L, SODIUM CHLORIDE, TRACE BROMINE & IODINE).",
        "description": "Unscented, highly bioavailable liquid Black Sea mineral brine oil. Silky transdermal glide for full-body sport massage, joint compresses, or mineral foot soak recovery. 300ml.",
        "benefits": [
            "100% pure unfragranced fractional solar brine from Lake Pomorie",
            "Maximum ionic concentration for full-body rubs, compresses, and foot baths",
            "Rapid transdermal absorption with natural silky mineral glide",
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
        "image": "assets/images/products/02_file.png",
        "lidImg": "assets/images/products/02_file.png",
        "badge": "1+1 Free Value Deal",
        "stripe": "https://buy.stripe.com/cNi14ncZS9cMeWX9OL5Ne0d",
        "botanical": "Choice of Signature Botanical Gel (300g) + Pure Magnesium Brine Oil (300ml)",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, BOTANICAL EXTRACT.",
        "description": "Buy 1 Dual Magnesium Gel (any blend) and receive 1 Dual Magnesium Oil FREE. Double the balneotherapy recovery care for the price of one single jar ($49 AUD).",
        "benefits": [
            "Includes 1x 300g Dual Magnesium Botanical Gel + 1x 300ml Pure Magnesium Oil",
            "Complete transdermal protocol: targeted gel massage + full-body liquid brine",
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
        "image": "assets/images/products/05_file.png",
        "lidImg": "assets/images/products/05_file.png",
        "badge": "Save $9 · Day & Night Pair",
        "stripe": "https://buy.stripe.com/6oU4gzcZS60AeWX9OL5Ne0j",
        "botanical": "Any 2 Signature Botanical Blends (e.g., Arnica Day Recovery + Lavender Night Sleep)",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, BOTANICAL EXTRACTS.",
        "description": "Pair Arnica for daytime athletic recovery with Bulgarian Lavender for evening sleep and nervous system reset. Total 600g pure Pomorie magnesium gels with FREE Australia-wide Express shipping.",
        "benefits": [
            "Save $9 AUD instantly + qualifies for FREE Australia Post Express Delivery",
            "2x 300g jars (600g total) — choose any combination of the 5 botanical blends",
            "Ideal 24-hour athletic recovery cycle: pre/post training + deep night sleep",
            "Official ATO Tax Invoice provided on checkout"
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
        "image": "assets/images/products/09_file.png",
        "lidImg": "assets/images/products/09_file.png",
        "badge": "Save $18 · Combat Team Pack",
        "stripe": "https://buy.stripe.com/7sYeVdgc4dt28yzbWT5Ne0k",
        "botanical": "Any 3 Signature Botanical Blends (900g Total Net Weight)",
        "inci": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, BOTANICAL EXTRACTS.",
        "description": "Choose any three 300g jars. Maximum value package designed for active fighters, gyms, families, and balneotherapy enthusiasts. Includes FREE Australia Post Express shipping.",
        "benefits": [
            "Save $18 AUD + FREE Express Delivery across Australia",
            "3x 300g jars (900g total) of certified Lake Pomorie Dual Magnesium Gel",
            "Trusted by ONE Championship veteran Sotir Kichukov and CPT MMA athletes",
            "Full batch traceability (Lot № 04 · Expiry 2027 · ISO 22716 GMP)"
        ]
    }
]


def load_blog_posts():
    with open(os.path.join(ROOT, "data", "blog_posts.json"), "r", encoding="utf-8") as f:
        posts = json.load(f)
    for p in posts:
        if not p.get("description") or len(p["description"].strip()) < 30:
            body_lines = [ln.strip() for ln in p.get("body_text", "").splitlines() if len(ln.strip()) > 60]
            p["description"] = body_lines[0][:240] if body_lines else p["title"]
    return posts


def build_product_html(prod, depth_prefix="../"):
    canonical = f"https://anchialo.com/product-page/{prod['slug']}"
    img_abs = f"https://anchialo.com/{prod['image']}"
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
                "gtin13": prod["gtin13"],
                "description": prod["description"],
                "image": [img_abs, f"https://anchialo.com/{prod['lidImg']}"],
                "brand": {
                    "@type": "Brand",
                    "name": "ANCHIALO"
                },
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
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.9",
                    "bestRating": "5",
                    "ratingCount": "420",
                    "reviewCount": "420"
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
                        "shippingDestination": {
                            "@type": "DefinedRegion",
                            "addressCountry": "AU"
                        },
                        "deliveryTime": {
                            "@type": "ShippingDeliveryTime",
                            "handlingTime": {
                                "@type": "QuantitativeValue",
                                "minValue": 0,
                                "maxValue": 1,
                                "unitCode": "DAY"
                            },
                            "transitTime": {
                                "@type": "QuantitativeValue",
                                "minValue": 1,
                                "maxValue": 4,
                                "unitCode": "DAY"
                            }
                        }
                    }
                }
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "ANCHIALO Store",
                        "item": "https://anchialo.com/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": prod["name"],
                        "item": canonical
                    }
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
  <link rel="stylesheet" href="{depth_prefix}styles.css">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
  <div class="announcement-bar">
    <div class="container announcement-inner">
      <span class="announcement-badge">✦ 100% NATURAL SOLAR HARVEST</span>
      <p class="announcement-text">Unique Dual Magnesium Formula (253.14 g/L MgCl₂ &amp; 70.36 g/L MgSO₄) · FREE Express Delivery Across Australia on Orders Over $80</p>
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
        <a href="{depth_prefix}index.html#purity">Clinical Purity</a>
        <a href="{depth_prefix}index.html#journal">Wellness Journal</a>
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
          <img src="{depth_prefix}{prod['image']}" alt="{html.escape(prod['name'])}" style="max-width: 320px; width: 100%; height: auto; margin: 0 auto; display: block;">
        </div>

        <div>
          <span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B4833E;">{html.escape(prod['botanical'])}</span>
          <h1 style="font-family: 'Cormorant Garamond', serif; font-size: clamp(30px, 4vw, 44px); color: #162820; margin: 8px 0 14px; line-height: 1.15;">{html.escape(prod['name'])}</h1>
          <div style="display: flex; align-items: baseline; gap: 14px; margin-bottom: 20px;">
            <span style="font-size: 32px; font-weight: 800; color: #1E3A2F;">A$ {prod['priceAUD']} AUD</span>
            <span style="font-size: 14px; color: #5C6460;">· In Stock in Melbourne · Includes AU GST</span>
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
            <span style="display: inline-block; margin-top: 6px; color: #1E3A2F; font-weight: 600;">Producer: Azimut 6000 Ltd, Pomorie, Bulgaria · GTIN: {prod['gtin13']} · Lot № 04 · Distributed in Australia by Sotir Kichukov (<a href="https://cptmma.com/" style="color:#1E3A2F;">CPT MMA Melbourne</a>).</span>
          </div>
        </div>
      </div>

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


def build_post_html(post, all_posts, depth_prefix="../"):
    slug = post["slug"]
    canonical = f"https://anchialo.com/post/{slug}"
    title = post["title"]
    desc = post.get("description", title)
    date_pub = post.get("datePublished", "2026-06-08T06:02:36.172Z")[:10]
    date_mod = post.get("dateModified", date_pub)[:10]
    img_url = post.get("image", {}).get("url", "https://anchialo.com/assets/images/products/06_file_transp.png")

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
                "author": {
                    "@type": "Person",
                    "@id": "https://cptmma.com/#sotir",
                    "name": "Sotir Kichukov",
                    "url": "https://cptmma.com/"
                },
                "publisher": {
                    "@type": "Organization",
                    "@id": "https://anchialo.com/#business",
                    "name": "ANCHIALO Australia",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://anchialo.com/assets/images/products/06_file_transp.png"
                    }
                },
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": canonical
                }
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "ANCHIALO Store",
                        "item": "https://anchialo.com/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Clinical Journal",
                        "item": "https://anchialo.com/#journal"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": title,
                        "item": canonical
                    }
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
  <link rel="stylesheet" href="{depth_prefix}styles.css">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
  <div class="announcement-bar">
    <div class="container announcement-inner">
      <span class="announcement-badge">✦ POMORIE BALNEOLOGY RESEARCH</span>
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
        <a href="{depth_prefix}index.html#journal" style="color: #1E3A2F; text-decoration: none;">Clinical Journal</a>
      </nav>

      <span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B4833E;">BALNEOTHERAPY &amp; ATHLETIC RECOVERY · PUBLISHED {date_pub}</span>
      <h1 style="font-family: 'Cormorant Garamond', serif; font-size: clamp(30px, 4.5vw, 46px); color: #162820; margin: 10px 0 16px; line-height: 1.15;">{html.escape(title)}</h1>
      <div style="font-size: 14px; color: #5C6460; margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid #EAE4DA;">
        By <a href="https://cptmma.com/" style="color: #1E3A2F; font-weight: 600; text-decoration: none;">Sotir Kichukov</a> (ONE Championship Veteran &amp; Founder of CPT MMA Melbourne) · Pomorie Lake Balneology Archive
      </div>

      <img src="{img_url}" alt="{html.escape(title)}" style="width: 100%; max-height: 440px; object-fit: cover; border-radius: 16px; margin-bottom: 32px;">

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


def build_home_jsonld():
    item_elements = []
    for idx, prod in enumerate(PRODUCTS, start=1):
        canonical = f"https://anchialo.com/product-page/{prod['slug']}"
        item_elements.append({
            "@type": "ListItem",
            "position": idx,
            "item": {
                "@type": "Product",
                "@id": f"{canonical}#product",
                "name": prod["name"],
                "url": canonical,
                "sku": prod["sku"],
                "gtin13": prod["gtin13"],
                "image": f"https://anchialo.com/{prod['image']}",
                "description": prod["description"],
                "brand": {"@type": "Brand", "name": "ANCHIALO"},
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.9",
                    "bestRating": "5",
                    "ratingCount": "420"
                },
                "offers": {
                    "@type": "Offer",
                    "url": canonical,
                    "priceCurrency": "AUD",
                    "price": prod["priceAUD"],
                    "priceValidUntil": "2027-12-31",
                    "availability": "https://schema.org/InStock",
                    "itemCondition": "https://schema.org/NewCondition"
                }
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
                "description": "Authentic Bulgarian Black Sea natural balneotherapy. 100% natural Dual Magnesium gels (253.14 g/L MgCl2 & 70.36 g/L MgSO4) and pure topical oils harvested from Lake Pomorie. Official Australian Store ($49 AUD) dispatched from Melbourne.",
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
                "sameAs": [
                    "https://cptmma.com/",
                    "https://cptmma.com/magnesium",
                    "https://www.facebook.com/ProFighterAndCoach",
                    "https://www.instagram.com/sotir_kichukov/",
                    "https://www.tiktok.com/@sotir_kichukov"
                ],
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.9",
                    "bestRating": "5",
                    "ratingCount": "420",
                    "reviewCount": "420"
                }
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
                        "name": "Why choose transdermal magnesium over oral tablets?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Oral magnesium tablets frequently cause gastrointestinal upset, diarrhea, and poor absorption due to stomach acids and digestive limits. Transdermal magnesium chloride is absorbed directly through the skin's sweat glands and hair follicles into the local tissue and bloodstream, delivering targeted relief where your muscles need it most without digestive stress."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "How do I apply Anchialo Dual Magnesium Gel?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Massage a generous amount onto clean, dry skin on tired muscles, sore joints, or along the spine. Allow it to absorb for 30 minutes to several hours, or leave it on overnight for deeper relaxation. If faint salt crystals form, simply rinse with cool water."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "Will I feel a tingling sensation?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Because Anchialo contains a clinical concentration of over 250 g/L magnesium salts, a mild warming or tingling sensation during the first few applications is completely normal and indicates rapid microcirculation."
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
                            "text": "All stock is located in Melbourne under Sotir Kichukov. You can order directly online through anchialo.com ($49 AUD per jar) or message via WhatsApp (+61 423 269 586) for same-day local pickup at CPT MMA or Australia Post Express dispatch with tracking."
                        }
                    }
                ]
            }
        ]
    }
    return json.dumps(schema, ensure_ascii=False)


def update_index_and_app(posts):
    index_path = os.path.join(ROOT, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Upgrade <head> in index.html
    head_seo = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="google-site-verification" content="G2RuPksRn9KZ88AvHmiol_yZ1x-yz3LFeHwcCuFgjvI">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ANCHIALO — Pure Black Sea Balneology &amp; Certified Dual Magnesium ($49 AUD Melbourne)</title>
  <meta name="description" content="Authentic Bulgarian Black Sea natural balneotherapy. 100% natural Dual Magnesium gels (253.14 g/L MgCl2 &amp; 70.36 g/L MgSO4) and pure topical oils harvested from Lake Pomorie. Official Australian Store ($49 AUD) dispatched from Melbourne by Sotir Kichukov.">
  <link rel="canonical" href="https://anchialo.com/">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta property="og:type" content="website">
  <meta property="og:title" content="ANCHIALO — Pure Black Sea Balneology &amp; Certified Dual Magnesium ($49 AUD)">
  <meta property="og:description" content="100% natural Lake Pomorie Dual Magnesium gels (Arnica, Lavender, Rosemary, Juniper, Grape) &amp; pure brine oil. 253.14 g/L MgCl2. Dispatched from Melbourne across Australia.">
  <meta property="og:url" content="https://anchialo.com/">
  <meta property="og:image" content="https://anchialo.com/assets/images/products/06_file_transp.png">
  <meta property="og:site_name" content="ANCHIALO">
  <meta property="og:locale" content="en_AU">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="ANCHIALO — Pure Black Sea Balneology &amp; Certified Dual Magnesium">
  <meta name="twitter:description" content="100% natural Dual Magnesium gels and pure topical oils from Lake Pomorie. Official Australian Store ($49 AUD) in Melbourne.">
  <meta name="twitter:image" content="https://anchialo.com/assets/images/products/06_file_transp.png">
  <meta name="geo.region" content="AU-VIC">
  <meta name="geo.placename" content="Melbourne, Victoria">
  <meta name="ICBM" content="-37.8136, 144.9631">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="manifest" href="manifest.webmanifest">
  <script type="application/ld+json">{build_home_jsonld()}</script>"""

    # Replace everything from <!DOCTYPE html> up to <link rel="icon" type="image/x-icon" href="favicon.ico">
    marker = '<link rel="icon" type="image/x-icon" href="favicon.ico">'
    if marker in content:
        idx = content.index(marker) + len(marker)
        content = head_seo + content[idx:]

    # 2. Pre-render SSR product cards inside #productsGrid so crawlers see all 9 products immediately
    ssr_products = []
    for prod in PRODUCTS:
        wa_msg = urllib.parse.quote(f"Hi Sotir, I would like to order {prod['name']} (A$ {prod['priceAUD']} AUD). Please confirm delivery / Melbourne pickup.")
        ssr_products.append(f"""          <div class="product-card">
            <div class="product-thumb">
              <span class="product-flag">{html.escape(prod['badge'])}</span>
              <a href="product-page/{prod['slug']}" title="{html.escape(prod['name'])}"><img src="{prod['image']}" alt="{html.escape(prod['name'])}" loading="lazy"></a>
            </div>
            <div class="product-body">
              <h3 class="product-name"><a href="product-page/{prod['slug']}" style="color:inherit;text-decoration:none;">{html.escape(prod['name'])}</a></h3>
              <div class="product-price-row">
                <span class="price-main">A$ {prod['priceAUD']} AUD</span>
                <span class="price-unit">/ 300g Net</span>
              </div>
              <p class="product-desc">{html.escape(prod['description'])}</p>
              <div class="product-actions">
                <button class="btn-card-add" data-id="{prod['id']}"><span>Add to Bag</span></button>
                <a href="https://wa.me/61423269586?text={wa_msg}" target="_blank" rel="noopener" class="btn-card-wa" title="Order via WhatsApp">WhatsApp</a>
              </div>
            </div>
          </div>""")
    ssr_products_block = '<div class="products-grid" id="productsGrid">\n' + "\n".join(ssr_products) + '\n        </div>'

    old_prod_grid = """<div class="products-grid" id="productsGrid">
          <!-- Dynamically populated from CATALOG_PRODUCTS in app.js -->
        </div>"""
    old_prod_grid_crlf = old_prod_grid.replace("\n", "\r\n")
    if old_prod_grid_crlf in content:
        content = content.replace(old_prod_grid_crlf, ssr_products_block)
    elif old_prod_grid in content:
        content = content.replace(old_prod_grid, ssr_products_block)

    # 3. Pre-render SSR blog cards + full archive links inside #blogGrid
    ssr_blogs = []
    for idx, post in enumerate(posts[:6]):
        img_url = post.get("image", {}).get("url", "assets/images/products/06_file_transp.png")
        ssr_blogs.append(f"""          <div class="blog-card">
            <div class="blog-card-thumb">
              <a href="post/{post['slug']}"><img src="{img_url}" alt="{html.escape(post['title'])}" loading="lazy"></a>
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
    ssr_blog_block = (
        '<div class="blog-grid" id="blogGrid">\n'
        + "\n".join(ssr_blogs)
        + '\n        </div>\n'
        + f'        <nav aria-label="Complete Balneotherapy Research Archive" style="margin-top:28px; padding-top:20px; border-top:1px solid rgba(30,58,47,0.12);">\n'
        + f'          <strong style="display:block; font-size:12px; letter-spacing:0.12em; text-transform:uppercase; color:#5C6460; margin-bottom:10px;">Complete Clinical &amp; Balneotherapy Archive (16 Publications):</strong>\n'
        + archive_links
        + '\n        </nav>'
    )

    old_blog_grid = """<div class="blog-grid" id="blogGrid">
          <!-- Dynamically populated from data/blog_posts.json -->
        </div>"""
    old_blog_grid_crlf = old_blog_grid.replace("\n", "\r\n")
    if old_blog_grid_crlf in content:
        content = content.replace(old_blog_grid_crlf, ssr_blog_block)
    elif old_blog_grid in content:
        content = content.replace(old_blog_grid, ssr_blog_block)

    # 4. Link CPT MMA in footer
    content = content.replace(
        "CPT MMA High Performance Recovery<br>",
        '<a href="https://cptmma.com/" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline;">CPT MMA High Performance Recovery</a><br>'
    )

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 5. Update app.js to include slugs and crawlable links
    app_path = os.path.join(ROOT, "app.js")
    with open(app_path, "r", encoding="utf-8") as f:
        app_js = f.read()

    slug_map = {p["id"]: p["slug"] for p in PRODUCTS}
    for pid, pslug in slug_map.items():
        target = f"id: '{pid}',"
        replacement = f"id: '{pid}',\n      slug: '{pslug}',"
        if f"slug: '{pslug}'" not in app_js and target in app_js:
            app_js = app_js.replace(target, replacement, 1)

    app_js = app_js.replace(
        '<h3 class="product-name">${prod.name}</h3>',
        '<h3 class="product-name"><a href="product-page/${prod.slug || \'\'}" style="color:inherit;text-decoration:none;">${prod.name}</a></h3>'
    )
    app_js = app_js.replace(
        '<h3 class="blog-card-title">${post.title}</h3>',
        '<h3 class="blog-card-title"><a href="post/${post.slug || \'\'}" style="color:inherit;text-decoration:none;">${post.title}</a></h3>'
    )

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_js)


def main():
    posts = load_blog_posts()

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

    today = "2026-10-28"
    urls = [("https://anchialo.com/", today, "daily", "1.0")]
    for prod in PRODUCTS:
        urls.append((f"https://anchialo.com/product-page/{prod['slug']}", today, "weekly", "0.9"))
    for post in posts:
        d = post.get("dateModified", today)[:10]
        urls.append((f"https://anchialo.com/post/{post['slug']}", d, "monthly", "0.8"))

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

    update_index_and_app(posts)
    print(f"Successfully updated index.html, app.js, {len(PRODUCTS)} product pages, {len(posts)} blog pages, and sitemap.xml.")


if __name__ == "__main__":
    main()
