import os
import fitz # PyMuPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REDESIGN_DIR = os.path.join(BASE_DIR, "labels", "redesigned")
SVG_DIR = os.path.join(REDESIGN_DIR, "svg")
PNG_DIR = os.path.join(REDESIGN_DIR, "renders")
PDF_DIR = os.path.join(REDESIGN_DIR, "pdf")

for d in [SVG_DIR, PNG_DIR, PDF_DIR]:
    os.makedirs(d, exist_ok=True)

VARIANTS = {
    "Arnica": {
        "bg_accent": "#D4AF37",
        "badge_color": "#B8860B",
        "light_accent": "#FDF8E8",
        "tagline": "ARNICA BLEND",
        "inci": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Glycerine, Hydroxyethylcellulose, Arnica Montana Flower Extract."
    },
    "Grape": {
        "bg_accent": "#722F37",
        "badge_color": "#581820",
        "light_accent": "#F8ECED",
        "tagline": "GRAPE BLEND",
        "inci": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Glycerine, Hydroxyethylcellulose, Parfum (Natural Fragrance)."
    },
    "Juniper": {
        "bg_accent": "#2E5D4B",
        "badge_color": "#1C3F32",
        "light_accent": "#EDF5F1",
        "tagline": "JUNIPER BLEND",
        "inci": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Hydroxyethylcellulose, Parfum (Natural Fragrance), Glycerine, Juniperus Chinensis Leaf Extract."
    },
    "Lavender": {
        "bg_accent": "#6A5ACD",
        "badge_color": "#483D8B",
        "light_accent": "#F1EEF9",
        "tagline": "LAVENDER BLEND",
        "inci": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Glycerine, Hydroxyethylcellulose, Lavandula Angustifolia Flower Extract."
    },
    "Rosemary": {
        "bg_accent": "#4A6B3D",
        "badge_color": "#2E4724",
        "light_accent": "#EEF5EB",
        "tagline": "ROSEMARY BLEND",
        "inci": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Glycerine, Hydroxyethylcellulose, Rosmarinus Officinalis Leaf Powder Extract."
    }
}

