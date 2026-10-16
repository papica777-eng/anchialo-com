# ANCHIALO — Pomorie Black Sea Minerals Platform & Master Archive

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-gold.svg)](LICENSE)
[![Origin: Pomorie Bulgaria](https://img.shields.io/badge/Origin-Pomorie%20Bulgaria%20(EU)-blue.svg)]()
[![Formulation: TGA 2025](https://img.shields.io/badge/Formulation-TGA%20Australia%202025-green.svg)]()
[![Print Standard: CMYK 300 DPI](https://img.shields.io/badge/Print-CMYK%20300%20DPI-red.svg)]()

> Official digital archive, e-commerce data assets, and high-end print-ready packaging suite for **ANCHIALO** (Azimut 6000 Ltd, Pomorie, Bulgaria).
> Preserved, extracted, and mathematically harmonized according to the Golden Ratio ($\Phi = 1.618$).

---

## 🏛️ Executive Summary

This repository contains the complete frontend codebase, structured data schemas, media assets, and 2025 Australian export packaging files for **ANCHIALO** (`anchialo.com`):

1. **Production-Ready Packaging Suite (2025 Australian Master & EU)**:
   - **Side Wrap-Around Labels**: Exact physical dimensions **28.0 cm × 3.8 cm** (3307 × 449 px @ 300 DPI). Tailored to fit 28.8 cm circumference cosmetic tubs without overlapping or curving over the edge.
   - **Top Lid Circular Labels**: Exact physical diameter **8.6 cm** (1016 × 1016 px @ 300 DPI).
   - **TGA-Compliant Verbatim Text**: 100% exact copy of the 2025 Australian Master Specification for all 5 signature blends:
     - 🌼 **Arnica Blend** (`ARNICA BLEND`)
     - 🍇 **Grape Blend** (`GRAPE BLEND`)
     - 🌲 **Juniper Blend** (`JUNIPER BLEND`)
     - 🪻 **Lavender Blend** (`LAVENDER BLEND`)
     - 🌿 **Rosemary Blend** (`ROSEMARY BLEND`)
   - **Print-Ready CMYK PDFs & 300 DPI Renders**: Ready for offset, digital, or flexographic print runs.

2. **Full Website Harvest (`https://www.anchialo.com`)**:
   - 42 HTML pages scraped with intact DOM, OpenGraph meta tags, and schema.org markup.
   - Complete structured product catalog exported as **`products.json`** and **`products.csv`** (Shopify & WooCommerce 1-click import ready).
   - All 16 blog posts and balneotherapy clinical research exported as **`blog_posts.json`** and formatted **Markdown** files (`data/blog_markdown/*.md`).
   - High-resolution media assets archived locally in `assets/images/`.

---

## 📐 Packaging Specifications & Golden Ratio ($\Phi = 1.618$)

| Parameter | Specification | Physical Units | Digital Units (300 DPI) |
|---|---|---|---|
| **Side Wrap Label** | Circumference minus 8mm tolerance | 280 mm × 38 mm | 3307 px × 449 px |
| **Top Lid Label** | Circular recessed lid insert | 86 mm diameter | 1016 px × 1016 px |
| **Color Space** | CMYK (ISO Coated v2 / FOGRA39) | CMYK | 300 DPI |
| **Bleed Margins** | 2 mm safety margin included | 2 mm | 24 px |
| **Barcode** | EAN-13 | GTIN-13 | `3 800230 111746` |
| **Expiry & Lot** | Official production lot | Text | `Lot № 07 / 25.12.2027` |
| **Manufacturer** | Azimut 6000 Ltd | Pomorie 8200 | Ivan Vazov 18 str., Bulgaria |

---

## 🗂️ Repository Structure

```
anchialo-com/
├── index.html                   # Sovereign Web Portal & Interactive Showcase
├── README.md                    # System Documentation & Printing Guide
├── MIGRATION_GUIDE.md           # Instructions for Shopify/WooCommerce/WordPress
├── data/
│   ├── products.csv             # 1-Click Import Catalog (Shopify/WooCommerce)
│   ├── products.json            # JSON Schema for Headless Next.js/Vite
│   ├── blog_posts.json          # 16 Balneotherapy Articles (JSON)
│   ├── blog_markdown/           # 16 Markdown Articles with Frontmatter
│   ├── wix_viewer_model.json    # Full Raw Wix Underlying Data Model
│   └── wix_warmup_data.json     # Full Raw Wix SSR Data Payload
├── assets/
│   ├── images/
│   │   ├── products/            # High-Resolution Product Photography
│   │   └── blog/                # High-Resolution Blog Imagery
│   └── mockups/                 # 8K 3D Studio Mockups of Luxury Tubs
├── labels/
│   ├── original/                # Original 10 PDF Labels from Google Drive
│   ├── Dual Magnesium...docx    # Sotir's Master Australian Text 2025
│   ├── azimut_logo.png          # Official Azimut 6000 Ltd Vector Brand Mark
│   ├── pomorie_aerial.png       # High-Res Aerial Shot of Pomorie Spit
│   └── production_ready/        # 10 Print-Ready Production Files (Φ = 1.618)
│       ├── html/                # Responsive HTML5 Vector Source Templates
│       ├── high_res_png_300dpi/ # 300 DPI Master Proofs
│       └── pdf_print_ready_cmyk/# Print-Ready CMYK PDFs (For Print Shop)
└── scraped_pages/               # 42 Static Rendered HTML Snapshots
```

---

## 🖨️ Instructions for Print Shop (Инструкции за Печатницата)

1. **Файлове за страничния етикет (Side Wrap)**:
   - Папка: `labels/production_ready/pdf_print_ready_cmyk/Side_Label_*_280x38mm_PRINT_READY.pdf`
   - Размер на щанцата (Die-Cut): **280 мм ширина × 38 мм височина**.
   - Медия: Водоустойчив полипропилен (BOPP / White Matte Film) с матов лак (Soft-Touch Matte Varnish) и златен топъл печат (Gold Hot Foil Stamping) за надписа `ANCHIALO` и разделителните линии.

2. **Файлове за капака (Top Lid Label)**:
   - Папка: `labels/production_ready/pdf_print_ready_cmyk/Top_Lid_*_86mm_PRINT_READY.pdf`
   - Размер на щанцата: **Кръгъл щанц диаметър 86 мм**.
   - Медия: Кръгъл самозалепващ стикер (BOPP / Permanent Adhesive).

---

## ⚡ Instant RAM Disk Mirror (`R:\`)

All production print PDFs and high-resolution renders are mirrored to the high-speed RAM disk:
```
R:\ANCHIALO_PRINT_READY_LABELS_2025\
├── pdf_print_ready_cmyk/
└── high_res_png_300dpi/
```

---

## 🚀 Quick Start (Local Web Server)

To browse the interactive showcase and product catalog locally:
```powershell
python -m http.server 8080
# Open http://localhost:8080 in your browser
```

---

**Brand:** ANCHIALO — Pomorie Black Sea Balneology  
**Manufacturer:** AZIMUT 6000 Ltd, Ivan Vazov 18 str., 8200 Pomorie, Bulgaria  
**Founder:** Sotir Kichukov
