# ANCHIALO — E-Commerce & CMS Migration Guide

This guide describes how to migrate the archived Anchialo store from Wix to modern platforms (Shopify, WooCommerce, WordPress, or Next.js/Vite).

---

## 1. Migrating Products to Shopify / WooCommerce

The repository includes a ready-to-import CSV file: `data/products.csv`.

### A. Shopify Import:
1. Log into your Shopify Admin -> **Products**.
2. Click **Import** (top right).
3. Select `data/products.csv`.
4. Check the box *"Overwrite any current products that have the same handle"* if updating existing ones.
5. Click **Upload and preview**, then click **Import products**.
   - Names, Descriptions, Prices ($49 USD), and Multi-Image URLs from `assets/images/products/` will be imported automatically!

### B. WooCommerce (WordPress) Import:
1. Log into WordPress Admin -> **WooCommerce** -> **Products**.
2. Click **Import** at the top.
3. Choose `data/products.csv` and click **Continue**.
4. Column mapping is already aligned:
   - `name` -> Product Name
   - `price` -> Regular Price
   - `description` -> Description
   - `images` -> Images (comma/semicolon separated)
   - `sku` -> SKU
5. Click **Run the importer**.

---

## 2. Migrating Blog Articles to WordPress / Ghost / Astro

The repository includes:
- `data/blog_posts.json` (Structured JSON array of 16 articles)
- `data/blog_markdown/*.md` (16 clean Markdown files with YAML frontmatter)

### For Astro / Next.js / Static Site Generators:
Copy `data/blog_markdown/*.md` directly into your content collection directory:
```bash
cp -r data/blog_markdown/* src/content/blog/
```

### For WordPress:
Use the standard WordPress REST API or WP-CLI to import:
```bash
wp post create --post_type=post --post_title="Title" --post_content="Content"
```

---

## 3. Print Shop Production Specifications

When ordering prints from a packaging printer (e.g. Avery Dennison, MCC Label, or Bulgarian label print houses like Dunav Press / Rotoprint):

- **Side Wrap Die-Cut**: `280 mm × 38 mm` (Corners: 1mm radius).
- **Top Lid Die-Cut**: Circular `Ø 86 mm`.
- **Material**: White Gloss or Matte Synthetic BOPP Film (waterproof and oil-resistant against magnesium brine).
- **Adhesive**: High-tack permanent acrylic emulsion.
- **Finishing**: Matte Soft-Touch Lamination with Gold Hot-Stamping on logo and dividers.