def generate_top_lid_svg(variant_name, data):
    accent = data["bg_accent"]
    badge_col = data["badge_color"]
    tag = data["tagline"]
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">
  <defs>
    <radialGradient id="porcelain" cx="50%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="70%" stop-color="#FBF9F5"/>
      <stop offset="100%" stop-color="#F0EBE1"/>
    </radialGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E2C275"/>
      <stop offset="50%" stop-color="#C5A059"/>
      <stop offset="100%" stop-color="#9C7A32"/>
    </linearGradient>
    <filter id="softGlow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.08"/>
    </filter>
    <path id="topArc" d="M 180,500 A 320,320 0 0,1 820,500" fill="none"/>
    <path id="bottomArc" d="M 820,500 A 320,320 0 0,1 180,500" fill="none"/>
  </defs>

  <!-- Circular Die Cut Line -->
  <circle cx="500" cy="500" r="490" fill="url(#porcelain)" stroke="url(#gold)" stroke-width="4"/>
  <circle cx="500" cy="500" r="465" fill="none" stroke="{accent}" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.6"/>
  <circle cx="500" cy="500" r="455" fill="none" stroke="url(#gold)" stroke-width="1"/>

  <!-- Top Curved Text -->
  <text font-family="'Cinzel', 'Playfair Display', 'Georgia', serif" font-size="22" letter-spacing="4" fill="#3A3834" font-weight="600">
    <textPath href="#topArc" startOffset="50%" text-anchor="middle">
      MAGNESIUM CHLORIDE &amp; MAGNESIUM SULFATE
    </textPath>
  </text>

  <!-- Bottom Curved Text -->
  <text font-family="'Cinzel', 'Playfair Display', 'Georgia', serif" font-size="20" letter-spacing="5" fill="#5A554E">
    <textPath href="#bottomArc" startOffset="50%" text-anchor="middle">
      POMORIE HYPERSALINE LAGOON · ANCIENT ANCHIALO
    </textPath>
  </text>

  <!-- Central Crest / Brand Mark -->
  <g transform="translate(500, 260)" text-anchor="middle">
    <!-- Stylized Mineral Waves Glyph -->
    <path d="M -40,-25 Q -20,-35 0,-25 Q 20,-15 40,-25 M -40,-15 Q -20,-25 0,-15 Q 20,-5 40,-15" fill="none" stroke="url(#gold)" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="0" cy="-40" r="3" fill="url(#gold)"/>
    
    <!-- ANCHIALO Logo -->
    <text y="40" font-family="'Cinzel', 'Trajan Pro', 'Cormorant Garamond', 'Times New Roman', serif" font-size="64" letter-spacing="14" fill="#24211D" font-weight="700">
      ANCHIALO
    </text>
    <text y="75" font-family="'Montserrat', 'Inter', sans-serif" font-size="14" letter-spacing="8" fill="#8C8275" font-weight="500">
      BALNEOTHERAPY LABS · EST. POMORIE
    </text>
  </g>

  <!-- Middle Divider -->
  <line x1="280" y1="400" x2="720" y2="400" stroke="url(#gold)" stroke-width="1.5"/>
  <polygon points="500,396 505,400 500,404 495,400" fill="url(#gold)"/>

  <!-- Main Product Title -->
  <g transform="translate(500, 480)" text-anchor="middle">
    <text font-family="'Cinzel', 'Playfair Display', serif" font-size="44" letter-spacing="6" fill="#1C1A18" font-weight="700">
      DUAL MAGNESIUM GEL
    </text>
    <text y="38" font-family="'Montserrat', 'Inter', sans-serif" font-size="18" letter-spacing="4" fill="#55514B">
      NATURAL TRANSDERMAL THERAPY
    </text>
  </g>

  <!-- Botanical Badge -->
  <g transform="translate(500, 595)">
    <rect x="-180" y="-30" width="360" height="60" rx="30" fill="{accent}" filter="url(#softGlow)"/>
    <rect x="-176" y="-26" width="352" height="52" rx="26" fill="none" stroke="#FFFFFF" stroke-width="1" opacity="0.4"/>
    <text y="8" text-anchor="middle" font-family="'Montserrat', 'Inter', sans-serif" font-size="22" letter-spacing="5" fill="#FFFFFF" font-weight="700">
      {tag}
    </text>
  </g>

  <!-- Lower Details & Purity Guarantee -->
  <g transform="translate(500, 715)" text-anchor="middle">
    <text font-family="'Montserrat', 'Inter', sans-serif" font-size="16" letter-spacing="3" fill="#4A453E" font-weight="600">
      100% PURE BLACK SEA LYE MINERALS · ZERO PRESERVATIVES
    </text>
    <text y="32" font-family="'Montserrat', 'Inter', sans-serif" font-size="14" letter-spacing="2" fill="#7A7369">
      FAST TRANSDERMAL ABSORPTION · MUSCLE &amp; JOINT RECOVERY
    </text>
    <text y="65" font-family="'Cinzel', serif" font-size="20" letter-spacing="6" fill="#C5A059" font-weight="700">
      300 g ℮
    </text>
  </g>
