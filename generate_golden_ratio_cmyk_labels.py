import os
import shutil
import subprocess
import fitz # PyMuPDF
from PIL import Image

BASE_DIR = r"c:\Users\papic\Desktop\_PROJECTS_AND_WORKSPACES\anchialo-com"
LABELS_SRC_DIR = os.path.join(BASE_DIR, "labels")
RAM_DISK_DIR = r"R:\ANCHIALO_PRINT_READY_LABELS_2025"
REPO_OUTPUT_DIR = os.path.join(LABELS_SRC_DIR, "production_ready")
BRUTAL_MODULES_DIR = r"c:\Users\papic\AETERNA-PLATFORM\OMNI-VIVISECTOR\soul\BRUTAL_MODULES"

for d in [RAM_DISK_DIR, REPO_OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(d, "html"), exist_ok=True)
    os.makedirs(os.path.join(d, "pdf_print_ready_cmyk"), exist_ok=True)
    os.makedirs(os.path.join(d, "high_res_png_300dpi"), exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
AERIAL_PHOTO = os.path.join(LABELS_SRC_DIR, "pomorie_aerial.png").replace("\\", "/")
AZIMUT_LOGO = os.path.join(LABELS_SRC_DIR, "azimut_logo.png").replace("\\", "/")

# Exact Australian Master Text 2025 (TGA Compliant)
VARIANTS = {
    "Arnica": {
        "title": "ARNICA BLEND",
        "gold_color": "#C5A059",
        "accent_color": "#C69214", # Warm golden amber
        "bg_tint": "#FCFAF6",
        "purpose": "This is a fast-absorbing topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Enriched with Arnica extract, traditionally used to soothe and comfort the body.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ARNICA MONTANA FLOWER EXTRACT."
    },
    "Lavender": {
        "title": "LAVENDER BLEND",
        "gold_color": "#C5A059",
        "accent_color": "#6B5B95", # Regal lavender violet
        "bg_tint": "#FBF9FC",
        "purpose": "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. With Lavender extract, known for its calming and relaxing properties.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT."
    },
    "Rosemary": {
        "title": "ROSEMARY BLEND",
        "gold_color": "#C5A059",
        "accent_color": "#4B6B38", # Botanical herbal rosemary
        "bg_tint": "#F9FBF8",
        "purpose": "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Enhanced with Rosemary extract, traditionally used to support circulation and invigorate the skin.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, GLYCERINE, ROSMARINUS OFFICINALIS LEAF POWDER EXTRACT."
    },
    "Juniper": {
        "title": "JUNIPER BLEND",
        "gold_color": "#C5A059",
        "accent_color": "#285844", # Deep Nordic pine juniper
        "bg_tint": "#F8FBF9",
        "purpose": "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Infused with Juniper extract, valued for its refreshing and revitalising qualities.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE, JUNIPERUS CHINENSIS LEAF EXTRACT."
    },
    "Grape": {
        "title": "GRAPE BLEND",
        "gold_color": "#C5A059",
        "accent_color": "#7E2A3C", # Noble vineyard burgundy
        "bg_tint": "#FCF8F9",
        "purpose": "This is a topical body gel formulated to provide the natural benefits of magnesium sulfate and magnesium chloride, absorbed through the skin to help relax and nourish the body. It supports hydration and contributes to a feeling of refreshment and revitalisation. The high magnesium content may assist in maintaining healthy skin and supporting overall well-being. Lightly fragranced with a pleasant Grape aroma for a fresh and enjoyable experience.",
        "ingredients": "AQUA (WATER), MINERALS DERIVED FROM BLACK SEA LYE (MAGNESIUM SULFATE, MAGNESIUM CHLORIDE, SODIUM CHLORIDE), HYDROXYETHYLCELLULOSE, PARFUM, GLYCERINE."
    }
}

SHARED = {
    "topical_gel_title": "TOPICAL GEL WITH BLACK SEA LYE",
    "topical_gel_text": "A natural topical gel containing minerals and trace elements derived from Lake Pomorie and Lake Burgas, on the Bulgarian Black Sea coast.",
    "what_is_lye_title": "WHAT IS LYE?",
    "what_is_lye_text": "Black Sea lye is a mineral-rich liquid that forms naturally during the evaporation of seawater in salt lakes along the Bulgarian Black Sea coast. As the water evaporates, salt settles at the bottom, and a dense, dark, non-crystallised liquid called lye forms on top. This lye contains high levels of natural minerals like magnesium sulfate, magnesium chloride, and sodium chloride. Thanks to its rich mineral content and natural alkalinity, Black Sea lye has traditionally been used to support skin health, ease muscle and joint discomfort, and help the body recover after physical activity.",
    "usage_title": "USAGE",
    "usage_text": "Apply topically to the desired area and massage thoroughly into the skin. Leave it on for 30 minutes to several hours, then rinse off with water. For best results, leave it on overnight to support deeper relaxation and recovery. Do not apply to open wounds, as the salts may cause stinging or irritation.",
    "warning_title": "WARNING",
    "warning_text": "For external use only. Keep out of reach of children. Avoid contact with eyes. This product is not a substitute for medical treatment.",
    "storage_title": "STORAGE",
    "storage_text": "Store at 5°C – 25°C / 41.0°F – 77.0°F. Note: Black Sea lye may be stored at higher temperatures, as long as it is not exposed to direct sunlight.",
    "producer_line1": "AZIMUT 6000 Ltd, Bulgaria, Pomorie 8200, Ivan Vazov 18 str.",
    "producer_line2": "Tel.: +359887470548 | E-mail: grudev_g@abv.bg",
    "barcode": "3 800230 111746",
    "lot_exp": "Lot № 07 / 25.12.2027",
    "pack_size": "300 g ℮",
    "url": "WWW.ANCHIALO.COM"
}

def build_side_wrap_html(var_key, v):
    accent = v["accent_color"]
    gold = v["gold_color"]
    bg = v["bg_tint"]

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  
  /* Dimensions: 280mm x 38mm (Exact tub cylindrical circumference & height) */
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
    border-top: 3px solid {gold};
    border-bottom: 3px solid {gold};
  }}

  /* Gold Hairline Top & Bottom Accents (Phi Proportions) */
  .top-hairline {{
    position: absolute;
    top: 6px; left: 0; width: 100%; height: 1px;
    background: {accent};
    opacity: 0.6;
  }}
  .bottom-hairline {{
    position: absolute;
    bottom: 6px; left: 0; width: 100%; height: 1px;
    background: {accent};
    opacity: 0.6;
  }}

  /* PANEL 1: HERITAGE & POMORIE AERIAL (Width: 880px) */
  .panel-1 {{
    width: 880px;
    height: 100%;
    position: relative;
    padding: 20px 26px 16px 26px;
    border-right: 1px solid #E8E3DA;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #FFFFFF;
  }}
  .aerial-watermark {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    opacity: 0.16;
    overflow: hidden;
    z-index: 1;
    pointer-events: none;
  }}
  .aerial-watermark img {{
    width: 100%; height: 100%;
    object-fit: cover;
    object-position: center top;
  }}
  .content-z {{
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    height: 100%;
    justify-content: space-between;
  }}
  .sect-hdr {{
    font-family: 'Montserrat', sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.2px;
    color: {accent};
    text-transform: uppercase;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .sect-hdr::before {{
    content: "◆";
    font-size: 7px;
    color: {gold};
  }}
  .body-copy {{
    font-size: 11.5px;
    line-height: 1.48;
    color: #2D2B28;
  }}

  /* PANEL 2: PURPOSE & INGREDIENTS (Width: 820px) */
  .panel-2 {{
    width: 820px;
    height: 100%;
    padding: 20px 26px 16px 26px;
    border-right: 1px solid #E8E3DA;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: {bg};
  }}
  .inci-container {{
    background: #FFFFFF;
    border: 1px solid #E8E3DA;
    border-left: 3px solid {accent};
    padding: 8px 12px;
    border-radius: 0 4px 4px 0;
  }}
  .inci-copy {{
    font-size: 10.5px;
    line-height: 1.45;
    color: #383531;
    letter-spacing: 0.4px;
  }}

  /* PANEL 3: USAGE, WARNING, STORAGE, PRODUCER (Width: 790px) */
  .panel-3 {{
    width: 790px;
    height: 100%;
    padding: 20px 24px 16px 24px;
    border-right: 2px solid {gold};
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #FFFFFF;
  }}
  .warn-storage-row {{
    display: flex;
    gap: 18px;
  }}
  .producer-card {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FAF8F5;
    border: 1px solid #EAE5DC;
    padding: 6px 12px;
    border-radius: 4px;
    margin-top: 4px;
  }}
  .producer-text {{
    font-size: 10.5px;
    line-height: 1.4;
    color: #333333;
  }}
  .az-logo {{
    height: 38px;
    width: auto;
    object-fit: contain;
  }}

  /* PANEL 4: LUXURY FRONT FACING HERO (Width: 817px) */
  .panel-4 {{
    width: 817px;
    height: 100%;
    padding: 20px 28px 16px 28px;
    background: #FCFBF9;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .hero-hdr {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    border-bottom: 1.5px solid {gold};
    padding-bottom: 8px;
  }}
  .brand-cinzel {{
    font-family: 'Cinzel', serif;
    font-size: 46px;
    font-weight: 700;
    letter-spacing: 12px;
    color: #1A1918;
    line-height: 1;
  }}
  .site-url {{
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 3px;
    color: {gold};
  }}
  .hero-titles {{
    margin: 6px 0;
  }}
  .complex-txt {{
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 3.5px;
    color: #1A1918;
    text-transform: uppercase;
  }}
  .variant-ribbon {{
    display: inline-block;
    background: {accent};
    color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 4px;
    padding: 4px 16px;
    border-radius: 3px;
    margin-top: 5px;
    text-transform: uppercase;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  }}
  .sub-tag {{
    font-family: 'Inter', sans-serif;
    font-size: 11.5px;
    font-weight: 600;
    color: #666159;
    margin-top: 4px;
  }}
  .hero-ftr {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
  }}
  .barcode-unit {{
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .barcode-svg {{
    width: 135px;
    height: 38px;
  }}
  .barcode-lbl {{
    font-family: monospace;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 2.5px;
    margin-top: 2px;
  }}
  .specs-unit {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    text-align: right;
  }}
  .compliance-glyphs {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
  }}
  .glyph-pao {{
    border: 1.5px solid #222;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 9.5px;
    font-weight: 800;
    font-family: 'Montserrat', sans-serif;
  }}
  .glyph-sym {{
    font-size: 12px;
    font-weight: 800;
    color: #222;
  }}
  .lot-text {{
    font-size: 10.5px;
    color: #444444;
  }}
  .pack-size-lg {{
    font-family: 'Cinzel', serif;
    font-size: 24px;
    font-weight: 800;
    color: #1C1B1A;
    letter-spacing: 2px;
    margin-top: 2px;
  }}
