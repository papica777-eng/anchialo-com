import os
import re
import csv
import json
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

RAW_PAGES_DIR = ensure_dir(os.path.join(BASE_DIR, "scraped_pages"))
DATA_DIR = ensure_dir(os.path.join(BASE_DIR, "data"))
BLOG_MD_DIR = ensure_dir(os.path.join(DATA_DIR, "blog_markdown"))
ASSETS_DIR = ensure_dir(os.path.join(BASE_DIR, "assets", "images"))
PROD_IMG_DIR = ensure_dir(os.path.join(ASSETS_DIR, "products"))
BLOG_IMG_DIR = ensure_dir(os.path.join(ASSETS_DIR, "blog"))

def fetch_sitemap_urls(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return [], []
        root = ET.fromstring(r.content)
        urls = []
        images = []
        for child in root:
            loc = child.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is not None and loc.text:
                urls.append(loc.text.strip())
            for img in child.findall("{http://www.google.com/schemas/sitemap-image/1.1}image"):
                img_loc = img.find("{http://www.google.com/schemas/sitemap-image/1.1}loc")
                img_title = img.find("{http://www.google.com/schemas/sitemap-image/1.1}title")
                if img_loc is not None and img_loc.text:
                    images.append({
                        "url": img_loc.text.strip(),
                        "title": img_title.text.strip() if img_title is not None and img_title.text else "",
                        "page_url": loc.text.strip() if loc is not None and loc.text else ""
                    })
        return urls, images
    except Exception as e:
        print(f"Error fetching sitemap {url}: {e}")
        return [], []

def download_file(url, target_path):
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return True
    try:
        r = requests.get(url, headers=HEADERS, timeout=45)
        if r.status_code == 200:
            with open(target_path, "wb") as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return False

def clean_filename(s):
    s = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', s)
    return s[:100]

def main():
    print("=== ANCHIALO.COM SOURCE HARVESTER & DATA EXTRACTOR ===")
    
    # 1. Fetch Sitemaps
    print("\n[1/5] Fetching sitemaps...")
    page_urls, _ = fetch_sitemap_urls("https://www.anchialo.com/pages-sitemap.xml")
    product_urls, product_images = fetch_sitemap_urls("https://www.anchialo.com/store-products-sitemap.xml")
    blog_urls, blog_images = fetch_sitemap_urls("https://www.anchialo.com/blog-posts-sitemap.xml")
    plan_urls, _ = fetch_sitemap_urls("https://www.anchialo.com/pricing-plans-sitemap.xml")

    all_urls = list(dict.fromkeys(page_urls + product_urls + blog_urls + plan_urls))
    print(f"Total Unique URLs discovered: {len(all_urls)}")
    print(f" - Main Pages: {len(page_urls)}")
    print(f" - Product Pages: {len(product_urls)}")
    print(f" - Blog Posts: {len(blog_urls)}")

    # 2. Scrape Pages & Extract Data
    print("\n[2/5] Downloading HTML pages & parsing structured schemas...")
    products_data = []
    blog_data = []
    wix_viewer_saved = False

    for idx, page_url in enumerate(all_urls, 1):
        parsed = urlparse(page_url)
        path = parsed.path.strip("/")
        if not path:
            filename = "index.html"
        else:
            filename = clean_filename(path.replace("/", "_")) + ".html"
        
        filepath = os.path.join(RAW_PAGES_DIR, filename)
        print(f"[{idx}/{len(all_urls)}] Fetching: {page_url} -> {filename}")
        
        try:
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                with open(filepath, "r", encoding="utf-8") as f:
                    html_text = f.read()
            else:
                r = requests.get(page_url, headers=HEADERS, timeout=30)
                if r.status_code != 200:
                    print(f"  Warning: status {r.status_code}")
                    continue
                html_text = r.text
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html_text)

            soup = BeautifulSoup(html_text, "html.parser")

            # Extract Wix Viewer Model once (from home or first page)
            if not wix_viewer_saved:
                vm_tag = soup.find("script", id="wix-viewer-model")
                if vm_tag and vm_tag.string:
                    try:
                        vm_json = json.loads(vm_tag.string)
                        with open(os.path.join(DATA_DIR, "wix_viewer_model.json"), "w", encoding="utf-8") as vmf:
                            json.dump(vm_json, vmf, indent=2, ensure_ascii=False)
                        print("  ✓ Saved wix_viewer_model.json")
                        wix_viewer_saved = True
                    except Exception:
                        pass
                
                warmup_tag = soup.find("script", id="wix-warmup-data")
                if warmup_tag and warmup_tag.string:
                    try:
                        wu_json = json.loads(warmup_tag.string)
                        with open(os.path.join(DATA_DIR, "wix_warmup_data.json"), "w", encoding="utf-8") as wuf:
                            json.dump(wu_json, wuf, indent=2, ensure_ascii=False)
                        print("  ✓ Saved wix_warmup_data.json")
                    except Exception:
                        pass

            # Parse LD+JSON for Products
            if "/product-page/" in page_url:
                prod_entry = {
                    "url": page_url,
                    "slug": path.split("/")[-1],
                    "title": soup.title.string.strip() if soup.title else "",
                    "name": "",
                    "sku": "",
                    "price": "",
                    "currency": "BGN",
                    "description": "",
                    "images": [],
                    "availability": "InStock"
                }
                for s in soup.find_all("script", type="application/ld+json"):
                    try:
                        d = json.loads(s.string)
                        if d.get("@type") == "Product":
                            prod_entry["name"] = d.get("name", "")
                            prod_entry["description"] = d.get("description", "")
                            prod_entry["sku"] = d.get("sku", "")
                            offers = d.get("offers", {})
                            if isinstance(offers, dict):
                                prod_entry["price"] = str(offers.get("price", ""))
                                prod_entry["currency"] = offers.get("priceCurrency", "BGN")
                                prod_entry["availability"] = offers.get("availability", "")
                            imgs = d.get("image", [])
                            if isinstance(imgs, list):
                                prod_entry["images"] = [
                                    (im.get("contentUrl") or im.get("url") or str(im)) if isinstance(im, dict) else str(im)
                                    for im in imgs
                                ]
                            elif isinstance(imgs, dict):
                                prod_entry["images"] = [imgs.get("contentUrl") or imgs.get("url") or str(imgs)]
                            elif isinstance(imgs, str):
                                prod_entry["images"] = [imgs]
                    except Exception:
                        pass
                if not prod_entry["name"] and prod_entry["title"]:
                    prod_entry["name"] = prod_entry["title"]
                products_data.append(prod_entry)

            # Parse LD+JSON for Blog Posts
            if "/post/" in page_url:
                post_entry = {
                    "url": page_url,
                    "slug": path.split("/")[-1],
                    "title": soup.title.string.strip() if soup.title else "",
                    "headline": "",
                    "datePublished": "",
                    "dateModified": "",
                    "author": "Anchialo",
                    "description": "",
                    "image": "",
                    "body_text": ""
                }
                for s in soup.find_all("script", type="application/ld+json"):
                    try:
                        d = json.loads(s.string)
                        if d.get("@type") in ["BlogPosting", "Article"]:
                            post_entry["headline"] = d.get("headline", "")
                            post_entry["datePublished"] = d.get("datePublished", "")
                            post_entry["dateModified"] = d.get("dateModified", "")
                            post_entry["description"] = d.get("description", "")
                            post_entry["image"] = d.get("image", "")
                    except Exception:
                        pass
                
                # Extract main article body text from DOM
                article_elem = soup.find("article") or soup.find("main")
                if article_elem:
                    post_entry["body_text"] = article_elem.get_text(separator="\n", strip=True)
                
                blog_data.append(post_entry)

        except Exception as e:
            print(f"Error scraping {page_url}: {e}")

    # 3. Save Structured Data
    print("\n[3/5] Saving Structured Catalog and Blog Data...")
    with open(os.path.join(DATA_DIR, "products.json"), "w", encoding="utf-8") as f:
        json.dump(products_data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved {len(products_data)} products to data/products.json")

    # CSV for WooCommerce / Shopify import
    with open(os.path.join(DATA_DIR, "products.csv"), "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "currency", "sku", "description", "images", "url", "availability"])
        writer.writeheader()
        for p in products_data:
            writer.writerow({
                "name": p["name"],
                "price": p["price"],
                "currency": p["currency"],
                "sku": p["sku"],
                "description": p["description"],
                "images": ";".join(p["images"]),
                "url": p["url"],
                "availability": p["availability"]
            })
    print(f"  ✓ Saved {len(products_data)} products to data/products.csv (Shopify/WooCommerce format)")

    with open(os.path.join(DATA_DIR, "blog_posts.json"), "w", encoding="utf-8") as f:
        json.dump(blog_data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved {len(blog_data)} blog posts to data/blog_posts.json")

    # Generate Markdown blog files
    for post in blog_data:
        md_name = f"{post['slug']}.md"
        md_path = os.path.join(BLOG_MD_DIR, md_name)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"title: \"{post['headline'] or post['title']}\"\n")
            f.write(f"date: \"{post['datePublished']}\"\n")
            f.write(f"slug: \"{post['slug']}\"\n")
            f.write(f"author: \"{post['author']}\"\n")
            f.write(f"image: \"{post['image']}\"\n")
            f.write(f"url: \"{post['url']}\"\n")
            f.write("---\n\n")
            f.write(f"# {post['headline'] or post['title']}\n\n")
            if post["description"]:
                f.write(f"> {post['description']}\n\n")
            if post["image"]:
                f.write(f"![Featured Image]({post['image']})\n\n")
            f.write(post["body_text"] + "\n")
    print(f"  ✓ Created {len(blog_data)} Markdown files in data/blog_markdown/")

    # 4. Download Product & Blog Images
    print("\n[4/5] Downloading all media assets...")
    print(f"Downloading {len(product_images)} product images...")
    for idx, img in enumerate(product_images, 1):
        url = img["url"]
        fname = clean_filename(os.path.basename(urlparse(url).path))
        if not fname.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            fname += ".png"
        target = os.path.join(PROD_IMG_DIR, f"{idx:02d}_{fname}")
        download_file(url, target)
    print(f"  ✓ Product images saved to assets/images/products/")

    print(f"Downloading {len(blog_images)} blog images...")
    for idx, img in enumerate(blog_images, 1):
        url = img["url"]
        fname = clean_filename(os.path.basename(urlparse(url).path))
        if not fname.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            fname += ".webp"
        target = os.path.join(BLOG_IMG_DIR, f"{idx:02d}_{fname}")
        download_file(url, target)
    print(f"  ✓ Blog images saved to assets/images/blog/")

    print("\n[5/5] Extraction Finished Successfully!")

if __name__ == "__main__":
    main()