</svg>"""
    return svg

def generate_side_label_svg(variant_name, data):
    accent = data["bg_accent"]
    badge_col = data["badge_color"]
    tag = data["tagline"]
    inci = data["inci"]
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3000 480" width="3000" height="480">
  <defs>
    <linearGradient id="sideBg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FAF8F5"/>
      <stop offset="70%" stop-color="#FAF8F5"/>
      <stop offset="100%" stop-color="#F3EFE9"/>
    </linearGradient>
    <linearGradient id="goldH" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#C5A059"/>
      <stop offset="50%" stop-color="#E5C77C"/>
      <stop offset="100%" stop-color="#C5A059"/>
    </linearGradient>
    <linearGradient id="variantBar" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{badge_col}"/>
      <stop offset="100%" stop-color="{accent}"/>
    </linearGradient>
  </defs>

  <!-- Background Base -->
  <rect width="3000" height="480" fill="url(#sideBg)"/>
  
  <!-- Subtle Border Lines Top and Bottom -->
  <line x1="0" y1="12" x2="3000" y2="12" stroke="url(#goldH)" stroke-width="2"/>
  <line x1="0" y1="468" x2="3000" y2="468" stroke="url(#goldH)" stroke-width="2"/>

  <!-- Top Accent Ribbon -->
  <rect x="0" y="14" width="3000" height="28" fill="{accent}"/>
  <text x="1500" y="33" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="13" font-weight="700" letter-spacing="4" fill="#FFFFFF">
    ANCHIALO MEDICAL BALNEOTHERAPY · NATURAL TOPICAL GEL WITH MAGNESIUM CHLORIDE &amp; MAGNESIUM SULFATE
  </text>

  <!-- ==================== SECTION 1: KEY BENEFITS (Left) ==================== -->
  <g transform="translate(60, 80)">
    <rect x="0" y="0" width="160" height="26" rx="4" fill="{accent}"/>
    <text x="80" y="17" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="#FFFFFF">
      KEY BENEFITS
    </text>
    <text x="0" y="55" font-family="'Inter', sans-serif" font-size="14" fill="#2E2C29" width="600">
      <tspan x="0" dy="0" font-weight="600">• Fast-absorbing transdermal mineral therapy delivering natural Magnesium.</tspan>
      <tspan x="0" dy="24">• Relieves acute muscle cramps, spasms, stiffness, and joint fatigue.</tspan>
      <tspan x="0" dy="24">• Deep soothing comfort for arthritis, osteoarthritis, sprains &amp; tendon stress.</tspan>
      <tspan x="0" dy="24">• Hydrates and rebalances skin with 100% pure Pomorie Black Sea lye minerals.</tspan>
      <tspan x="0" dy="24">• Enriched with pure botanical {variant_name} extract for soothing synergy.</tspan>
    </text>
    <text x="0" y="240" font-family="'Cinzel', serif" font-size="12" letter-spacing="2" fill="#8C8275">
      HARVESTED FROM POMORIE LAGOON · ANCIENT HEALING TRADITION
    </text>
  </g>

  <!-- Vertical Divider 1 -->
  <line x1="780" y1="70" x2="780" y2="430" stroke="#DDD7CD" stroke-width="1.5"/>

  <!-- ==================== SECTION 2: HOW TO USE & CAUTION ==================== -->
  <g transform="translate(830, 80)">
    <rect x="0" y="0" width="150" height="26" rx="4" fill="#3D3B37"/>
    <text x="75" y="17" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="#FFFFFF">
      HOW TO USE
    </text>
    <text x="0" y="55" font-family="'Inter', sans-serif" font-size="14" fill="#33312D">
      <tspan x="0" dy="0">Apply a generous amount onto clean, dry skin over the affected area.</tspan>
      <tspan x="0" dy="24">Massage gently until partially absorbed. Allow minerals to act for 30–60 min</tspan>
      <tspan x="0" dy="24">or leave overnight for maximum therapeutic benefit. If desired, rinse with water.</tspan>
    </text>

    <rect x="0" y="150" width="180" height="26" rx="4" fill="#6B655B"/>
    <text x="90" y="167" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="#FFFFFF">
      CAUTION &amp; STORAGE
    </text>
    <text x="0" y="205" font-family="'Inter', sans-serif" font-size="13" fill="#55514B">
      <tspan x="0" dy="0">For external topical use only. Avoid contact with eyes and open wounds.</tspan>
      <tspan x="0" dy="22">Keep out of reach of children. Store in a cool, dry place (5°C – 25°C).</tspan>
      <tspan x="0" dy="22">Protect from direct sunlight. Do not freeze.</tspan>
    </text>
  </g>

  <!-- Vertical Divider 2 -->
  <line x1="1520" y1="70" x2="1520" y2="430" stroke="#DDD7CD" stroke-width="1.5"/>

  <!-- ==================== SECTION 3: INCI, SPECS, SYMBOLS ==================== -->
  <g transform="translate(1570, 80)">
    <rect x="0" y="0" width="150" height="26" rx="4" fill="#3D3B37"/>
    <text x="75" y="17" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="#FFFFFF">
      INGREDIENTS (INCI)
    </text>
    <text x="0" y="55" font-family="'Inter', sans-serif" font-size="13" fill="#2E2C29" font-style="italic">
      <tspan x="0" dy="0">{inci}</tspan>
    </text>

    <!-- Packaging & Lab Info -->
    <g transform="translate(0, 150)">
      <text font-family="'Montserrat', sans-serif" font-size="13" font-weight="600" fill="#3D3B37">
        <tspan x="0" dy="0">LOT NUMBER / EXPIRY DATE:</tspan>
        <tspan x="220" font-weight="700" fill="#1C1A18">Lot № 07 / 25.12.2027</tspan>
        <tspan x="0" dy="30">NOMINAL PACK SIZE:</tspan>
        <tspan x="220" font-weight="800" font-size="16" fill="{badge_col}">300 g ℮ (10.1 fl oz)</tspan>
      </text>

      <!-- Compliance Icons (PAO, Recycling, Mobius) -->
      <g transform="translate(0, 75)">
        <!-- 12M Jar -->
        <rect x="0" y="0" width="55" height="38" rx="6" fill="none" stroke="#4A453E" stroke-width="2"/>
        <text x="27" y="24" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="14" font-weight="700" fill="#4A453E">12M</text>
        
        <!-- Recycling Symbol -->
        <g transform="translate(85, 20)">
          <circle cx="0" cy="0" r="18" fill="none" stroke="#4A453E" stroke-width="2"/>
          <text x="0" y="6" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="12" font-weight="800" fill="#4A453E">♳ PET</text>
        </g>

        <!-- Certified Pomorie Origin Seal -->
        <g transform="translate(210, 0)">
          <rect x="0" y="0" width="220" height="38" rx="19" fill="{data['light_accent']}" stroke="{accent}" stroke-width="1.5"/>
          <text x="110" y="24" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="12" font-weight="700" fill="{badge_col}">
            ✓ POMORIE BLACK SEA LYE
          </text>
        </g>
      </g>
    </g>
  </g>

  <!-- Vertical Divider 3 -->
  <line x1="2220" y1="70" x2="2220" y2="430" stroke="url(#goldH)" stroke-width="2"/>

  <!-- ==================== SECTION 4: FRONT FACING HERO PANEL ==================== -->
  <g transform="translate(2260, 60)">
    <!-- Brand Crest & Logo -->
    <text x="350" y="50" text-anchor="middle" font-family="'Cinzel', 'Trajan Pro', serif" font-size="44" letter-spacing="10" font-weight="700" fill="#1C1A18">
      ANCHIALO
    </text>
    <text x="350" y="75" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="12" letter-spacing="6" font-weight="600" fill="#8C8275">
      POMORIE BALNEOLOGY LABS
    </text>

    <!-- Product Title -->
    <text x="350" y="125" text-anchor="middle" font-family="'Cinzel', serif" font-size="28" font-weight="700" letter-spacing="3" fill="#2E2C29">
      DUAL MAGNESIUM GEL
    </text>

    <!-- Variant Accent Box -->
    <rect x="100" y="145" width="500" height="42" rx="21" fill="url(#variantBar)"/>
    <text x="350" y="172" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="16" font-weight="800" letter-spacing="4" fill="#FFFFFF">
      BLACK SEA LYE WITH {variant_name.upper()}
    </text>

    <!-- Barcode & Manufacturer -->
    <g transform="translate(40, 210)">
      <!-- EAN-13 Barcode Vector Graphic -->
      <g fill="#1A1816">
        <rect x="0" y="0" width="3" height="70"/>
        <rect x="6" y="0" width="2" height="70"/>
        <rect x="12" y="0" width="4" height="60"/>
        <rect x="20" y="0" width="2" height="60"/>
        <rect x="26" y="0" width="6" height="60"/>
        <rect x="36" y="0" width="2" height="60"/>
        <rect x="42" y="0" width="4" height="60"/>
        <rect x="50" y="0" width="2" height="60"/>
        <rect x="56" y="0" width="6" height="60"/>
        <rect x="66" y="0" width="2" height="60"/>
        <rect x="72" y="0" width="4" height="70"/>
        <rect x="78" y="0" width="2" height="70"/>
        <rect x="84" y="0" width="6" height="60"/>
        <rect x="94" y="0" width="2" height="60"/>
        <rect x="100" y="0" width="4" height="60"/>
        <rect x="108" y="0" width="6" height="60"/>
        <rect x="118" y="0" width="2" height="60"/>
        <rect x="124" y="0" width="4" height="60"/>
        <rect x="132" y="0" width="6" height="60"/>
        <rect x="142" y="0" width="2" height="70"/>
        <rect x="148" y="0" width="3" height="70"/>
      </g>
      <text x="75" y="85" text-anchor="middle" font-family="'Courier New', monospace" font-size="14" font-weight="700" fill="#1A1816">
        3 800230 111746
      </text>

      <!-- Manufacturer Block -->
      <g transform="translate(190, 10)">
        <text font-family="'Inter', sans-serif" font-size="12" fill="#3D3B37">
          <tspan x="0" dy="0" font-weight="700">PRODUCED IN BULGARIA (EU) BY:</tspan>
          <tspan x="0" dy="18" font-weight="600">AZIMUT 6000 Ltd.</tspan>
          <tspan x="0" dy="16">18 Ivan Vazov Str., 8200 Pomorie</tspan>
          <tspan x="0" dy="16">Tel: +359 887 470 548</tspan>
          <tspan x="0" dy="16" font-weight="600" fill="{badge_col}">www.anchialo.com</tspan>
        </text>
      </g>
    </g>
  </g>
</svg>"""
    return svg