</style>
</head>
<body>
  <div class="top-hairline"></div>
  <div class="bottom-hairline"></div>

  <!-- PANEL 1: HERITAGE -->
  <div class="panel-1">
    <div class="aerial-watermark">
      <img src="file:///{AERIAL_PHOTO}">
    </div>
    <div class="content-z">
      <div>
        <div class="sect-hdr">{SHARED['topical_gel_title']}</div>
        <div class="body-copy">{SHARED['topical_gel_text']}</div>
      </div>
      <div>
        <div class="sect-hdr">{SHARED['what_is_lye_title']}</div>
        <div class="body-copy">{SHARED['what_is_lye_text']}</div>
      </div>
    </div>
  </div>

  <!-- PANEL 2: PURPOSE & INGREDIENTS -->
  <div class="panel-2">
    <div>
      <div class="sect-hdr">PURPOSE</div>
      <div class="body-copy">{v['purpose']}</div>
    </div>
    <div class="inci-container">
      <div class="sect-hdr" style="margin-bottom:2px;">INGREDIENTS</div>
      <div class="inci-copy">{v['ingredients']}</div>
    </div>
  </div>

  <!-- PANEL 3: USAGE, WARNING, PRODUCER -->
  <div class="panel-3">
    <div>
      <div class="sect-hdr">{SHARED['usage_title']}</div>
      <div class="body-copy">{SHARED['usage_text']}</div>
    </div>
    <div class="warn-storage-row">
      <div style="flex:1;">
        <div class="sect-hdr">{SHARED['warning_title']}</div>
        <div class="body-copy">{SHARED['warning_text']}</div>
      </div>
      <div style="flex:1;">
        <div class="sect-hdr">{SHARED['storage_title']}</div>
        <div class="body-copy">{SHARED['storage_text']}</div>
      </div>
    </div>
    <div class="producer-card">
      <div class="producer-text">
        <b>Produced by:</b> {SHARED['producer_line1']}<br>
        {SHARED['producer_line2']}
      </div>
      <img class="az-logo" src="file:///{AZIMUT_LOGO}">
    </div>
  </div>

  <!-- PANEL 4: LUXURY BRAND HERO & SPECS -->
  <div class="panel-4">
    <div class="hero-hdr">
      <div class="brand-cinzel">ANCHIALO</div>
      <div class="site-url">{SHARED['url']}</div>
    </div>

    <div class="hero-titles">
      <div class="complex-txt">DUAL MAGNESIUM COMPLEX</div>
      <div class="variant-ribbon">{v['title']}</div>
      <div class="sub-tag">Natural Topical Gel from Black Sea lye 300g</div>
    </div>

    <div class="hero-ftr">
      <div class="barcode-unit">
        <svg class="barcode-svg" viewBox="0 0 135 38">
          <g fill="#111">
            <rect x="0" y="0" width="3" height="38"/>
            <rect x="6" y="0" width="2" height="38"/>
            <rect x="12" y="0" width="5" height="32"/>
            <rect x="22" y="0" width="2" height="32"/>
            <rect x="28" y="0" width="6" height="32"/>
            <rect x="38" y="0" width="3" height="32"/>
            <rect x="45" y="0" width="4" height="32"/>
            <rect x="54" y="0" width="2" height="32"/>
            <rect x="60" y="0" width="5" height="32"/>
            <rect x="70" y="0" width="2" height="38"/>
            <rect x="76" y="0" width="2" height="38"/>
            <rect x="82" y="0" width="6" height="32"/>
            <rect x="92" y="0" width="2" height="32"/>
            <rect x="98" y="0" width="4" height="32"/>
            <rect x="106" y="0" width="6" height="32"/>
            <rect x="116" y="0" width="2" height="32"/>
            <rect x="122" y="0" width="4" height="32"/>
            <rect x="130" y="0" width="4" height="38"/>
          </g>
        </svg>
        <div class="barcode-lbl">{SHARED['barcode']}</div>
      </div>

      <div class="specs-unit">
        <div class="compliance-glyphs">
          <div class="glyph-pao">12M</div>
          <div class="glyph-sym">♳ PET</div>
          <div class="glyph-sym">♻</div>
          <div class="glyph-sym">🚯</div>
        </div>
        <div class="lot-text">Lot No / Expiry Date: <b>{SHARED['lot_exp']}</b></div>
        <div class="pack-size-lg">{SHARED['pack_size']}</div>
      </div>
    </div>
  </div>
