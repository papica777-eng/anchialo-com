import os
import subprocess
import fitz # PyMuPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LABELS_DIR = os.path.join(BASE_DIR, "labels")
AUS_DIR = os.path.join(LABELS_DIR, "australian_master_2025")
HTML_DIR = os.path.join(AUS_DIR, "html")
RENDERS_DIR = os.path.join(AUS_DIR, "renders")
PDF_DIR = os.path.join(AUS_DIR, "pdf")

for d in [HTML_DIR, RENDERS_DIR, PDF_DIR]:
    os.makedirs(d, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Master Text 2025 for Australia (TGA-compliant verbatim text)
MASTER_DATA = {
    "Arnica": {
        "title": "ARNICA BLEND",
        "accent": "#C99700", # Warm golden amber
        "accent_bg": "#FCF8EC",
        "purpose": "This is a fast-absorbing topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Enriched with Arnica extract, traditionally used to soothe and comfort the body.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA FLOWER EXTRACT."
    },
    "Lavender": {
        "title": "LAVENDER BLEND",
        "accent": "#6C58A3", # Sophisticated lavender violet
        "accent_bg": "#F4F0FA",
        "purpose": "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. With Lavender extract, known for its calming and relaxing properties.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT."
    },
    "Rosemary": {
        "title": "ROSEMARY BLEND",
        "accent": "#4D6E37", # Botanical rosemary green
        "accent_bg": "#F2F7EE",
        "purpose": "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Enhanced with Rosemary extract, traditionally used to support circulation and invigorate the skin.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ROSMARINUS OFFICINALIS LEAF POWDER EXTRACT."
    },
    "Juniper": {
        "title": "JUNIPER BLEND",
        "accent": "#2B5E4B", # Deep evergreen juniper
        "accent_bg": "#EEF6F2",
        "purpose": "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Infused with Juniper extract, valued for its refreshing and revitalising qualities.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE, JUNIPERUS CHINENSIS LEAF EXTRACT."
    },
    "Grape": {
        "title": "GRAPE BLEND",
        "accent": "#87283E", # Noble vine grape burgundy
        "accent_bg": "#FAF0F2",
        "purpose": "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Lightly fragranced with a pleasant Grape aroma for a fresh and enjoyable experience.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE."
    }
}

SHARED_TEXT = {
    "what_is_lye_header": "WHAT IS LYE?",
    "what_is_lye_text": "Black Sea lye is a mineral-rich liquid that forms naturally during the evaporation of seawater in salt lakes along the Bulgarian Black Sea coast. As the water evaporates, salt settles at the bottom, and a dense, dark, non-crystallised liquid called lye forms on top. This lye contains high levels of natural minerals like magnesium sulfate, magnesium chloride, and sodium chloride. Thanks to its rich mineral content and natural alkalinity, Black Sea lye has traditionally been used to support skin health, ease muscle and joint discomfort, and help the body recover after physical activity.",
    "topical_gel_header": "TOPICAL GEL WITH BLACK SEA LYE",
    "topical_gel_text": "A natural topical gel containing minerals and trace elements derived from Lake Pomorie and Lake Burgas, on the Bulgarian Black Sea coast.",
    "usage_header": "USAGE",
    "usage_text": "Apply topically to the desired area and massage thoroughly into the skin. Leave it on for 30 minutes to several hours, then rinse off with water. For best results, leave it on overnight to support deeper relaxation and recovery. Do not apply to open wounds, as the salts may cause stinging or irritation.",
    "warning_header": "WARNING",
    "warning_text": "For external use only. Keep out of reach of children. Avoid contact with eyes. This product is not a substitute for medical treatment.",
    "storage_header": "STORAGE",
    "storage_text": "Store at 5°C – 25°C / 41.0°F – 77.0°F. Note: Black Sea lye may be stored at higher temperatures, as long as it is not exposed to direct sunlight.",
    "producer_lines": [
        "AZIMUT 6000 Ltd, Bulgaria,",
        "Pomorie 8200, Ivan Vazov 18 str.",
        "Tel.: +359887470548",
        "E-mail: grudev_g@abv.bg"
    ]
}

def generate_side_label_html(variant_key, var_data):
    accent = var_data["accent"]
    photo_path = os.path.abspath(os.path.join(LABELS_DIR, "pomorie_aerial.png")).replace("\\", "/")
    azimut_path = os.path.abspath(os.path.join(LABELS_DIR, "azimut_logo.png")).replace("\\", "/")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  
  /* Physical dimensions: 280mm x 38mm = 3307px x 449px at 300 DPI */
  body {{
    width: 3307px;
    height: 449px;
    background: #FFFFFF;
    color: #1A1A1A;
    font-family: 'Inter', sans-serif;
    display: flex;
    flex-direction: row;
    overflow: hidden;
    position: relative;
    border-top: 3px solid {accent};
    border-bottom: 3px solid #C5A059;
  }}

  /* PANEL 1: POMORIE SALT LAKE HERITAGE & PHOTO (Width: 840px) */
  .panel-heritage {{
    width: 840px;
    height: 100%;
    position: relative;
    display: flex;
    flex-direction: column;
    padding: 18px 24px 14px 24px;
    background: #FFFFFF;
    border-right: 1px solid #E2DDD5;
  }}
  .photo-bg-wrap {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    opacity: 0.14;
    overflow: hidden;
    z-index: 1;
  }}
  .photo-bg-wrap img {{
    width: 100%; height: 100%;
    object-fit: cover;
    object-position: center top;
  }}
  .heritage-content {{
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    height: 100%;
    justify-content: space-between;
  }}
  .h-badge {{
    display: inline-flex;
    background: #1C1B1A;
    color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 3px;
    margin-bottom: 5px;
    align-self: flex-start;
  }}
  .desc-block {{
    font-size: 11.5px;
    line-height: 1.48;
    color: #2D2B28;
    margin-bottom: 6px;
  }}
  .desc-block b {{
    font-family: 'Montserrat', sans-serif;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: {accent};
    text-transform: uppercase;
    display: block;
    margin-bottom: 2px;
  }}

  /* PANEL 2: PURPOSE & INGREDIENTS (Width: 800px) */
  .panel-purpose {{
    width: 800px;
    height: 100%;
    padding: 18px 24px 14px 24px;
    border-right: 1px solid #E2DDD5;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #FFFFFF;
  }}
  .inci-box {{
    background: #FAF8F5;
    border-left: 3px solid {accent};
    padding: 8px 12px;
    border-radius: 0 4px 4px 0;
  }}
  .inci-text {{
    font-size: 10.5px;
    line-height: 1.45;
    color: #3A3835;
    letter-spacing: 0.5px;
  }}

  /* PANEL 3: USAGE, WARNING, STORAGE & PRODUCER (Width: 810px) */
  .panel-usage {{
    width: 810px;
    height: 100%;
    padding: 18px 24px 14px 24px;
    border-right: 2px solid {accent};
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #FFFFFF;
  }}
  .producer-flex {{
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    background: #FAF8F5;
    padding: 6px 12px;
    border-radius: 4px;
    margin-top: 4px;
  }}
  .producer-text {{
    font-size: 10.5px;
    line-height: 1.4;
    color: #333333;
  }}
  .azimut-img {{
    height: 38px;
    width: auto;
    object-fit: contain;
  }}

  /* PANEL 4: BRAND HERO & PACKAGING SPECS (Width: 857px) */
  .panel-hero {{
    width: 857px;
    height: 100%;
    padding: 18px 28px 14px 28px;
    background: #FCFBF9;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .hero-top-row {{
    display: flex;
    flex-direction: row;
    align-items: baseline;
    justify-content: space-between;
    border-bottom: 1px solid #E5E0D8;
    padding-bottom: 8px;
  }}
  .hero-brand {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 46px;
    font-weight: 700;
    letter-spacing: 10px;
    color: #1A1918;
    line-height: 1;
  }}
  .hero-url {{
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 3px;
    color: {accent};
  }}
  .hero-titles {{
    margin: 4px 0;
  }}
  .complex-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: 19px;
    font-weight: 800;
    letter-spacing: 3px;
    color: #1C1B1A;
    text-transform: uppercase;
  }}
  .variant-ribbon {{
    display: inline-block;
    background: {accent};
    color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 3.5px;
    padding: 4px 14px;
    border-radius: 3px;
    margin-top: 4px;
    text-transform: uppercase;
  }}
  .sub-gel-text {{
    font-family: 'Inter', sans-serif;
    font-size: 11.5px;
    font-weight: 600;
    color: #666159;
    margin-top: 4px;
  }}
  
  .hero-footer {{
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }}
  
  .barcode-col {{
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .barcode-svg {{
    width: 140px;
    height: 40px;
  }}
  .barcode-digits {{
    font-family: monospace;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2.5px;
    margin-top: 2px;
  }}
  
  .specs-col {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    text-align: right;
  }}
  .lot-row {{
    font-size: 10.5px;
    color: #444444;
    line-height: 1.4;
  }}
  .pack-size-highlight {{
    font-family: 'Montserrat', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #1C1B1A;
    margin-top: 2px;
  }}
  
  /* Standard Packaging Compliance Icons */
  .icons-row {{
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
  }}
  .pao-icon {{
    border: 1.5px solid #222;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 10px;
    font-weight: 800;
    font-family: 'Montserrat', sans-serif;
  }}
  .recycle-badge {{
    font-size: 12px;
    font-weight: 800;
    color: #222;
  }}
</style>
</head>
<body>

  <!-- ==================== PANEL 1: HERITAGE & WHAT IS LYE ==================== -->
  <div class="panel-heritage">
    <div class="photo-bg-wrap">
      <img src="file:///{photo_path}">
    </div>
    <div class="heritage-content">
      <div class="desc-block">
        <b>{SHARED_TEXT['topical_gel_header']}</b>
        {SHARED_TEXT['topical_gel_text']}
      </div>
      <div class="desc-block">
        <b>{SHARED_TEXT['what_is_lye_header']}</b>
        {SHARED_TEXT['what_is_lye_text']}
      </div>
    </div>
  </div>

  <!-- ==================== PANEL 2: PURPOSE & INGREDIENTS ==================== -->
  <div class="panel-purpose">
    <div class="desc-block" style="flex: 1;">
      <b>PURPOSE</b>
      {var_data['purpose']}
    </div>
    <div class="inci-box">
      <b style="font-family:'Montserrat',sans-serif; font-size:10.5px; font-weight:700; color:{accent}; margin-bottom:3px; display:block;">INGREDIENTS</b>
      <div class="inci-text">{var_data['ingredients']}</div>
    </div>
  </div>

  <!-- ==================== PANEL 3: USAGE, WARNING, STORAGE, PRODUCER ==================== -->
  <div class="panel-usage">
    <div class="desc-block">
      <b>{SHARED_TEXT['usage_header']}</b>
      {SHARED_TEXT['usage_text']}
    </div>
    <div style="display: flex; flex-direction: row; gap: 18px;">
      <div class="desc-block" style="flex: 1;">
        <b>{SHARED_TEXT['warning_header']}</b>
        {SHARED_TEXT['warning_text']}
      </div>
      <div class="desc-block" style="flex: 1;">
        <b>{SHARED_TEXT['storage_header']}</b>
        {SHARED_TEXT['storage_text']}
      </div>
    </div>
    
    <div class="producer-flex">
      <div class="producer-text">
        <b>Produced by:</b> {SHARED_TEXT['producer_lines'][0]}<br>
        {SHARED_TEXT['producer_lines'][1]} | {SHARED_TEXT['producer_lines'][2]} | {SHARED_TEXT['producer_lines'][3]}
      </div>
      <img class="azimut-img" src="file:///{azimut_path}">
    </div>
  </div>

  <!-- ==================== PANEL 4: FRONT FACING HERO & PACK SPECS ==================== -->
  <div class="panel-hero">
    <div class="hero-top-row">
      <div class="hero-brand">ANCHIALO</div>
      <div class="hero-url">WWW.ANCHIALO.COM</div>
    </div>

    <div class="hero-titles">
      <div class="complex-title">DUAL MAGNESIUM COMPLEX</div>
      <div class="variant-ribbon">{var_data['title']}</div>
      <div class="sub-gel-text">Natural Topical Gel from Black Sea lye 300g</div>
    </div>

    <div class="hero-footer">
      <!-- Barcode -->
      <div class="barcode-col">
        <svg class="barcode-svg" viewBox="0 0 140 40">
          <g fill="#111">
            <rect x="0" y="0" width="3" height="40"/>
            <rect x="6" y="0" width="2" height="40"/>
            <rect x="12" y="0" width="5" height="34"/>
            <rect x="22" y="0" width="2" height="34"/>
            <rect x="28" y="0" width="6" height="34"/>
            <rect x="38" y="0" width="3" height="34"/>
            <rect x="45" y="0" width="4" height="34"/>
            <rect x="54" y="0" width="2" height="34"/>
            <rect x="60" y="0" width="5" height="34"/>
            <rect x="70" y="0" width="2" height="40"/>
            <rect x="76" y="0" width="2" height="40"/>
            <rect x="82" y="0" width="6" height="34"/>
            <rect x="92" y="0" width="2" height="34"/>
            <rect x="98" y="0" width="4" height="34"/>
            <rect x="106" y="0" width="6" height="34"/>
            <rect x="116" y="0" width="2" height="34"/>
            <rect x="122" y="0" width="4" height="34"/>
            <rect x="130" y="0" width="6" height="34"/>
            <rect x="140" y="0" width="2" height="40"/>
            <rect x="146" y="0" width="3" height="40"/>
          </g>
        </svg>
        <div class="barcode-digits">3 800230 111746</div>
      </div>

      <!-- Symbols & Specs -->
      <div class="specs-col">
        <div class="icons-row">
          <div class="pao-icon">12M</div>
          <div class="recycle-badge">♳ PET</div>
          <div class="recycle-badge">♻</div>
          <div class="recycle-badge">🚯</div>
        </div>
        <div class="lot-row">
          Lot No / Expiry Date: <b>Lot № 07 / 25.12.2027</b>
        </div>
        <div class="pack-size-highlight">300 g ℮</div>
      </div>
    </div>
  </div>

</body>
</html>"""

def generate_top_lid_html(variant_key, var_data):
    accent = var_data["accent"]
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@400;500;600;700;800&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  
  /* Physical dimensions: 8.6cm = 1016px x 1016px at 300 DPI */
  body {{
    width: 1016px;
    height: 1016px;
    background: #EAE6DF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Montserrat', sans-serif;
  }}
  .lid-circle {{
    width: 980px;
    height: 980px;
    border-radius: 50%;
    background: #FFFFFF;
    position: relative;
    box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }}
  .ring-1 {{
    position: absolute;
    top: 22px; left: 22px; right: 22px; bottom: 22px;
    border-radius: 50%;
    border: 2.5px solid #C5A059;
  }}
  .ring-2 {{
    position: absolute;
    top: 36px; left: 36px; right: 36px; bottom: 36px;
    border-radius: 50%;
    border: 1px dashed {accent};
    opacity: 0.6;
  }}
  .ring-3 {{
    position: absolute;
    top: 46px; left: 46px; right: 46px; bottom: 46px;
    border-radius: 50%;
    border: 1px solid #C5A059;
    opacity: 0.5;
  }}

  .curved-svg {{
    position: absolute;
    top: 0; left: 0;
    width: 980px; height: 980px;
  }}
  .curved-text-top {{
    font-family: 'Montserrat', sans-serif;
    font-size: 21px;
    font-weight: 700;
    letter-spacing: 5px;
    fill: #222222;
  }}
  .curved-text-bottom {{
    font-family: 'Montserrat', sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 5.5px;
    fill: #1A1A1A;
  }}

  .lid-center {{
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }}

  .brand-logo {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 80px;
    font-weight: 700;
    letter-spacing: 18px;
    color: #1A1918;
    line-height: 1;
    margin-bottom: 24px;
  }}

  .title-bar {{
    background: #1C1B1A;
    color: #FFFFFF;
    padding: 16px 52px;
    border-radius: 4px;
    letter-spacing: 6px;
    font-size: 32px;
    font-weight: 700;
    border-top: 2px solid #C5A059;
    border-bottom: 2px solid #C5A059;
    margin-bottom: 18px;
  }}

  .variant-pill {{
    background: {accent};
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 4px;
    padding: 8px 30px;
    border-radius: 20px;
    margin-bottom: 22px;
  }}

  .badge-oval {{
    border: 1.5px solid #C5A059;
    background: linear-gradient(135deg, #FFF9EB 0%, #F5E8C8 100%);
    color: #4A3B1C;
    padding: 9px 30px;
    border-radius: 50px;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 3px;
  }}
</style>
</head>
<body>
  <div class="lid-circle">
    <div class="ring-1"></div>
    <div class="ring-2"></div>
    <div class="ring-3"></div>

    <svg class="curved-svg" viewBox="0 0 980 980">
      <defs>
        <path id="topArcLid" d="M 140,490 A 350,350 0 0,1 840,490" fill="none"/>
        <path id="bottomArcLid" d="M 840,490 A 350,350 0 0,1 140,490" fill="none"/>
      </defs>
      <text class="curved-text-top">
        <textPath href="#topArcLid" startOffset="50%" text-anchor="middle">
          MAGNESIUM CHLORIDE &amp; MAGNESIUM SULFATE
        </textPath>
      </text>
      <text class="curved-text-bottom">
        <textPath href="#bottomArcLid" startOffset="50%" text-anchor="middle">
          NATURAL TOPICAL GEL · BLACK SEA LYE 300g
        </textPath>
      </text>
    </svg>

    <div class="lid-center">
      <div class="brand-logo">ANCHIALO</div>
      <div class="title-bar">DUAL MAGNESIUM COMPLEX</div>
      <div class="variant-pill">{var_data['title']}</div>
      <div class="badge-oval">NO PRESERVATIVES ADDED</div>
    </div>
  </div>
</body>
</html>"""

def render(html_path, png_path, w, h):
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        f"--screenshot={png_path}",
        f"--window-size={w},{h}",
        "--hide-scrollbars",
        html_path
    ]
    subprocess.run(cmd, check=True)

