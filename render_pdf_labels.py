import os
import fitz # PyMuPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORIGINAL_DIR = os.path.join(BASE_DIR, "labels", "original")
RENDERS_DIR = os.path.join(BASE_DIR, "labels", "renders")
os.makedirs(RENDERS_DIR, exist_ok=True)

print("=== CONVERTING PDF LABELS TO HIGH-RES PNGs & EXTRACTING SPECS ===")

specs = {}

for filename in sorted(os.listdir(ORIGINAL_DIR)):
    if not filename.endswith(".pdf"):
        continue
    
    filepath = os.path.join(ORIGINAL_DIR, filename)
    doc = fitz.open(filepath)
    print(f"\nProcessing: {filename} ({len(doc)} pages)")
    
    label_specs = {
        "filename": filename,
        "pages": []
    }
    
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        rect = page.rect
        width_pt = rect.width
        height_pt = rect.height
        width_mm = width_pt * 25.4 / 72.0
        height_mm = height_pt * 25.4 / 72.0
        
        text = page.get_text("text").strip()
        
        # Render high-res PNG (2x zoom = 144 DPI or 3x = 216 DPI)
        matrix = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        
        base_name = os.path.splitext(filename)[0]
        png_name = f"{base_name}_p{page_idx+1}.png"
        png_path = os.path.join(RENDERS_DIR, png_name)
        pix.save(png_path)
        
        print(f"  Page {page_idx+1}: {width_pt:.1f}pt x {height_pt:.1f}pt ({width_mm:.1f}mm x {height_mm:.1f}mm)")
        print(f"  Saved render: {png_name} ({pix.width}x{pix.height}px)")
        print(f"  Text snippet: {repr(text[:120])}")
        
        label_specs["pages"].append({
            "page_num": page_idx + 1,
            "width_mm": round(width_mm, 2),
            "height_mm": round(height_mm, 2),
            "width_px": pix.width,
            "height_px": pix.height,
            "render_file": png_name,
            "text": text
        })
        
    doc.close()

import json
with open(os.path.join(BASE_DIR, "labels", "label_specs.json"), "w", encoding="utf-8") as f:
    json.dump(specs, f, indent=2, ensure_ascii=False)

print("\nAll label renders and specifications extracted successfully.")
