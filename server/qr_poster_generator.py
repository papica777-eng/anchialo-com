"""Print-ready A4 PDF & PNG Counter QR Partner Poster and USP Brochure Generator."""

import argparse
import os
import re
import fitz  # PyMuPDF
import qrcode

PINE = (0.106, 0.239, 0.204)
PINE_LIGHT = (0.93, 0.96, 0.95)
GOLD = (0.702, 0.510, 0.133)
GOLD_TEXT = (0.90, 0.78, 0.45)
CREAM = (0.98, 0.97, 0.95)
INK = (0.10, 0.14, 0.13)
MUTED = (0.28, 0.32, 0.34)
SUBTLE = (0.44, 0.48, 0.50)
WHITE = (1.0, 1.0, 1.0)
BORDER = (0.85, 0.83, 0.78)


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _asset_path(*parts: str) -> str:
    return os.path.join(_repo_root(), *parts)


def _make_qr_png(url: str, out_path: str) -> str:
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#1b3d34", back_color="#ffffff").convert("RGB")
    qr_img.save(out_path)
    return out_path


def _draw_header(page: fitz.Page, subtitle: str, badge_line: str, height: float = 148) -> None:
    page.draw_rect(fitz.Rect(0, 0, 595, 842), color=None, fill=CREAM)
    page.draw_rect(fitz.Rect(0, 0, 595, height), color=None, fill=PINE)
    page.draw_rect(fitz.Rect(42, height, 553, height + 3.5), color=None, fill=GOLD)
    page.insert_text((44, 52), "ANCHIALO", fontsize=32, color=WHITE, fontname="hebo")
    page.insert_text(
        (44, 74),
        "LAKE POMORIE DUAL MAGNESIUM · BULGARIAN BLACK SEA BALNEOLOGY",
        fontsize=9.5,
        color=GOLD_TEXT,
        fontname="hebo",
    )
    page.insert_text((44, 108), subtitle[:62], fontsize=13.5, color=(0.97, 0.97, 0.95), fontname="hebo")
    page.insert_text((44, 129), badge_line[:88], fontsize=9.2, color=(0.82, 0.88, 0.85), fontname="helv")


def _draw_footer(page: fitz.Page, line1: str, line2: str) -> None:
    page.draw_line((44, 774), (551, 774), color=BORDER, width=0.8)
    page.insert_text((44, 792), line1, fontsize=8.3, color=SUBTLE, fontname="helv")
    page.insert_text((44, 807), line2, fontsize=8.3, color=SUBTLE, fontname="helv")


def _draw_usp_pills(page: fitz.Page, top_y: float) -> None:
    """Draw 4 lab-verified USP metric cards across the page width."""
    cards = [
        ("323.5 g/L", "Dual Magnesium", "253.14 MgCl2 + 70.36 MgSO4"),
        ("pH 6.9", "Skin-Neutral", "Gentle everyday body care"),
        ("0.00 ppm", "Heavy Metals", "Pb / Cd / As below detection"),
        ("ISO 22716", "EU GMP Lot 04", "No Preservatives Added"),
    ]
    x0 = 44
    w = 120
    gap = 9
    for idx, (val, title, sub) in enumerate(cards):
        x = x0 + idx * (w + gap)
        rect = fitz.Rect(x, top_y, x + w, top_y + 62)
        page.draw_rect(rect, color=BORDER, fill=WHITE, width=0.9)
        page.draw_rect(fitz.Rect(x, top_y, x + w, top_y + 3), color=None, fill=GOLD)
        page.insert_text((x + 9, top_y + 22), val, fontsize=13, color=PINE, fontname="hebo")
        page.insert_text((x + 9, top_y + 37), title, fontsize=8.8, color=INK, fontname="hebo")
        page.insert_text((x + 9, top_y + 50), sub, fontsize=7.0, color=SUBTLE, fontname="helv")