def main():
    print("Generating redesigned SVGs and rendering high-res images...")
    for var_name, var_data in VARIANTS.items():
        print(f"\n--- VARIANT: {var_name} ---")
        # 1. Top Lid SVG
        top_svg = generate_top_lid_svg(var_name, var_data)
        top_svg_path = os.path.join(SVG_DIR, f"Anchialo_Top_Lid_{var_name}_Redesign.svg")
        with open(top_svg_path, "w", encoding="utf-8") as f:
            f.write(top_svg)
        print(f"  ✓ Saved SVG: {top_svg_path}")

        # Render Top Lid to PNG and PDF via PyMuPDF
        doc_top = fitz.open(stream=top_svg.encode("utf-8"), filetype="svg")
        pix_top = doc_top[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        top_png_path = os.path.join(PNG_DIR, f"Anchialo_Top_Lid_{var_name}_Redesign.png")
        pix_top.save(top_png_path)
        
        pdf_bytes_top = doc_top.convert_to_pdf()
        top_pdf_path = os.path.join(PDF_DIR, f"Anchialo_Top_Lid_{var_name}_Redesign.pdf")
        with open(top_pdf_path, "wb") as pf:
            pf.write(pdf_bytes_top)
        doc_top.close()
        print(f"  ✓ Saved PNG & PDF: {top_png_path}")

        # 2. Side Label SVG
        side_svg = generate_side_label_svg(var_name, var_data)
        side_svg_path = os.path.join(SVG_DIR, f"Anchialo_Side_Wrap_{var_name}_Redesign.svg")
        with open(side_svg_path, "w", encoding="utf-8") as f:
            f.write(side_svg)
        print(f"  ✓ Saved SVG: {side_svg_path}")

        # Render Side Wrap to PNG and PDF
        doc_side = fitz.open(stream=side_svg.encode("utf-8"), filetype="svg")
        pix_side = doc_side[0].get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
        side_png_path = os.path.join(PNG_DIR, f"Anchialo_Side_Wrap_{var_name}_Redesign.png")
        pix_side.save(side_png_path)

        pdf_bytes_side = doc_side.convert_to_pdf()
        side_pdf_path = os.path.join(PDF_DIR, f"Anchialo_Side_Wrap_{var_name}_Redesign.pdf")
        with open(side_pdf_path, "wb") as pf:
            pf.write(pdf_bytes_side)
        doc_side.close()
        print(f"  ✓ Saved PNG & PDF: {side_png_path}")

    print("\nAll 10 Redesigned Label SVGs, High-Res PNGs, and PDFs created successfully!")

if __name__ == "__main__":
    main()
