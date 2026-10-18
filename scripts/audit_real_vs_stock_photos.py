#!/usr/bin/env python3
"""
audit_real_vs_stock_photos.py — Forensic Photo Audit

Audits images on each contractor's existing website to distinguish between:
  - GENUINE LOCAL PHOTOS: Real trucks, owner/crew, custom project sites, WNC terrain.
  - STOCK IMAGES: Stock libraries (Shutterstock, iStock, Unsplash, generic agency filler).
"""

import urllib.request
import re
import json
from urllib.parse import urljoin

SITES_TO_AUDIT = [
    ("tates-grading", "https://tatesgradingnc.com"),
    ("turning-leaf-tree", "https://turningleaftreenc.com"),
    ("dirtworks-septic", "https://dirttworks.com"),
    ("riveras-roofing", "https://riverasconstructionsllc.com"),
    ("mateos-retaining-walls", "https://mateoscl.com"),
    ("tri-city-paving", "https://tricitypavinginc.com"),
    ("capstone-crawlspace", "https://capstonecrawlspace.com"),
    ("coomers-well-pump", "https://coomerswellandpump.com"),
    ("wnc-decks", "https://hendersonvilledeckbuilders.com")
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def audit_site(slug, url):
    print(f"\n=======================================================")
    print(f"🔍 AUDITING: {slug} ({url})")
    print(f"=======================================================")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            html = r.read().decode("utf-8", errors="ignore")
            
            # Find all image URLs
            img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I)
            bg_tags = re.findall(r'url\(["\']?([^)"\']+\.(?:jpg|jpeg|png|webp))["\']?\)', html, re.I)
            raw_links = list(set(img_tags + bg_tags))
            
            stock_found = []
            local_found = []
            logos_found = []

            for link in raw_links:
                full_url = urljoin(url, link)
                lower = full_url.lower()

                # Filter out svg/icons
                if any(ext in lower for ext in ['.svg', 'icon', 'favicon', 'facebook', 'instagram', 'pixel', 'badge']):
                    continue
                
                # Check logo
                if 'logo' in lower:
                    logos_found.append(full_url)
                    continue

                # Indicators of stock photos
                is_stock = any(kw in lower for kw in [
                    'stock', 'shutterstock', 'getty', 'istock', 'adobe', 'depositphotos',
                    'dreamstime', 'bigstock', '123rf', 'freepik', 'unsplash', 'pexels',
                    'pixabay', 'generic', 'placeholder', 'sample'
                ])
                
                # Check Aztec Media CRM (Riveras has an agency folder 'Stock')
                if 'stock%2f' in lower or '/stock/' in lower:
                    is_stock = True

                if is_stock:
                    stock_found.append(full_url)
                else:
                    local_found.append(full_url)

            print(f"  • Logos Found ({len(logos_found)}):")
            for l in logos_found[:3]:
                print(f"      🏷️  {l}")

            print(f"  • Stock Images Detected ({len(stock_found)}):")
            for s in stock_found[:4]:
                print(f"      ⚠️  [STOCK] {s}")

            print(f"  • Authentic Local Photos Detected ({len(local_found)}):")
            for loc in local_found[:5]:
                print(f"      📸  [LOCAL] {loc}")

            return {
                "slug": slug,
                "url": url,
                "logos": logos_found,
                "stock": stock_found,
                "local": local_found
            }
    except Exception as e:
        print(f"  ❌ Error fetching {url}: {e}")
        return {"slug": slug, "url": url, "error": str(e)}

def main():
    results = {}
    for slug, url in SITES_TO_AUDIT:
        results[slug] = audit_site(slug, url)
    
    with open("data/photo_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
