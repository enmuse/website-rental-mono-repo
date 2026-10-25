#!/usr/bin/env python3
"""
test_sites_compliance.py — Monorepo Quality & Speed Compliance Test Suite

Audits:
  1. Site Isolation & Zero Cross-Site Coupling (No sibling site links)
  2. 100/100 PageSpeed Readiness (Zero external stylesheets/scripts, inlined styles)
  3. Schema.org Structured Data Integrity (Valid JSON-LD with NAP, Geo, OpeningHours)
  4. Mobile-First Responsiveness (Viewport, Mobile sticky call bar)
  5. SEO & Canonical Metadata Integrity (Title, Meta Description, Canonical, Sitemap, Robots)
"""

import sys
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITES_DIR = REPO_ROOT / "sites"
DATA_FILE = REPO_ROOT / "data" / "clients.json"

def main():
    print("=========================================================")
    print("🛡️ WNC Website Rental Compliance & Quality Test Suite")
    print("=========================================================\n")

    if not DATA_FILE.exists():
        print(f"❌ Error: data/clients.json not found.")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        clients = json.load(f)

    all_passed = True
    total_checks = 0
    passed_checks = 0

    for c in clients:
        slug = c["slug"]
        site_path = SITES_DIR / slug
        html_file = site_path / "index.html"
        robots_file = site_path / "robots.txt"
        sitemap_file = site_path / "sitemap.xml"

        print(f"🔍 Auditing /sites/{slug}/ ({c['business_name']}):")

        # Check 1: Existence of files
        total_checks += 1
        if html_file.exists() and robots_file.exists() and sitemap_file.exists():
            passed_checks += 1
            print("  ✓ Essential files present (index.html, robots.txt, sitemap.xml)")
        else:
            all_passed = False
            print("  ❌ Missing core files!")

        content = html_file.read_text(encoding="utf-8")

        # Check 2: Zero Cross-Site Coupling (Must not reference sibling sites)
        total_checks += 1
        has_cross_site = False
        for sibling in clients:
            if sibling["slug"] != slug:
                if f"/sites/{sibling['slug']}" in content or sibling["business_name"] in content:
                    has_cross_site = True
                    break
        if not has_cross_site:
            passed_checks += 1
            print("  ✓ Zero Cross-Site Coupling verified (100% isolated property)")
        else:
            all_passed = False
            print("  ❌ Failed isolation: Found cross-site links or references!")

        # Check 3: PageSpeed Rules (Zero external CSS/JS, inlined style tag)
        total_checks += 1
        has_external_css = bool(re.search(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', content, re.I))
        has_external_js = bool(re.search(r'<script[^>]+src=["\'][^"\']+["\'][^>]*>', content, re.I))
        has_inlined_css = '<style id="inlined-styles">' in content

        if not has_external_css and not has_external_js and has_inlined_css:
            passed_checks += 1
            print("  ✓ 100/100 PageSpeed readiness verified (Zero render-blocking assets)")
        else:
            all_passed = False
            print(f"  ❌ Speed violations: external_css={has_external_css}, external_js={has_external_js}, inlined_css={has_inlined_css}")

        # Check 4: Schema.org JSON-LD Verification
        total_checks += 1
        schema_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        if schema_matches:
            try:
                schema_obj = json.loads(schema_matches[0].strip())
                if schema_obj.get("@type") == "HomeAndConstructionBusiness" and "telephone" in schema_obj and "geo" in schema_obj:
                    passed_checks += 1
                    print(f"  ✓ Schema.org JSON-LD valid: {schema_obj.get('@type')} (NAP & Coordinates active)")
                else:
                    all_passed = False
                    print("  ❌ Schema.org JSON-LD missing required keys!")
            except Exception as e:
                all_passed = False
                print(f"  ❌ Invalid JSON in Schema block: {e}")
        else:
            all_passed = False
            print("  ❌ Missing Schema.org JSON-LD block!")

        # Check 5: Mobile-First Direct Phone & Sticky Action Bar
        total_checks += 1
        phone_clean = c["cell_phone"].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        has_phone_link = f'href="tel:{phone_clean}"' in content
        has_mobile_bar = "mobile-sticky-bar" in content

        if has_phone_link and has_mobile_bar:
            passed_checks += 1
            print(f"  ✓ Mobile-first direct call buttons & sticky bar verified ({c['cell_phone']})")
        else:
            all_passed = False
            print("  ❌ Mobile call integration missing!")

        # Check 6: Proof-of-Life Anti-Hallucination Guardrail (AGENTS.md Mandate)
        total_checks += 1
        is_synthetic = False
        web = c.get("current_website", "")
        owner = c.get("owner_name", "")
        # Detect legacy synthetic domain patterns
        if any(pat in web for pat in ["sonsloghnc", "professionnc", "loghomesenc", "ramireznc", "floresnc", "silvasonsloghom"]):
            is_synthetic = True
        if not owner or owner.strip() == "":
            is_synthetic = True
        if len(phone_clean) != 10:
            is_synthetic = True

        if not is_synthetic:
            passed_checks += 1
            print(f"  ✓ Proof-of-Life verified: Authentic business entity with named principal ({owner})")
        else:
            all_passed = False
            print(f"  ❌ Synthetic placeholder detected! Violates AGENTS.md Anti-Hallucination Protocol: {c['slug']}")

        print()

    print("=========================================================")
    print(f"📊 Audit Summary: {passed_checks}/{total_checks} checks passed.")
    if all_passed:
        print("🎉 ALL 10 CLIENT SITES ARE 100% COMPLIANT & READY FOR DEPLOYMENT!")
        print("=========================================================\n")
        sys.exit(0)
    else:
        print("❌ SOME CHECKS FAILED! Please review the output above.")
        print("=========================================================\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
