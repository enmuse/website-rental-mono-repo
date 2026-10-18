#!/usr/bin/env python3
"""
setup_stripe.py — Programmatic Stripe Product & Payment Link Generator

Creates and verifies the following recurring subscription products in Stripe:
  1. Frontline Website Rental: $49/mo flat
  2. WNC Trade Network Corridor Lease Tier A: $1,250/mo
  3. WNC Trade Network Corridor Lease Tier B: $950/mo
  4. WNC Trade Network Corridor Lease Tier C: $750/mo

Generates live buy.stripe.com payment links with mobile phone and business name collection.
Saves all Product IDs, Price IDs, and Payment URLs into data/stripe_products.json.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
OUTPUT_FILE = REPO_ROOT / "data" / "stripe_products.json"

def load_stripe_key():
    if not ENV_FILE.exists():
        sys.exit("❌ .env file not found")
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("STRIPE_SECRET_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("❌ STRIPE_SECRET_KEY not found in .env")

def stripe_api(endpoint: str, key: str, method: str = "GET", data: dict = None) -> dict:
    url = f"https://api.stripe.com/v1/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    encoded_data = None
    if data:
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"❌ Stripe API Error ({e.code}) on /{endpoint}: {err_body}")
        raise e

def create_or_find_product(key: str, name: str, description: str) -> str:
    # Check if already exists by searching active products
    res = stripe_api("products?limit=50&active=true", key)
    for p in res.get("data", []):
        if p.get("name") == name:
            print(f"   ✓ Found existing Product: '{name}' ({p['id']})")
            return p["id"]
            
    # Create product
    print(f"   🔨 Creating Product: '{name}'...")
    create_res = stripe_api(
        "products",
        key,
        method="POST",
        data={
            "name": name,
            "description": description,
            "active": "true"
        }
    )
    prod_id = create_res["id"]
    print(f"   ✓ Created Product: {prod_id}")
    return prod_id

def create_or_find_price(key: str, product_id: str, amount_cents: int, interval: str = "month") -> str:
    # Check if price already exists for product
    res = stripe_api(f"prices?product={product_id}&active=true", key)
    for p in res.get("data", []):
        if p.get("unit_amount") == amount_cents and p.get("recurring", {}).get("interval") == interval:
            print(f"   ✓ Found existing Price: ${amount_cents / 100:.2f}/{interval} ({p['id']})")
            return p["id"]
            
    print(f"   🔨 Creating Price: ${amount_cents / 100:.2f}/{interval}...")
    create_res = stripe_api(
        "prices",
        key,
        method="POST",
        data={
            "product": product_id,
            "unit_amount": str(amount_cents),
            "currency": "usd",
            "recurring[interval]": interval,
            "active": "true"
        }
    )
    price_id = create_res["id"]
    print(f"   ✓ Created Price: {price_id}")
    return price_id

def create_or_find_payment_link(key: str, price_id: str) -> str:
    # Check if payment link already exists for this price
    res = stripe_api("payment_links?limit=50", key)
    for pl in res.get("data", []):
        if pl.get("active") and any(item.get("price") == price_id for item in pl.get("line_items", {}).get("data", [])):
            print(f"   ✓ Found existing Payment Link: {pl['url']}")
            return pl["url"]
            
    print(f"   🔨 Creating Payment Link for Price: {price_id}...")
    create_res = stripe_api(
        "payment_links",
        key,
        method="POST",
        data={
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
            "phone_number_collection[enabled]": "true",
            "allow_promotion_codes": "true",
            "custom_fields[0][key]": "business_name",
            "custom_fields[0][label][type]": "custom",
            "custom_fields[0][label][custom]": "Contractor / Company Name",
            "custom_fields[0][type]": "text",
            "custom_fields[0][optional]": "false"
        }
    )
    url = create_res["url"]
    print(f"   ✓ Generated Live Payment Link: {url}")
    return url

def main():
    print("=========================================================")
    print("💳 WNC Website Rental & Corridor Lease Stripe Setup Engine")
    print("=========================================================\n")
    
    key = load_stripe_key()
    print("🔑 Loaded Stripe Key (Prefix: " + key[:7] + "...)\n")
    
    products_catalog = [
        {
            "id_tag": "website_rental_49",
            "name": "WNC Trade Contractor Website Rental",
            "description": "High-performance 100/100 speed website rental, edge hosting, ongoing updates, and direct phone dispatch by Ridgeline Trade Network.",
            "amount_cents": 4900,
            "interval": "month",
            "badge": "$49.00 / month flat"
        },
        {
            "id_tag": "corridor_lease_tier_a_1250",
            "name": "WNC Trade Network — Exclusive Corridor Lease (Tier A)",
            "description": "Exclusive dispatch routing of all unbranded Google organic search traffic from high-ticket regional trade corridors (Metro Asheville Tree, Southern Plateau Excavating, Highlands-Cashiers Septic, etc.) directly to your business phone.",
            "amount_cents": 125000,
            "interval": "month",
            "badge": "$1,250.00 / month"
        },
        {
            "id_tag": "corridor_lease_tier_b_950",
            "name": "WNC Trade Network — Exclusive Corridor Lease (Tier B)",
            "description": "Exclusive dispatch routing of unbranded Google organic search traffic from regional trade corridors (Central West Roofing, Southern Plateau Retaining Walls, High Country Crawlspace, Water Systems, Deck Building) directly to your dispatch phone.",
            "amount_cents": 95000,
            "interval": "month",
            "badge": "$950.00 / month"
        },
        {
            "id_tag": "corridor_lease_tier_c_750",
            "name": "WNC Trade Network — Exclusive Corridor Lease (Tier C)",
            "description": "Exclusive dispatch routing of unbranded Google organic search traffic from regional trade corridors (East Foothills Driveway Paving & Grading) directly to your dispatch phone.",
            "amount_cents": 75000,
            "interval": "month",
            "badge": "$750.00 / month"
        }
    ]
    
    results = {}
    
    for item in products_catalog:
        print(f"📦 Processing: {item['name']} ({item['badge']})")
        prod_id = create_or_find_product(key, item["name"], item["description"])
        price_id = create_or_find_price(key, prod_id, item["amount_cents"], item["interval"])
        payment_link = create_or_find_payment_link(key, price_id)
        
        results[item["id_tag"]] = {
            "name": item["name"],
            "product_id": prod_id,
            "price_id": price_id,
            "amount_usd": item["amount_cents"] / 100,
            "interval": item["interval"],
            "payment_link": payment_link,
            "badge": item["badge"]
        }
        print()
        
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print(f"💾 Saved Stripe catalog to {OUTPUT_FILE.relative_to(REPO_ROOT)}\n")
    print("=========================================================")
    print("🎉 ALL PRODUCTS & PAYMENT LINKS ARE LIVE!")
    print("=========================================================")
    for tag, d in results.items():
        print(f" • {d['name']} ({d['badge']})")
        print(f"   URL: {d['payment_link']}\n")

if __name__ == "__main__":
    main()