def generate_qr_partner_poster(
    partner_code: str,
    partner_name: str,
    output_dir: str | None = None,
    store_url: str = "https://anchialo.com",
) -> dict[str, str]:
    """Generate a high-resolution A4 PDF and PNG reception counter poster embedding a tracked QR URL."""
    clean_code = re.sub(r"[^A-Z0-9_-]", "", partner_code.upper())[:24]
    if not clean_code:
        raise ValueError("partner_code must contain alphanumeric characters")

    out_root = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_posters")
    os.makedirs(out_root, exist_ok=True)

    target_url = f"{store_url.rstrip('/')}/?ref={clean_code}#collection"
    qr_png_path = _make_qr_png(target_url, os.path.join(out_root, f"qr_{clean_code}.png"))

    pdf_path = os.path.join(out_root, f"ANCHIALO_POSTER_{clean_code}.pdf")
    poster_png_path = os.path.join(out_root, f"ANCHIALO_POSTER_{clean_code}.png")

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    _draw_header(
        page,
        subtitle=f"Official Partner Counter Display: {partner_name[:42]}",
        badge_line="323.5 g/L Dual Magnesium (MgCl2 + MgSO4) · 300g Non-Drip Gel · Melbourne Ready Stock",
        height=148,
    )

    page.insert_text(
        (44, 184),
        "Why Athletes & Clinics Switch From Watery Sprays to ANCHIALO",
        fontsize=16.5,
        color=INK,
        fontname="hebo",
    )
    page.insert_text(
        (44, 203),
        "Try the counter tester on clean skin: silky massage glide that stays where you apply it — zero drip, zero crust.",
        fontsize=10.2,
        color=MUTED,
        fontname="helv",
    )

    _draw_usp_pills(page, top_y=218)

    # USP Comparison & Product Image Row
    usp_box = fitz.Rect(44, 294, 375, 422)
    page.draw_rect(usp_box, color=BORDER, fill=WHITE, width=0.9)
    page.insert_text((56, 314), "UNIQUE SELLING ADVANTAGE", fontsize=9.2, color=GOLD, fontname="hebo")
    bullets = [
        "• Hyper-Saline Lake Pomorie Concentrate — not dissolved synthetic flakes",
        "• Dual Salt Matrix: fast MgCl2 absorption + soothing MgSO4 skin feel",
        "• 5 Botanical Blends: Arnica, Lavender, Rosemary, Juniper, Grape",
        "• Zero Preservatives, Zero Parabens, Zero Artificial Dyes (ATA #267262)",
        "• Fast Melbourne Dispatch: A$49 (300g) · 2-Pack A$89 + Free Express >A$80",
    ]
    for idx, line in enumerate(bullets):
        page.insert_text((56, 333 + idx * 17.5), line, fontsize=8.8, color=INK, fontname="helv")

    hero_photo = _asset_path("assets", "images", "products", "09_file.png")
    if os.path.exists(hero_photo):
        page.draw_rect(fitz.Rect(387, 294, 551, 422), color=BORDER, fill=WHITE, width=0.9)
        page.insert_image(fitz.Rect(391, 298, 547, 418), filename=hero_photo, keep_proportion=True)

    # Central QR Scan Card
    page.draw_rect(fitz.Rect(96, 442, 499, 756), color=GOLD, fill=WHITE, width=1.8)
    page.insert_image(fitz.Rect(184, 456, 410, 682), filename=qr_png_path)
    page.insert_text(
        (134, 706),
        f"SCAN TO ORDER + UNLOCK 10% OFF: CODE {clean_code}",
        fontsize=12.5,
        color=PINE,
        fontname="hebo",
    )
    page.insert_text(
        (148, 726),
        "Apple Pay, Card or PayPal in 10 seconds · Dispatched fast from Melbourne",
        fontsize=9.3,
        color=MUTED,
        fontname="helv",
    )
    page.insert_text(
        (140, 744),
        f"Direct Link: {target_url}",
        fontsize=8.3,
        color=SUBTLE,
        fontname="helv",
    )

    _draw_footer(
        page,
        "External cosmetic body care only. Verified Lot 04 · ISO 22716 GMP · BDS 8840:1971 · Zero Heavy Metals.",
        "Australian Distribution: Sotir Kichukov · CPT MMA Melbourne · WhatsApp +61 423 269 586",
    )

    doc.save(pdf_path)
    pix = page.get_pixmap(dpi=150)
    pix.save(poster_png_path)
    doc.close()

    return {
        "partner_code": clean_code,
        "target_url": target_url,
        "qr_png_path": qr_png_path,
        "pdf_path": pdf_path,
        "poster_png_path": poster_png_path,
    }


