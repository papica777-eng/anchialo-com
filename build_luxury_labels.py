import os
import subprocess
import fitz # PyMuPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "labels", "redesigned_v2")
HTML_DIR = os.path.join(OUTPUT_DIR, "html")
RENDERS_DIR = os.path.join(OUTPUT_DIR, "renders")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdf")

for d in [HTML_DIR, RENDERS_DIR, PDF_DIR]:
    os.makedirs(d, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Exact text data from original labels
LABELS_DATA = {
    "Arnica": {
        "variant_upper": "ARNICA",
        "variant_title": "Arnica",
        "accent_color": "#C59B27", # Sophisticated goldenrod
        "accent_bg": "#FCF8EC",
        "key_benefits": "Fast-absorbing gel delivers a mineral boost through magnesium sulfate and magnesium chloride, leaving the body feeling relaxed and revitalised after physical activity. Relieves muscle tension and soothes tired areas, hydrates and comforts dry skin. Enriched with real Arnica extract to gently support the skin’s natural balance.",
        "how_to_use": "Massage the gel into clean, dry skin on the desired area. Leave on for 30 minutes to several hours, or overnight for deeper relaxation. If irritation occurs, rinse with cool water. Avoid sensitive areas and mucus membranes.",
        "caution": "For external use only. Avoid contact with eyes. Keep out of reach of children. Store at 5°C – 25°C. Avoid direct sunlight.",
        "ingredients": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Glycerine, Hydroxyethylcellulose, Arnica Montana Flower Extract."
    },
    "Grape": {
        "variant_upper": "GRAPE",
        "variant_title": "Grape",
        "accent_color": "#7E2A3C", # Sophisticated burgundy
        "accent_bg": "#FAF0F2",
        "key_benefits": "Fast-absorbing gel delivers a mineral boost through magnesium sulfate and magnesium chloride, leaving the body feeling relaxed and revitalised after physical activity. Relieves muscle tension and soothes tired areas, hydrates and comforts dry skin.",
        "how_to_use": "Massage the gel into clean, dry skin on the desired area. Leave on for 30 minutes to several hours, or overnight for deeper relaxation. If irritation occurs, rinse with cool water. Avoid sensitive areas and mucus membranes.",
        "caution": "For external use only. Avoid contact with eyes. Keep out of reach of children. Store at 5°C – 25°C. Avoid direct sunlight.",
        "ingredients": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Glycerine, Hydroxyethylcellulose, Parfum (natural fragrance)."
    },
    "Juniper": {
        "variant_upper": "JUNIPER",
        "variant_title": "Juniper",
        "accent_color": "#2D5A46", # Deep forest pine
        "accent_bg": "#EEF5F1",
        "key_benefits": "Fast-absorbing gel delivers a mineral boost through magnesium sulfate and magnesium chloride, leaving the body feeling relaxed and revitalised after physical activity. Relieves muscle tension and soothes tired areas, hydrates and comforts dry skin. Enriched with real Juniper extract for a mild refreshing sensation on the skin.",
        "how_to_use": "Massage the gel into clean, dry skin on the desired area. Leave on for 30 minutes to several hours, or overnight for deeper relaxation. If irritation occurs, rinse with cool water. Avoid sensitive areas and mucus membranes.",
        "caution": "For external use only. Avoid contact with eyes. Keep out of reach of children. Store at 5°C – 25°C. Avoid direct sunlight.",
        "ingredients": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Hydroxyethylcellulose, Parfum (natural fragrance), Glycerine, Juniperus Chinensis Leaf Extract."
    },
    "Lavender": {
        "variant_upper": "LAVENDER",
        "variant_title": "Lavender",
        "accent_color": "#5D4C8C", # Elegant lavender violet
        "accent_bg": "#F2EFF8",
        "key_benefits": "Fast-absorbing gel delivers a mineral boost through magnesium sulfate and magnesium chloride, leaving the body feeling relaxed and revitalised after physical activity. Relieves muscle tension and soothes tired areas, hydrates and comforts dry skin. Enriched with real Lavender extract to gently refresh and calm the skin.",
        "how_to_use": "Massage the gel into clean, dry skin on the desired area. Leave on for 30 minutes to several hours, or overnight for deeper relaxation. If irritation occurs, rinse with cool water. Avoid sensitive areas and mucus membranes.",
        "caution": "For external use only. Avoid contact with eyes. Keep out of reach of children. Store at 5°C – 25°C. Avoid direct sunlight.",
        "ingredients": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Glycerine, Hydroxyethylcellulose, Lavandula Angustifolia Flower Extract."
    },
    "Rosemary": {
        "variant_upper": "ROSEMARY",
        "variant_title": "Rosemary",
        "accent_color": "#4A6338", # Botanical herbal olive
        "accent_bg": "#F1F5EE",
        "key_benefits": "Fast-absorbing gel delivers a mineral boost through magnesium sulfate and magnesium chloride, leaving the body feeling relaxed and revitalised after physical activity. Relieves muscle tension and soothes tired areas, hydrates and comforts dry skin. Enriched with real Rosemary extract for a light, refreshing feel after application.",
        "how_to_use": "Massage the gel into clean, dry skin on the desired area. Leave on for 30 minutes to several hours, or overnight for deeper relaxation. If irritation occurs, rinse with cool water. Avoid sensitive areas and mucus membranes.",
        "caution": "For external use only. Avoid contact with eyes. Keep out of reach of children. Store at 5°C – 25°C. Avoid direct sunlight.",
        "ingredients": "Aqua (Water), Black Sea Lye Minerals (Magnesium Sulfate, Magnesium Chloride, Sodium Chloride), Glycerine, Hydroxyethylcellulose, Rosmarinus Oﬃcinalis Leaf Powder Extract."
    }
}

def build_top_lid_html(variant_name, info):
    accent = info["accent_color"]
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');
  
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1000px;
    height: 1000px;
    background: #E8E5DF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Montserrat', sans-serif;
  }}
  .label-circle {{
    width: 960px;
    height: 960px;
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
  /* Delicate gold rings */
  .ring-outer {{
    position: absolute;
    top: 20px; left: 20px; right: 20px; bottom: 20px;
    border-radius: 50%;
    border: 2px solid #C5A059;
  }}
  .ring-inner {{
    position: absolute;
    top: 32px; left: 32px; right: 32px; bottom: 32px;
    border-radius: 50%;
    border: 1px dashed {accent};
    opacity: 0.7;
  }}
  .ring-fine {{
    position: absolute;
    top: 40px; left: 40px; right: 40px; bottom: 40px;
    border-radius: 50%;
    border: 1px solid #C5A059;
    opacity: 0.5;
  }}
  
  .curved-svg {{
    position: absolute;
    top: 0; left: 0;
    width: 960px; height: 960px;
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
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 5px;
    fill: #1A1A1A;
  }}
  
  /* Center Content Block */
  .center-content {{
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 0 40px;
  }}
  
  .brand-logo {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 76px;
    font-weight: 700;
    letter-spacing: 16px;
    color: #1A1918;
    text-transform: uppercase;
    margin-bottom: 25px;
    line-height: 1;
    text-shadow: 0 1px 1px rgba(0,0,0,0.05);
  }}
  
  .title-bar {{
    background: #1C1B1A;
    color: #FFFFFF;
    padding: 16px 50px;
    border-radius: 4px;
    letter-spacing: 6px;
    font-size: 32px;
    font-weight: 700;
    text-transform: uppercase;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    border-top: 1px solid #C5A059;
    border-bottom: 1px solid #C5A059;
    margin-bottom: 30px;
  }}
  
  .badge-oval {{
    border: 1.5px solid #C5A059;
    background: linear-gradient(135deg, #FFF9EB 0%, #F5E8C8 100%);
    color: #4A3B1C;
    padding: 10px 32px;
    border-radius: 50px;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    box-shadow: 0 2px 8px rgba(197, 160, 89, 0.25);
  }}
</style>
</head>
<body>
  <div class="label-circle">
    <div class="ring-outer"></div>
    <div class="ring-inner"></div>
    <div class="ring-fine"></div>

    <svg class="curved-svg" viewBox="0 0 960 960">
      <defs>
        <path id="topArc" d="M 140,480 A 340,340 0 0,1 820,480" fill="none"/>
        <path id="bottomArc" d="M 820,480 A 340,340 0 0,1 140,480" fill="none"/>
      </defs>
      <text class="curved-text-top">
        <textPath href="#topArc" startOffset="50%" text-anchor="middle">
          MAGNESIUM CHLORIDE &amp; MAGNESIUM SULFATE
        </textPath>
      </text>
      <text class="curved-text-bottom">
        <textPath href="#bottomArc" startOffset="50%" text-anchor="middle">
          NATURAL TOPICAL GEL · <tspan fill="{accent}">{info['variant_upper']} BLEND</tspan>
        </textPath>
      </text>
    </svg>

    <div class="center-content">
      <div class="brand-logo">ANCHIALO</div>
      <div class="title-bar">DUAL MAGNESIUM GEL</div>
      <div class="badge-oval">NO PRESERVATIVES ADDED</div>
    </div>
  </div>
</body>
</html>"""

def build_side_wrap_html(variant_name, info):
    accent = info["accent_color"]
    accent_bg = info["accent_bg"]
    
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');
  
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 3000px;
    height: 480px;
    background: #FFFFFF;
    font-family: 'Inter', sans-serif;
    color: #222222;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  
  /* Top Full-width Header Bar */
  .top-banner {{
    background: #1C1B1A;
    color: #FFFFFF;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Montserrat', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    border-bottom: 2px solid {accent};
  }}
  
  .main-container {{
    flex: 1;
    display: flex;
    padding: 24px 40px;
    background: #FFFFFF;
  }}
  
  /* Section Columns */
  .col {{
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }}
  
  .col-benefits {{
    width: 720px;
    padding-right: 35px;
    border-right: 1px solid #E5E1D8;
  }}
  
  .col-usage {{
    width: 680px;
    padding: 0 35px;
    border-right: 1px solid #E5E1D8;
  }}
  
  .col-ingredients {{
    width: 660px;
    padding: 0 35px;
    border-right: 2px solid {accent};
  }}
  
  .col-brand {{
    width: 820px;
    padding-left: 45px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  
  /* Section Heading Pills */
  .heading-pill {{
    display: inline-flex;
    align-items: center;
    background: #F4EFE6;
    color: #2B2823;
    border-left: 4px solid {accent};
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    margin-bottom: 12px;
    border-radius: 0 4px 4px 0;
  }}
  
  .body-text {{
    font-size: 14px;
    line-height: 1.65;
    color: #333333;
    font-weight: 400;
  }}
  
  .inci-text {{
    font-size: 13px;
    line-height: 1.6;
    color: #444444;
    font-style: italic;
  }}
  
  /* Brand Right Section */
  .brand-header {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    border-bottom: 1px solid #E5E1D8;
    padding-bottom: 12px;
  }}
  
  .brand-name {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 52px;
    font-weight: 700;
    letter-spacing: 12px;
    color: #1A1918;
    line-height: 1;
  }}
  
  .brand-url {{
    font-family: 'Montserrat', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 2px;
    color: {accent};
    text-decoration: none;
  }}
  
  .variant-banner {{
    background: {accent};
    color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 4px;
    text-transform: uppercase;
    padding: 10px 24px;
    border-radius: 4px;
    margin: 14px 0;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
  }}
  
  .bottom-info-row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: auto;
  }}
  
  .producer-block {{
    font-size: 12.5px;
    line-height: 1.5;
    color: #444444;
  }}
  .producer-block b {{
    color: #111111;
    font-weight: 600;
  }}
  
  .specs-block {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }}
  
  .lot-text {{
    font-size: 12.5px;
    color: #444444;
    line-height: 1.5;
    text-align: right;
  }}
  .lot-text b {{
    color: #111111;
  }}
  
  .pack-size {{
    font-family: 'Montserrat', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #1A1918;
    margin-top: 4px;
  }}
  
  .barcode-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  
  .barcode-lines {{
    display: flex;
    height: 48px;
    align-items: stretch;
    gap: 2px;
  }}
  .b-bar {{ background: #111; }}
  
  .barcode-text {{
    font-family: monospace;
    font-size: 13px;
    letter-spacing: 3px;
    margin-top: 4px;
    font-weight: 700;
  }}
</style>
</head>
<body>
  <div class="top-banner">
    NATURAL TOPICAL GEL WITH MAGNESIUM CHLORIDE &amp; MAGNESIUM SULFATE
  </div>

  <div class="main-container">
    <!-- COLUMN 1: KEY BENEFITS -->
    <div class="col col-benefits">
      <div class="heading-pill">KEY BENEFITS</div>
      <div class="body-text">
        {info['key_benefits']}
      </div>
    </div>

    <!-- COLUMN 2: HOW TO USE & CAUTION -->
    <div class="col col-usage">
      <div class="heading-pill">HOW TO USE</div>
      <div class="body-text" style="margin-bottom: 16px;">
        {info['how_to_use']}
      </div>

      <div class="heading-pill">CAUTION &amp; STORAGE</div>
      <div class="body-text">
        {info['caution']}
      </div>
    </div>

    <!-- COLUMN 3: INGREDIENTS -->
    <div class="col col-ingredients">
      <div class="heading-pill">INGREDIENTS</div>
      <div class="inci-text">
        {info['ingredients']}
      </div>
    </div>

    <!-- COLUMN 4: BRAND, PRODUCER & PACK SPECS -->
    <div class="col col-brand">
      <div class="brand-header">
        <div class="brand-name">ANCHIALO</div>
        <div class="brand-url">www.anchialo.com</div>
      </div>

      <div class="variant-banner">
        BLACK SEA LYE WITH {info['variant_upper']}
      </div>

      <div class="bottom-info-row">
        <!-- Producer Block -->
        <div class="producer-block">
          <b>Produced by:</b><br>
          AZIMUT 6000 Ltd, Bulgaria,<br>
          Pomorie 8200, Ivan Vazov 18 str.<br>
          Tel: +359887470548<br>
          E-mail: grudev_g@abv.bg
        </div>

        <!-- Barcode Vector -->
        <div class="barcode-wrap">
          <svg width="150" height="45" viewBox="0 0 150 45">
            <rect x="0" y="0" width="3" height="45" fill="#111"/>
            <rect x="6" y="0" width="2" height="45" fill="#111"/>
            <rect x="12" y="0" width="5" height="40" fill="#111"/>
            <rect x="22" y="0" width="2" height="40" fill="#111"/>
            <rect x="28" y="0" width="6" height="40" fill="#111"/>
            <rect x="38" y="0" width="3" height="40" fill="#111"/>
            <rect x="45" y="0" width="4" height="40" fill="#111"/>
            <rect x="54" y="0" width="2" height="40" fill="#111"/>
            <rect x="60" y="0" width="5" height="40" fill="#111"/>
            <rect x="70" y="0" width="2" height="45" fill="#111"/>
            <rect x="76" y="0" width="2" height="45" fill="#111"/>
            <rect x="82" y="0" width="6" height="40" fill="#111"/>
            <rect x="92" y="0" width="2" height="40" fill="#111"/>
            <rect x="98" y="0" width="4" height="40" fill="#111"/>
            <rect x="106" y="0" width="6" height="40" fill="#111"/>
            <rect x="116" y="0" width="2" height="40" fill="#111"/>
            <rect x="122" y="0" width="4" height="40" fill="#111"/>
            <rect x="130" y="0" width="6" height="40" fill="#111"/>
            <rect x="140" y="0" width="2" height="45" fill="#111"/>
            <rect x="146" y="0" width="3" height="45" fill="#111"/>
          </svg>
          <div class="barcode-text">3 800230 111746</div>
        </div>

        <!-- Specs Block -->
        <div class="specs-block">
          <div class="lot-text">
            <b>Lot No / Expiry Date:</b><br>
            Lot № 07 / 25.12.2027<br>
            <b>Pack Size:</b>
          </div>
          <div class="pack-size">300 g ℮</div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""

def render_html_to_png(html_path, png_path, width, height):
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        f"--screenshot={png_path}",
        f"--window-size={width},{height}",
        "--hide-scrollbars",
        html_path
    ]
    subprocess.run(cmd, check=True)

def png_to_pdf(png_path, pdf_path):
    img = fitz.open(png_path)
    pdf_bytes = img.convert_to_pdf()
    img.close()
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

def main():
    print("Generating Luxury Redesigned Labels (100% Exact Text Preservation)...")
    
    for vname, vdata in LABELS_DATA.items():
        print(f"\nProcessing {vname}...")
        
        # 1. Top Lid
        top_html = build_top_lid_html(vname, vdata)
        top_html_path = os.path.join(HTML_DIR, f"Top_Lid_{vname}.html")
        with open(top_html_path, "w", encoding="utf-8") as f:
            f.write(top_html)
            
        top_png_path = os.path.join(RENDERS_DIR, f"Top_Lid_{vname}_Luxury.png")
        render_html_to_png(top_html_path, top_png_path, 1000, 1000)
        
        top_pdf_path = os.path.join(PDF_DIR, f"Top_Lid_{vname}_Luxury.pdf")
        png_to_pdf(top_png_path, top_pdf_path)
        print(f"  ✓ Top Lid: {top_png_path}")

        # 2. Side Wrap
        side_html = build_side_wrap_html(vname, vdata)
        side_html_path = os.path.join(HTML_DIR, f"Side_Wrap_{vname}.html")
        with open(side_html_path, "w", encoding="utf-8") as f:
            f.write(side_html)
            
        side_png_path = os.path.join(RENDERS_DIR, f"Side_Wrap_{vname}_Luxury.png")
        render_html_to_png(side_html_path, side_png_path, 3000, 480)
        
        side_pdf_path = os.path.join(PDF_DIR, f"Side_Wrap_{vname}_Luxury.pdf")
        png_to_pdf(side_png_path, side_pdf_path)
        print(f"  ✓ Side Wrap: {side_png_path}")

    print("\nAll 10 Luxury Redesigned Labels generated and rendered successfully!")

if __name__ == "__main__":
    main()
