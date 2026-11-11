"""Print-ready A4 PDF & PNG Counter QR Partner Poster Generator for Melbourne gyms and clinics."""

import argparse
import os
import re
import fitz  # PyMuPDF
import qrcode


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
    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=2)
    qr.add_data(target_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#1b3d34", back_color="#ffffff").convert("RGB")

    qr_png_path = os.path.join(out_root, f"qr_{clean_code}.png")
    qr_img.save(qr_png_path)

    # Create A4 PDF (595 x 842 pt) using PyMuPDF
    pdf_path = os.path.join(out_root, f"ANCHIALO_POSTER_{clean_code}.pdf")
    poster_png_path = os.path.join(out_root, f"ANCHIALO_POSTER_{clean_code}.png")

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # Background canvas
    page.draw_rect(fitz.Rect(0, 0, 595, 842), color=None, fill=(0.98, 0.97, 0.95))
    # Header deep pine band
    page.draw_rect(fitz.Rect(0, 0, 595, 165), color=None, fill=(0.106, 0.239, 0.204))
    # Gold divider
    page.draw_rect(fitz.Rect(42, 165, 553, 169), color=None, fill=(0.702, 0.510, 0.133))

    page.insert_text((45, 58), "ANCHIALO", fontsize=34, color=(1, 1, 1), fontname="helv")
    page.insert_text(
        (45, 86),
        "LAKE POMORIE DUAL MAGNESIUM · BULGARIAN BLACK SEA MINERALS",
        fontsize=10.5,
        color=(0.90, 0.78, 0.45),
        fontname="helv",
    )
    page.insert_text(
        (45, 122),
        f"Official Partner Display: {partner_name[:46]}",
        fontsize=14,
        color=(0.96, 0.96, 0.94),
        fontname="helv",
    )
    page.insert_text(
        (45, 144),
        "253.14 g/L Magnesium Chloride + 70.36 g/L Magnesium Sulfate · 300g Non-Drip Cosmetic Gel",
        fontsize=9.5,
        color=(0.82, 0.87, 0.85),
        fontname="helv",
    )

    page.insert_text(
        (45, 222),
        "Post-Training Body Care & Evening Wind-Down Ritual",
        fontsize=20,
        color=(0.10, 0.14, 0.13),
        fontname="helv",
    )
    page.insert_text(
        (45, 252),
        "Try the counter tester on clean skin — fast-absorbing, smooth massage glide with zero spray drip.",
        fontsize=11.5,
        color=(0.28, 0.32, 0.34),
        fontname="helv",
    )
    page.insert_text(
        (45, 274),
        "• 5 Botanical Blends: Arnica Montana, Bulgarian Lavender, Garden Rosemary, Alpine Juniper, Grape",
        fontsize=10.5,
        color=(0.22, 0.26, 0.28),
        fontname="helv",
    )
    page.insert_text(
        (45, 294),
        "• Stocked right here in Melbourne (Dispatched fast via Australia Post or CPT MMA pickup)",
        fontsize=10.5,
        color=(0.22, 0.26, 0.28),
        fontname="helv",
    )

    # Central QR card
    page.draw_rect(fitz.Rect(110, 330, 485, 685), color=(0.702, 0.510, 0.133), fill=(1, 1, 1), width=1.8)
    page.insert_image(fitz.Rect(172, 355, 422, 605), filename=qr_png_path)
    page.insert_text(
        (145, 634),
        f"SCAN TO ORDER + UNLOCK 10% OFF: CODE {clean_code}",
        fontsize=13,
        color=(0.106, 0.239, 0.204),
        fontname="helv",
    )
    page.insert_text(
        (165, 658),
        "Pay with Apple Pay, Card or PayPal in 10 seconds · A$49 / 2-Pack A$89",
        fontsize=9.5,
        color=(0.35, 0.39, 0.41),
        fontname="helv",
    )

    # Footer
    page.insert_text(
        (45, 742),
        f"Direct URL: {target_url}",
        fontsize=9.5,
        color=(0.35, 0.39, 0.41),
        fontname="helv",
    )
    page.insert_text(
        (45, 766),
        "External cosmetic body care only. Verified Lot 04 · ISO 22716 GMP · BDS 8840:1971 · Zero Heavy Metals.",
        fontsize=8.5,
        color=(0.45, 0.48, 0.50),
        fontname="helv",
    )
    page.insert_text(
        (45, 786),
        "Australian Distribution: Sotir Kichukov · CPT MMA Melbourne · WhatsApp +61 423 269 586",
        fontsize=8.5,
        color=(0.45, 0.48, 0.50),
        fontname="helv",
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


def main() -> None:
    """CLI entrypoint for generating Melbourne partner QR posters."""
    parser = argparse.ArgumentParser(description="Generate ANCHIALO Melbourne QR partner poster PDF & PNG")
    parser.add_argument("--code", required=True, help="Partner promo code (e.g., CPT15, RENEGADE15)")
    parser.add_argument("--name", required=True, help="Partner gym or clinic display name")
    parser.add_argument("--out", default=None, help="Output directory")
    args = parser.parse_args()
    result = generate_qr_partner_poster(args.code, args.name, output_dir=args.out)
    print(f"Generated poster: {result['pdf_path']} ({result['target_url']})")


if __name__ == "__main__":
    main()