def to_pdf(png_path, pdf_path):
    img = fitz.open(png_path)
    pdf_bytes = img.convert_to_pdf()
    img.close()
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

def main():
    print("=== GENERATING AUSTRALIAN MASTER 2025 LABELS (EXACT TGA TEXT) ===")
    
    for vkey, vdata in MASTER_DATA.items():
        print(f"\nVariant: {vkey} ({vdata['title']})")
        
        # 1. Side Wrap (280mm x 38mm = 3307px x 449px)
        side_html = generate_side_label_html(vkey, vdata)
        side_html_path = os.path.join(HTML_DIR, f"Anchialo_Side_Label_{vkey}_2025.html")
        with open(side_html_path, "w", encoding="utf-8") as f:
            f.write(side_html)
            
        side_png_path = os.path.join(RENDERS_DIR, f"Anchialo_Side_Label_{vkey}_2025.png")
        render(side_html_path, side_png_path, 3307, 449)
        
        side_pdf_path = os.path.join(PDF_DIR, f"Anchialo_Side_Label_{vkey}_2025.pdf")
        to_pdf(side_png_path, side_pdf_path)
        print(f"  ✓ Side Wrap Label (28cm x 3.8cm): {side_png_path}")

        # 2. Top Lid (8.6cm = 1016px x 1016px)
        top_html = generate_top_lid_html(vkey, vdata)
        top_html_path = os.path.join(HTML_DIR, f"Anchialo_Top_Lid_{vkey}_2025.html")
        with open(top_html_path, "w", encoding="utf-8") as f:
            f.write(top_html)
            
        top_png_path = os.path.join(RENDERS_DIR, f"Anchialo_Top_Lid_{vkey}_2025.png")
        render(top_html_path, top_png_path, 1016, 1016)
        
        top_pdf_path = os.path.join(PDF_DIR, f"Anchialo_Top_Lid_{vkey}_2025.pdf")
        to_pdf(top_png_path, top_pdf_path)
        print(f"  ✓ Top Lid Label (8.6cm): {top_png_path}")

    print("\nAll Australian Master 2025 Labels generated successfully!")

if __name__ == "__main__":
    main()