def generate_brand_usp_brochures(
    output_dir: str | None = None,
    store_url: str = "https://anchialo.com",
) -> dict[str, str]:
    """Generate customer Product & Mineral Guide PDF and B2B Partner Wholesale Guide PDF."""
    out_root = output_dir or _asset_path("assets", "brochures")
    os.makedirs(out_root, exist_ok=True)

    product_pdf = os.path.join(out_root, "ANCHIALO_Product_Guide_AU.pdf")
    partner_pdf = os.path.join(out_root, "ANCHIALO_Partner_Wholesale_Guide_AU.pdf")
    qr_store = _make_qr_png(f"{store_url.rstrip('/')}/#collection", os.path.join(out_root, "_qr_store.png"))
    qr_partner = _make_qr_png(f"{store_url.rstrip('/')}/#partners", os.path.join(out_root, "_qr_partner.png"))

    # -------------------- 1. CUSTOMER PRODUCT & USP GUIDE (2 PAGES) --------------------
    doc = fitz.open()
    p1 = doc.new_page(width=595, height=842)
    _draw_header(
        p1,
        subtitle="Australian Product & Mineral Dossier · Dual Magnesium Body Care",
        badge_line="Lake Pomorie Hyper-Saline Concentrate · ISO 22716 GMP · Melbourne Ready Stock",
        height=144,
    )

    p1.insert_text(
        (44, 180),
        "The Anchialo Difference: 323.5 g/L Natural Dual Magnesium",
        fontsize=16,
        color=INK,
        fontname="hebo",
    )
    p1.insert_text(
        (44, 200),
        "Harvested through natural solar evaporation in Bulgaria's protected Lake Pomorie salterns, Anchialo",
        fontsize=10,
        color=MUTED,
        fontname="helv",
    )
    p1.insert_text(
        (44, 214),
        "combines fast-absorbing Magnesium Chloride and skin-soothing Magnesium Sulfate in a silky cosmetic gel.",
        fontsize=10,
        color=MUTED,
        fontname="helv",
    )
    _draw_usp_pills(p1, top_y=230)

    # Studio Hero Photo + USP Comparison Table
    trio_img = _asset_path("assets", "images", "products", "09_file.png")
    if os.path.exists(trio_img):
        p1.draw_rect(fitz.Rect(44, 308, 285, 512), color=BORDER, fill=WHITE, width=0.9)
        p1.insert_image(fitz.Rect(48, 312, 281, 508), filename=trio_img, keep_proportion=True)

    comp_rect = fitz.Rect(298, 308, 551, 512)
    p1.draw_rect(comp_rect, color=BORDER, fill=WHITE, width=0.9)
    p1.draw_rect(fitz.Rect(298, 308, 551, 336), color=None, fill=PINE)
    p1.insert_text((310, 326), "WHY GEL BEATS MAGNESIUM SPRAYS", fontsize=9.8, color=WHITE, fontname="hebo")
    comp_rows = [
        ("Texture & Hold", "Smooth massage glide; zero watery drip"),
        ("Dual Matrix", "253.14 g/L MgCl2 + 70.36 g/L MgSO4"),
        ("Origin", "Natural Pomorie solar brine (not flakes)"),
        ("Clean Label", "Zero preservatives, zero parabens, pH 6.9"),
        ("Heavy Metals", "0.00 ppm Pb / Cd / As (ATA #267262)"),
        ("Value & Size", "300g jar lasts 6-8 weeks (A$49 AUD)"),
    ]
    for idx, (label, val) in enumerate(comp_rows):
        y = 354 + idx * 25
        p1.insert_text((310, y), label, fontsize=8.8, color=PINE, fontname="hebo")
        p1.insert_text((310, y + 11), val, fontsize=8.3, color=MUTED, fontname="helv")

    # Verified Lab Assay Summary Box
    p1.draw_rect(fitz.Rect(44, 530, 551, 748), color=BORDER, fill=PINE_LIGHT, width=0.9)
    p1.insert_text((58, 552), "OFFICIAL LABORATORY VERIFICATION (LOT 04 · ATA #267262)", fontsize=10.5, color=PINE, fontname="hebo")
    assay_lines = [
        "• Magnesium Chloride (MgCl2): 253.14 g/L (BDS 8840:1971 Standard Norm: 185-285 g/L)",
        "• Magnesium Sulfate (MgSO4): 70.36 g/L (Lab Method 2/2009 Standard Norm: 55-95 g/L)",
        "• Physiological pH Balance: 6.9 neutral (gentle on sensitive skin; zero synthetic fragrance overload)",
        "• Microbiological & Heavy Metal Purity: 0.00 ppm Lead, Cadmium, Arsenic (EU Pharmacopoeia compliant)",
        "• Manufacturing Standard: Small-batch blended by Azimut 6000 Ltd under ISO 22716 Cosmetic GMP",
        "• Australian Fulfillment: Ready stock in Melbourne · Express Australia Post · Free shipping over A$80",
    ]
    for idx, line in enumerate(assay_lines):
        p1.insert_text((58, 576 + idx * 24), line, fontsize=9.2, color=INK, fontname="helv")

    _draw_footer(
        p1,
        "External cosmetic body care only. Not intended to diagnose, treat, cure, or prevent any disease.",
        "Page 1 of 2 · Order online at https://anchialo.com · Melbourne Dispatch: +61 423 269 586",
    )

    # Page 2: Complete 5-Blend + Oil Matrix & Value Packs
    p2 = doc.new_page(width=595, height=842)
    _draw_header(
        p2,
        subtitle="Complete Collection Matrix, Ritual Protocol & Value Packs",
        badge_line="5 Botanical Dual Magnesium Gels (300g) · Pure Black Sea Lye Oil (300ml) · Combos",
        height=126,
    )

    blends = [
        ("Arnica Blend (300g Gel / 300ml Oil)", "Daytime post-training massage", "Warm botanical comfort after heavy mat, gym & leg sessions."),
        ("Lavender Blend (300g Gel)", "Evening wind-down ritual", "Bulgarian Lavandula aroma crafted for calm pre-sleep massage."),
        ("Rosemary Blend (300g Gel / 300ml Oil)", "Morning & pre-session refresh", "Crisp herbal invigoration for active mornings & warm-ups."),
        ("Juniper Blend (300g Gel)", "Deep lower-body refresh", "Alpine juniper extract for heavy legs, feet & long work shifts."),
        ("Red Grape Blend (300g Gel)", "Skin conditioning & glow", "Antioxidant-rich grape extract leaving skin soft and velvety."),
        ("Pure Dual Magnesium Oil (300ml)", "Unscented studio & soak", "Silky liquid brine for full-body massage or mineral foot soaks."),
    ]
    y_cursor = 152
    for title, tag, desc in blends:
        p2.draw_rect(fitz.Rect(44, y_cursor, 551, y_cursor + 46), color=BORDER, fill=WHITE, width=0.8)
        p2.insert_text((56, y_cursor + 18), title, fontsize=10, color=PINE, fontname="hebo")
        p2.insert_text((340, y_cursor + 18), tag.upper(), fontsize=8.0, color=GOLD, fontname="hebo")
        p2.insert_text((56, y_cursor + 35), desc, fontsize=8.8, color=MUTED, fontname="helv")
        y_cursor += 53

    # Combos + Oil/Gel Duo Photo
    duo_img = _asset_path("assets", "images", "products", "02_file.png")
    if os.path.exists(duo_img):
        p2.draw_rect(fitz.Rect(44, 480, 224, 676), color=BORDER, fill=WHITE, width=0.9)
        p2.insert_image(fitz.Rect(48, 484, 220, 672), filename=duo_img, keep_proportion=True)

    p2.draw_rect(fitz.Rect(236, 480, 551, 588), color=BORDER, fill=WHITE, width=0.9)
    p2.insert_text((248, 500), "AUSTRALIAN VALUE PACKS (AUD)", fontsize=9.8, color=GOLD, fontname="hebo")
    packs = [
        "• Single 300g Gel or 300ml Oil: A$49.00",
        "• 1+1 Special Offer (Gel + Oil Combo): A$49.00 (Free 300ml Oil)",
        "• Day & Night 2-Pack (600g): A$89.00 + FREE Express Shipping",
        "• Combat Team 3-Pack (900g): A$129.00 + FREE Express Shipping",
    ]
    for idx, line in enumerate(packs):
        p2.insert_text((248, 520 + idx * 16.5), line, fontsize=9.0, color=INK, fontname="helv")

    p2.draw_rect(fitz.Rect(236, 598, 551, 676), color=BORDER, fill=PINE_LIGHT, width=0.9)
    p2.insert_text((248, 616), "3-STEP COSMETIC APPLICATION", fontsize=9.5, color=PINE, fontname="hebo")
    p2.insert_text((248, 633), "1. Apply a generous layer to clean skin & massage 2-3 minutes.", fontsize=8.6, color=INK, fontname="helv")
    p2.insert_text((248, 648), "2. Leave on 20-30 minutes (or overnight for deep conditioning).", fontsize=8.6, color=INK, fontname="helv")
    p2.insert_text((248, 663), "3. Rinse lightly with warm water or towel off excess mineral salt.", fontsize=8.6, color=INK, fontname="helv")

    # Bottom QR CTA
    p2.draw_rect(fitz.Rect(44, 690, 551, 762), color=GOLD, fill=WHITE, width=1.4)
    p2.insert_image(fitz.Rect(52, 695, 114, 757), filename=qr_store)
    p2.insert_text((128, 718), "ORDER ONLINE WITH EXPRESS MELBOURNE DISPATCH", fontsize=11, color=PINE, fontname="hebo")
    p2.insert_text((128, 736), "Scan to shop all 5 blends & combo offers at https://anchialo.com/#collection", fontsize=9.2, color=MUTED, fontname="helv")
    p2.insert_text((128, 751), "Free Australia Post Express shipping on orders over A$80 · Apple Pay / Card / PayPal", fontsize=8.5, color=SUBTLE, fontname="helv")

    _draw_footer(
        p2,
        "External cosmetic body care only. Verified Lot 04 · ISO 22716 GMP · BDS 8840:1971.",
        "Page 2 of 2 · Australian Fulfillment: Melbourne VIC · WhatsApp +61 423 269 586",
    )
    doc.save(product_pdf)
    doc.close()

    # -------------------- 2. B2B PARTNER & WHOLESALE GUIDE (1 PAGE) --------------------
    b2b = fitz.open()
    bp = b2b.new_page(width=595, height=842)
    _draw_header(
        bp,
        subtitle="Melbourne Gym, MMA & Clinic Partner Program (Zero-Risk Model)",
        badge_line="Counter QR Stand + Free 300g Tester · Automated 18-20% Commission · Wholesale Cartons",
        height=144,
    )

    bp.insert_text(
        (44, 180),
        "Turn Reception Foot Traffic Into Recurring Margin — With Zero Inventory Risk",
        fontsize=15.5,
        color=INK,
        fontname="hebo",
    )
    bp.insert_text(
        (44, 200),
        "Built for Melbourne MMA/BJJ academies, boxing gyms, myotherapy studios, and sports physio clinics.",
        fontsize=10,
        color=MUTED,
        fontname="helv",
    )

    # Two Option Cards
    bp.draw_rect(fitz.Rect(44, 218, 290, 398), color=GOLD, fill=WHITE, width=1.5)
    bp.draw_rect(fitz.Rect(44, 218, 290, 246), color=None, fill=PINE)
    bp.insert_text((56, 236), "OPTION A: ZERO-RISK QR COUNTER STAND", fontsize=9.2, color=WHITE, fontname="hebo")
    opt_a = [
        "• Upfront Cost: A$0.00 (Free 300g tester + A4 poster)",
        "• Member Offer: Instant 10% OFF via your gym code",
        "• Partner Payout: 18-20% commission per order",
        "• Fulfillment: We pack, ship & handle support",
        "• Tracking: Real-time live partner dashboard",
        "• Ideal for: Reception desks & athlete lounges",
    ]
    for idx, line in enumerate(opt_a):
        bp.insert_text((56, 268 + idx * 20), line, fontsize=8.8, color=INK, fontname="helv")

    bp.draw_rect(fitz.Rect(305, 218, 551, 398), color=BORDER, fill=WHITE, width=1.0)
    bp.draw_rect(fitz.Rect(305, 218, 551, 246), color=None, fill=GOLD)
    bp.insert_text((317, 236), "OPTION B: CLINIC & PRO SHOP WHOLESALE", fontsize=9.2, color=WHITE, fontname="hebo")
    opt_b = [
        "• Retail RRP: A$49.00 per 300g jar / 300ml oil",
        "• Starter Box (12 Units): Strong pro-shop margin",
        "• Studio Cabin Use: Ideal for deep tissue massage",
        "• Zero-Drip Formula: Clean linen, zero sticky oil film",
        "• Local Stock: Same/next-day Melbourne courier",
        "• Lab Dossier: Full EU GMP & ATA #267262 pack",
    ]
    for idx, line in enumerate(opt_b):
        bp.insert_text((317, 268 + idx * 20), line, fontsize=8.8, color=INK, fontname="helv")

    # Visual + Why Members Reorder
    pair_img = _asset_path("assets", "images", "products", "05_file.png")
    if os.path.exists(pair_img):
        bp.draw_rect(fitz.Rect(44, 414, 248, 608), color=BORDER, fill=WHITE, width=0.9)
        bp.insert_image(fitz.Rect(48, 418, 244, 604), filename=pair_img, keep_proportion=True)

    bp.draw_rect(fitz.Rect(262, 414, 551, 608), color=BORDER, fill=PINE_LIGHT, width=0.9)
    bp.insert_text((276, 436), "WHY MEMBERS & THERAPISTS PREFER ANCHIALO", fontsize=9.8, color=PINE, fontname="hebo")
    reasons = [
        "1. Instant Try-Before-Buy: Members feel the silky, warming",
        "   mineral glide at reception and scan in 10 seconds.",
        "2. 323.5 g/L Dual Magnesium: High-density Black Sea brine",
        "   without the stinging mist or watery mess of sprays.",
        "3. Clean Cosmetic Compliance: Zero medical claims, pure",
        "   ISO 22716 GMP body care with 0.00 ppm heavy metals.",
        "4. High Repeat Rate: 300g jar drives 6-8 week reorders.",
    ]
    for idx, line in enumerate(reasons):
        bp.insert_text((276, 458 + idx * 20), line, fontsize=8.9, color=INK, fontname="helv")

    # Partner Activation Box
    bp.draw_rect(fitz.Rect(44, 626, 551, 756), color=GOLD, fill=WHITE, width=1.6)
    bp.insert_image(fitz.Rect(54, 634, 162, 742), filename=qr_partner)
    bp.insert_text((178, 656), "CLAIM YOUR FREE MELBOURNE PARTNER TESTER KIT", fontsize=12, color=PINE, fontname="hebo")
    bp.insert_text((178, 678), "Direct Australian Contact: Sotir Kichukov (CPT MMA Melbourne)", fontsize=9.8, color=INK, fontname="hebo")
    bp.insert_text((178, 698), "WhatsApp / Call: +61 423 269 586 · Web: https://anchialo.com/#partners", fontsize=9.3, color=MUTED, fontname="helv")
    bp.insert_text((178, 718), "We deliver your custom QR counter stand + 300g tester jar within 24-48h in Melbourne.", fontsize=9.0, color=SUBTLE, fontname="helv")
    bp.insert_text((178, 738), "External cosmetic body care only · Verified Lot 04 · ISO 22716 GMP.", fontsize=8.4, color=SUBTLE, fontname="helv")

    _draw_footer(
        bp,
        "External cosmetic body care only. Verified Lot 04 · ISO 22716 GMP · BDS 8840:1971 · Zero Heavy Metals.",
        "Anchialo Australia B2B Program · Melbourne VIC · WhatsApp +61 423 269 586",
    )
    b2b.save(partner_pdf)
    b2b.close()

    for tmp_qr in (qr_store, qr_partner):
        if os.path.exists(tmp_qr):
            os.remove(tmp_qr)

    return {
        "product_guide_pdf": product_pdf,
        "partner_guide_pdf": partner_pdf,
    }