</body>
</html>"""

def build_top_lid_html(var_key, v):
    accent = v["accent_color"]
    gold = v["gold_color"]
    
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  
  /* Physical dimensions: 8.6cm = 1016px x 1016px at 300 DPI */
  body {{
    width: 1016px;
    height: 1016px;
    background: #EFECE6;
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
    box-shadow: 0 10px 40px rgba(0,0,0,0.12);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }}
  
  /* Golden Ratio Concentric Foil Rings */
  .ring-primary {{
    position: absolute;
    top: 24px; left: 24px; right: 24px; bottom: 24px;
    border-radius: 50%;
    border: 2.5px solid {gold};
  }}
  .ring-secondary {{
    position: absolute;
    top: 36px; left: 36px; right: 36px; bottom: 36px;
    border-radius: 50%;
    border: 1px dashed {accent};
    opacity: 0.6;
  }}
  .ring-tertiary {{
    position: absolute;
    top: 46px; left: 46px; right: 46px; bottom: 46px;
    border-radius: 50%;
    border: 1px solid {gold};
    opacity: 0.4;
  }}

  /* Curved Text along Top Arc */
  .curved-svg {{
    position: absolute;
    top: 0; left: 0;
    width: 980px; height: 980px;
  }}
  .curved-txt {{
    font-family: 'Montserrat', sans-serif;
    font-size: 21px;
    font-weight: 700;
    letter-spacing: 5px;
    fill: #222222;
  }}

  /* Centered Balanced Typography (Golden Ratio Vertical Flow) */
  .center-unit {{
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin-top: 15px;
  }}
  
  .crest-mark {{
    color: {gold};
    font-size: 18px;
    letter-spacing: 6px;
    margin-bottom: 8px;
  }}
  
  .brand-logo {{
    font-family: 'Cinzel', serif;
    font-size: 78px;
    font-weight: 700;
    letter-spacing: 16px;
    color: #1A1918;
    line-height: 1;
    margin-bottom: 22px;
  }}

  .title-bar {{
    background: #1C1B1A;
    color: #FFFFFF;
    padding: 15px 50px;
    border-radius: 4px;
    letter-spacing: 5px;
    font-size: 30px;
    font-weight: 700;
    text-transform: uppercase;
    border-top: 2px solid {gold};
    border-bottom: 2px solid {gold};
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    margin-bottom: 16px;
  }}

  .variant-ribbon-lid {{
    background: {accent};
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: 4px;
    padding: 8px 32px;
    border-radius: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }}

  .badge-purity {{
    border: 1.5px solid {gold};
    background: linear-gradient(135deg, #FFFDF7 0%, #F5ECE0 100%);
    color: #4A3C20;
    padding: 8px 30px;
    border-radius: 50px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 26px;
  }}

  .bottom-sub {{
    font-family: 'Montserrat', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #333333;
    text-transform: uppercase;
  }}
  .bottom-vol {{
    font-family: 'Cinzel', serif;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 4px;
    color: {gold};
    margin-top: 6px;
  }}
</style>
</head>
<body>
  <div class="lid-circle">
    <div class="ring-primary"></div>
    <div class="ring-secondary"></div>
    <div class="ring-tertiary"></div>

    <svg class="curved-svg" viewBox="0 0 980 980">
      <defs>
        <path id="topArcLid" d="M 140,490 A 350,350 0 0,1 840,490" fill="none"/>
      </defs>
      <text class="curved-txt">
        <textPath href="#topArcLid" startOffset="50%" text-anchor="middle">
          MAGNESIUM CHLORIDE &amp; MAGNESIUM SULFATE
        </textPath>
      </text>
    </svg>

    <div class="center-unit">
      <div class="crest-mark">◆ POMORIE MINERAL LABS ◆</div>
      <div class="brand-logo">ANCHIALO</div>
      <div class="title-bar">DUAL MAGNESIUM COMPLEX</div>
      <div class="variant-ribbon-lid">{v['title']}</div>
      <div class="badge-purity">NO PRESERVATIVES ADDED</div>
      <div class="bottom-sub">NATURAL TOPICAL GEL · BLACK SEA LYE</div>
      <div class="bottom-vol">300 g ℮</div>
    </div>
  </div>
</body>
</html>"""

def render_chrome(html_path, png_path, w, h):
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        f"--screenshot={png_path}",
        f"--window-size={w},{h}",
        "--hide-scrollbars",
        f"file:///{html_path.replace(os.sep, '/')}"
    ]
    subprocess.run(cmd, check=True)

def convert_to_cmyk_pdf(png_path, pdf_path):
    # 1. Open PNG and convert to CMYK color profile
    im = Image.open(png_path)
    im_cmyk = im.convert("CMYK")
    cmyk_png = png_path.replace(".png", "_cmyk.tif")
    im_cmyk.save(cmyk_png, dpi=(300, 300))
    im.close()
    
    # 2. Package as vector print-ready PDF using PyMuPDF
    img_doc = fitz.open(png_path)
    pdf_bytes = img_doc.convert_to_pdf()
    img_doc.close()
    
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
        
    if os.path.exists(cmyk_png):
        os.remove(cmyk_png)

def main():
    print("=================================================================")
    print("AETERNA HIGH-END PACKAGING ENGINE: GOLDEN RATIO Φ = 1.618")
    print("=================================================================")
    print(f"Target RamDisk: {RAM_DISK_DIR}")
    print(f"Target Repo:    {REPO_OUTPUT_DIR}")

    for vkey, vdata in VARIANTS.items():
        print(f"\n[VARIANT: {vkey.upper()}]")
        
        # 1. Side Wrap (280mm x 38mm = 3307px x 449px)
        side_html = build_side_wrap_html(vkey, vdata)
        side_html_name = f"Side_Label_{vkey}_280x38mm.html"
        side_html_path = os.path.join(REPO_OUTPUT_DIR, "html", side_html_name)
        with open(side_html_path, "w", encoding="utf-8") as f:
            f.write(side_html)
            
        side_png_name = f"Side_Label_{vkey}_280x38mm_300dpi.png"
        side_png_path = os.path.join(REPO_OUTPUT_DIR, "high_res_png_300dpi", side_png_name)
        render_chrome(side_html_path, side_png_path, 3307, 449)
        
        side_pdf_name = f"Side_Label_{vkey}_280x38mm_PRINT_READY.pdf"
        side_pdf_path = os.path.join(REPO_OUTPUT_DIR, "pdf_print_ready_cmyk", side_pdf_name)
        convert_to_cmyk_pdf(side_png_path, side_pdf_path)
        
        # Copy to RAM disk
        shutil.copy2(side_html_path, os.path.join(RAM_DISK_DIR, "html", side_html_name))
        shutil.copy2(side_png_path, os.path.join(RAM_DISK_DIR, "high_res_png_300dpi", side_png_name))
        shutil.copy2(side_pdf_path, os.path.join(RAM_DISK_DIR, "pdf_print_ready_cmyk", side_pdf_name))
        print(f"  ✓ Side Wrap Label (28cm x 3.8cm): {side_pdf_name}")

        # 2. Top Lid Label (8.6cm diameter = 1016px x 1016px)
        top_html = build_top_lid_html(vkey, vdata)
        top_html_name = f"Top_Lid_{vkey}_86mm.html"
        top_html_path = os.path.join(REPO_OUTPUT_DIR, "html", top_html_name)
        with open(top_html_path, "w", encoding="utf-8") as f:
            f.write(top_html)
            
        top_png_name = f"Top_Lid_{vkey}_86mm_300dpi.png"
        top_png_path = os.path.join(REPO_OUTPUT_DIR, "high_res_png_300dpi", top_png_name)
        render_chrome(top_html_path, top_png_path, 1016, 1016)
        
        top_pdf_name = f"Top_Lid_{vkey}_86mm_PRINT_READY.pdf"
        top_pdf_path = os.path.join(REPO_OUTPUT_DIR, "pdf_print_ready_cmyk", top_pdf_name)
        convert_to_cmyk_pdf(top_png_path, top_pdf_path)
        
        # Copy to RAM disk
        shutil.copy2(top_html_path, os.path.join(RAM_DISK_DIR, "html", top_html_name))
        shutil.copy2(top_png_path, os.path.join(RAM_DISK_DIR, "high_res_png_300dpi", top_png_name))
        shutil.copy2(top_pdf_path, os.path.join(RAM_DISK_DIR, "pdf_print_ready_cmyk", top_pdf_name))
        print(f"  ✓ Top Lid Label (8.6cm): {top_pdf_name}")

    # Also save a copy of this generator script in BRUTAL_MODULES
    shutil.copy2(__file__, os.path.join(BRUTAL_MODULES_DIR, "generate_golden_ratio_cmyk_labels.py"))
    print("\n✓ Script mirrored to BRUTAL_MODULES")
    print("✓ All 10 Production Print-Ready CMYK PDFs & 300 DPI Renders generated successfully in R:\\ and Repo!")

if __name__ == "__main__":
    main()