def optimize_web_product_images(max_dim: int = 900, quality: int = 82) -> list[dict[str, object]]:
    """Generate lightweight WebP derivatives in assets/images/products/web/ and assets/images/web/."""
    from PIL import Image

    results: list[dict[str, object]] = []
    targets = [
        (_asset_path("assets", "images", "products"), max_dim),
        (_asset_path("assets", "images"), 1440),
    ]
    for src_dir, dim in targets:
        web_dir = os.path.join(src_dir, "web")
        os.makedirs(web_dir, exist_ok=True)
        for name in sorted(os.listdir(src_dir)):
            if not name.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            src_path = os.path.join(src_dir, name)
            stem = os.path.splitext(name)[0]
            out_path = os.path.join(web_dir, f"{stem}.webp")
            with Image.open(src_path) as im:
                im.thumbnail((dim, dim), Image.Resampling.LANCZOS)
                mode = "RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB"
                converted = im.convert(mode)
                converted.save(out_path, "WEBP", quality=quality, method=6)
                w, h = converted.size
            results.append(
                {
                    "file": f"{os.path.relpath(out_path, _asset_path())}",
                    "width": w,
                    "height": h,
                    "kb": round(os.path.getsize(out_path) / 1024, 1),
                }
            )
    return results


def main() -> None:
    """CLI entrypoint for generating Melbourne QR partner posters, USP brochures, and WebP assets."""
    parser = argparse.ArgumentParser(description="Generate ANCHIALO Melbourne QR partner poster & USP brochures")
    parser.add_argument("--code", help="Partner promo code (e.g., CPT15, RENEGADE15)")
    parser.add_argument("--name", help="Partner gym or clinic display name")
    parser.add_argument("--out", default=None, help="Output directory")
    parser.add_argument("--brochures", action="store_true", help="Also generate customer & partner USP brochures")
    parser.add_argument("--optimize-web", action="store_true", help="Generate lightweight WebP product images")
    args = parser.parse_args()
    if args.code and args.name:
        result = generate_qr_partner_poster(args.code, args.name, output_dir=args.out)
        print(f"Generated poster: {result['pdf_path']} ({result['target_url']})")
    if args.brochures or not (args.code and args.name or args.optimize_web):
        brochures = generate_brand_usp_brochures(output_dir=args.out)
        print(f"Generated brochures: {brochures['product_guide_pdf']} & {brochures['partner_guide_pdf']}")
    if args.optimize_web:
        items = optimize_web_product_images()
        for item in items:
            print(f"{item['file']}: {item['width']}x{item['height']} ({item['kb']} KB)")


if __name__ == "__main__":
    main()
