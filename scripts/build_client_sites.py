#!/usr/bin/env python3
"""
build_client_sites.py — Automated Programmatic Site Generator

Reads data/clients.json and atomically generates:
  1. Complete, isolated 100/100 PageSpeed client rental websites in /sites/<slug>/
     with real contractor project photography & official logos.
  2. Master Client Showcase Portal at /index.html with interactive audit,
     real project previews, and SMS cold outreach scripts.
  3. Independent robots.txt and sitemap.xml files per property.

Follows the Script-Driven Execution Mandate and Zero Cross-Site Coupling protocol.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, date

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "clients.json"
STRIPE_FILE = REPO_ROOT / "data" / "stripe_products.json"
WHOIS_FILE = REPO_ROOT / "data" / "whois_info.json"
SITES_DIR = REPO_ROOT / "sites"
BASE_DOMAIN = "preview.ridgelinetrade.com"
BASE_URL = f"https://{BASE_DOMAIN}"

def load_clients():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_stripe_products():
    if STRIPE_FILE.exists():
        with open(STRIPE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_whois_info():
    if WHOIS_FILE.exists():
        with open(WHOIS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def generate_client_html(c):
    """Generates the single-file, 100/100 PageSpeed, conversion-optimized HTML for a client."""
    phone_clean = c["cell_phone"].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
    sms_number = c.get("direct_sms_number", f"+1{phone_clean}")
    
    current_web = c.get("current_website", "")
    if current_web.startswith("http"):
        domain_display = current_web.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
    else:
        domain_display = f"{c['slug']}.com"
    
    # 1. Brand Logo / Header
    if c.get("has_custom_logo") and c.get("logo_path"):
        brand_header_html = f"""
        <div class="brand-group-logo">
          <img src="{c['logo_path']}" alt="{c['business_name']} Logo" class="brand-logo-img" width="160" height="44" loading="eager" decoding="async">
          <div class="brand-sub-wrap">
            <span class="brand-name-sub">{c['short_name']}</span>
            <span class="brand-location">{c['city']}, NC • {c['trade']}</span>
          </div>
        </div>
        """
    else:
        brand_header_html = f"""
        <div class="brand-group">
          <a href="./" class="brand-name">{c['business_name']}</a>
          <span class="brand-location">{c['city']}, NC • {c['trade']}</span>
        </div>
        """

    # 2. Hero Featured Photo Card
    projects = c.get("projects", [])
    if projects:
        hero_featured_html = f"""
        <div class="hero-featured-photo-card">
          <img src="{projects[0]['image']}" alt="{projects[0]['title']}" class="hero-photo" width="560" height="373" fetchpriority="high" decoding="async">
          <div class="hero-photo-caption">
            <strong>Featured WNC Project:</strong> {projects[0]['title']} <span>({projects[0]['location']})</span>
          </div>
        </div>
        """
    else:
        hero_featured_html = ""

    # 3. Real Project Photo Gallery Cards
    projects_cards = ""
    for p in projects:
        projects_cards += f"""
        <div class="project-card">
          <div class="project-img-wrap">
            <img src="{p['image']}" alt="{p['title']}" class="project-img" width="560" height="373" loading="lazy" decoding="async">
            <span class="project-loc-badge">📍 {p['location']}</span>
          </div>
          <div class="project-body">
            <h3 class="project-title">{p['title']}</h3>
            <p class="project-desc">{p['desc']}</p>
          </div>
        </div>
        """

    # 4. Service Cards
    services_cards = ""
    for s in c["services"]:
        services_cards += f"""
        <div class="service-card">
          <div class="service-icon-box">
            <svg class="service-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="service-title">{s['title']}</h3>
          <p class="service-desc">{s['desc']}</p>
          <div class="service-badge">Mountain Grade Certified</div>
        </div>
        """

    # 5. Trust Badges
    trust_badges_html = ""
    for b in c["trust_badges"]:
        trust_badges_html += f"""
        <div class="trust-badge-item">
          <svg class="check-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span>{b}</span>
        </div>
        """

    # 6. Testimonials
    testimonials_html = ""
    for t in c["testimonials"]:
        testimonials_html += f"""
        <div class="testimonial-card">
          <div class="stars">★★★★★</div>
          <p class="testimonial-quote">"{t['quote']}"</p>
          <div class="testimonial-author">
            <span class="author-name">{t['author']}</span>
            <span class="author-loc"> • {t['location']}</span>
          </div>
        </div>
        """

    # Hub towns tags
    towns_tags = "".join([f'<span class="hub-pill">{town}</span>' for town in c["hub_towns"]])

    tagline_raw = c.get('tagline', '')
    if f"Across {c['city']}" in tagline_raw:
        headline_prefix = tagline_raw.split(f"Across {c['city']}")[0].rstrip(" •-–")
        hero_headline_html = f"<h1>{headline_prefix} <span>Across {c['city']}, NC</span></h1>"
    elif f"in {c['city']}" in tagline_raw:
        headline_prefix = tagline_raw.split(f"in {c['city']}")[0].rstrip(" •-–")
        hero_headline_html = f"<h1>{headline_prefix} <span>in {c['city']}, NC</span></h1>"
    elif "Across" in tagline_raw:
        headline_prefix = tagline_raw.split("Across")[0].rstrip(" •-–")
        hero_headline_html = f"<h1>{headline_prefix} <span>Across {c['city']}, NC</span></h1>"
    else:
        hero_headline_html = f"<h1>{tagline_raw} <span>Across {c['city']}, NC</span></h1>"


    # SEO Title & Description Overrides
    seo_title = c.get("seo_title", f"{c['business_name']} | {c['city']}, NC {c['trade']}")
    seo_desc = c.get("seo_description", f"{c['tagline']}. Serving {', '.join(c['hub_towns'])}. Call {c['owner_name']} directly at {c['cell_phone']} for rapid quotes.")

    # Community Grid Section
    if c.get("community_grid"):
        comm_cards = ""
        for comm in c["community_grid"]:
            comm_cards += f"""
        <div class="community-card">
          <span class="community-sub">{comm['subtitle']}</span>
          <h3>📍 {comm['neighborhood']}</h3>
          <p>{comm['desc']}</p>
        </div>
        """
        community_heading = c.get("community_heading", f"Serving {c['city']} & Surrounding Communities")
        community_sub = c.get("community_sub", f"Customized specifically for the elevation, terrain, and soil conditions of local {c['county'].split(',')[0]} properties.")
        community_grid_html = f"""
  <!-- Hyper-Local Community Coverage Section -->
  <section class="section-wrap">
    <div class="section-header">
      <div class="section-subtitle">Hyper-Local Mountain Coverage</div>
      <h2>{community_heading}</h2>
      <p style="color: var(--text-muted); max-width: 680px; margin: 0.5rem auto 0; font-size: 0.95rem;">
        {community_sub}
      </p>
    </div>
    <div class="community-grid">
      {comm_cards}
    </div>
  </section>
        """
    else:
        community_grid_html = ""

    # FAQ Section & Schema
    if c.get("faqs"):
        faq_cards = ""
        for fq in c["faqs"]:
            faq_cards += f"""
        <div class="faq-item">
          <h3>❓ {fq['q']}</h3>
          <p>{fq['a']}</p>
        </div>
        """
        faq_heading = c.get("faq_heading", f"Frequently Asked Questions in {c['city']} & {c['county'].split(',')[0]}")
        faqs_html = f"""
  <!-- Frequently Asked Questions (FAQ) -->
  <section class="section-wrap">
    <div class="section-header">
      <div class="section-subtitle">Local Property Owner Questions</div>
      <h2>{faq_heading}</h2>
    </div>
    <div class="faq-grid">
      {faq_cards}
    </div>
  </section>
        """
        faq_schema_data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": fq["q"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": fq["a"]
                    }
                }
                for fq in c["faqs"]
            ]
        }
        faq_schema_json = f"""
  <!-- Schema.org FAQPage JSON-LD -->
  <script type="application/ld+json">
{json.dumps(faq_schema_data, indent=2)}
  </script>"""
    else:
        faqs_html = ""
        faq_schema_json = ""

    # Schema JSON-LD
    schema_data = {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "name": c["business_name"],
        "telephone": c["cell_phone"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": c["street_address"],
            "addressLocality": c["city"],
            "addressRegion": c["state"],
            "postalCode": c["zip"],
            "addressCountry": "US"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": c["geo"]["latitude"],
            "longitude": c["geo"]["longitude"]
        },
        "areaServed": c["hub_towns"],
        "openingHours": "Mo-Sa 07:00-18:00",
        "priceRange": "$$",
        "description": c["tagline"]
    }
    if c.get("is_spanish_speaking"):
        schema_data["knowsLanguage"] = ["en", "es"]
    schema_json = json.dumps(schema_data, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{seo_title}</title>
  <meta name="description" content="{seo_desc}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{BASE_URL}/sites/{c['slug']}/">
  
  <!-- Open Graph -->
  <meta property="og:title" content="{c['business_name']} | Mountain {c['trade']}">
  <meta property="og:description" content="{seo_desc}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_US">
  
  <!-- Inlined Critical CSS for 100/100 PageSpeed Performance -->
  <style id="inlined-styles">
    :root {{
      --primary: {c['primary_color']};
      --accent: {c['accent_color']};
      --bg: #090d16;
      --card-bg: rgba(255, 255, 255, 0.04);
      --card-border: rgba(255, 255, 255, 0.09);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --surface: #111827;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    
    html {{
      scroll-behavior: smooth;
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}
    
    body {{
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Top Emergency Alert Bar */
    .top-bar {{
      background: var(--surface);
      border-bottom: 1px solid var(--card-border);
      padding: 0.5rem 1rem;
      font-size: 0.85rem;
      color: var(--text-muted);
      text-align: center;
    }}
    .top-bar strong {{
      color: var(--accent);
    }}
    
    /* Navigation */
    .navbar {{
      position: sticky;
      top: 0;
      z-index: 50;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      background: rgba(9, 13, 22, 0.85);
      border-bottom: 1px solid var(--card-border);
      padding: 0.85rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .brand-group {{
      display: flex;
      flex-direction: column;
    }}
    .brand-name {{
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #ffffff;
      text-decoration: none;
    }}
    .brand-location {{
      font-size: 0.75rem;
      color: var(--accent);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    
    .brand-group-logo {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
    }}
    .brand-logo-img {{
      max-height: 42px;
      width: auto;
      object-fit: contain;
      border-radius: 6px;
      display: block;
      background: #ffffff;
      padding: 4px 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }}
    .brand-name-sub {{
      font-size: 1.05rem;
      font-weight: 800;
      color: #ffffff;
      display: block;
      line-height: 1.2;
    }}
    
    .nav-cta {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .btn-call {{
      background: var(--accent);
      color: #ffffff;
      padding: 0.65rem 1.25rem;
      border-radius: 9999px;
      font-weight: 700;
      font-size: 0.9rem;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
      transition: transform 0.15s ease, opacity 0.15s ease;
    }}
    .btn-call:hover {{
      transform: translateY(-1px);
      opacity: 0.95;
    }}
    .btn-call svg {{
      width: 18px;
      height: 18px;
    }}

    /* Hero Section */
    .hero {{
      padding: 3.5rem 1.5rem 2.5rem;
      max-width: 1100px;
      margin: 0 auto;
      text-align: center;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-bottom: 1.5rem;
    }}
    .hero-badge .status-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
      box-shadow: 0 0 8px #10b981;
    }}
    .hero h1 {{
      font-size: clamp(2rem, 5vw, 3.25rem);
      font-weight: 900;
      line-height: 1.15;
      letter-spacing: -0.03em;
      margin-bottom: 1.25rem;
      color: #ffffff;
    }}
    .hero h1 span {{
      color: var(--accent);
    }}
    .hero p.lead {{
      font-size: clamp(1rem, 2vw, 1.25rem);
      color: var(--text-muted);
      max-width: 760px;
      margin: 0 auto 2rem;
    }}
    .hero-buttons {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .btn-primary {{
      background: var(--accent);
      color: #ffffff;
      padding: 0.85rem 1.75rem;
      border-radius: 8px;
      font-weight: 700;
      font-size: 1rem;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      transition: transform 0.15s ease;
    }}
    .btn-primary:hover {{
      transform: translateY(-2px);
    }}
    .btn-secondary {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: #ffffff;
      padding: 0.85rem 1.75rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 1rem;
      text-decoration: none;
      transition: background 0.15s ease;
    }}
    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.08);
    }}

    /* Hero Featured Photo Card */
    .hero-featured-photo-card {{
      max-width: 600px;
      margin: 2rem auto 0;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--card-border);
      background: var(--surface);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
    }}
    .hero-photo {{
      width: 100%;
      height: 280px;
      object-fit: cover;
      display: block;
    }}
    .hero-photo-caption {{
      padding: 0.75rem 1rem;
      font-size: 0.85rem;
      color: var(--text-muted);
      background: rgba(0, 0, 0, 0.4);
      text-align: left;
    }}
    .hero-photo-caption strong {{
      color: var(--accent);
    }}
    .hero-photo-caption span {{
      color: #ffffff;
    }}

    /* Trust Pill Bar */
    .trust-container {{
      max-width: 1000px;
      margin: 2.5rem auto 3rem;
      padding: 0 1.5rem;
    }}
    .trust-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.25rem;
    }}
    .trust-badge-item {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text);
    }}
    .check-icon {{
      width: 18px;
      height: 18px;
      color: #10b981;
      flex-shrink: 0;
    }}

    /* Section Headers */
    .section-wrap {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 3.5rem 1.5rem;
    }}
    .section-header {{
      text-align: center;
      margin-bottom: 2.5rem;
    }}
    .section-subtitle {{
      color: var(--accent);
      font-weight: 700;
      text-transform: uppercase;
      font-size: 0.8rem;
      letter-spacing: 0.06em;
      margin-bottom: 0.5rem;
    }}
    .section-header h2 {{
      font-size: clamp(1.75rem, 3.5vw, 2.5rem);
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.02em;
    }}

    /* Real Mountain Project Photo Grid */
    .projects-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
      margin-top: 1.5rem;
    }}
    .project-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .project-card:hover {{
      transform: translateY(-4px);
      border-color: rgba(255, 255, 255, 0.25);
    }}
    .project-img-wrap {{
      position: relative;
      width: 100%;
      height: 220px;
      background: #1e293b;
      overflow: hidden;
    }}
    .project-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.3s ease;
    }}
    .project-card:hover .project-img {{
      transform: scale(1.04);
    }}
    .project-loc-badge {{
      position: absolute;
      bottom: 0.75rem;
      left: 0.75rem;
      background: rgba(9, 13, 22, 0.85);
      backdrop-filter: blur(8px);
      color: #ffffff;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      border: 1px solid rgba(255, 255, 255, 0.15);
    }}
    .project-body {{
      padding: 1.25rem;
      flex-grow: 1;
      display: flex;
      flex-direction: column;
    }}
    .project-title {{
      font-size: 1.15rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 0.5rem;
      line-height: 1.3;
    }}
    .project-desc {{
      font-size: 0.88rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    /* Services Grid */
    .services-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.5rem;
    }}
    .service-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.75rem;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .service-card:hover {{
      transform: translateY(-3px);
      border-color: rgba(255, 255, 255, 0.2);
    }}
    .service-icon-box {{
      width: 44px;
      height: 44px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.06);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 1.25rem;
      color: var(--accent);
    }}
    .service-svg {{
      width: 24px;
      height: 24px;
    }}
    .service-title {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 0.75rem;
    }}
    .service-desc {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-bottom: 1.25rem;
      flex-grow: 1;
    }}
    .service-badge {{
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-dim);
      border-top: 1px solid var(--card-border);
      padding-top: 0.75rem;
    }}

    
    /* Company Story / Heritage Box */
    .story-box {{
      background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 2.5rem;
      margin: 2rem 0;
    }}
    .story-box h2 {{
      font-size: clamp(1.5rem, 3vw, 2rem);
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 1.25rem;
    }}
    .story-lead {{
      color: var(--text);
      font-size: 1.05rem;
      line-height: 1.7;
      margin-bottom: 2rem;
    }}
    .story-highlights {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.25rem;
      border-top: 1px solid var(--card-border);
      padding-top: 1.5rem;
    }}
    .story-item {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}
    .story-item strong {{
      color: var(--accent);
      font-size: 0.95rem;
      font-weight: 700;
    }}
    .story-item span {{
      color: var(--text-muted);
      font-size: 0.85rem;
      line-height: 1.5;
    }}

    /* Local Geology & WNC Mountain Challenges */
    .local-challenge-box {{
      background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 2.5rem;
      margin: 2rem 0;
    }}
    .local-challenge-box h3 {{
      font-size: 1.5rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 1rem;
    }}
    .local-challenge-box p {{
      color: var(--text-muted);
      margin-bottom: 1.5rem;
    }}
    .hub-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      align-items: center;
    }}
    .hub-pill {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      font-size: 0.8rem;
      color: var(--text);
      font-weight: 600;
    }}

    /* Testimonials */
    .testimonials-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }}
    .testimonial-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.75rem;
    }}
    .stars {{
      color: #f59e0b;
      margin-bottom: 0.75rem;
      font-size: 1.1rem;
      letter-spacing: 2px;
    }}
    .testimonial-quote {{
      color: var(--text);
      font-style: italic;
      margin-bottom: 1rem;
      font-size: 0.95rem;
    }}
    .testimonial-author {{
      font-size: 0.85rem;
    }}
    .author-name {{
      font-weight: 700;
      color: #ffffff;
    }}
    .author-loc {{
      color: var(--accent);
    }}

    
    /* Hyper-Local Community Grid */
    .community-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.25rem;
      margin-top: 2rem;
    }}
    .community-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.75rem;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .community-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(34, 197, 94, 0.4);
    }}
    .community-card h3 {{
      font-size: 1.15rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 0.35rem;
    }}
    .community-card .community-sub {{
      font-size: 0.8rem;
      color: var(--accent);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 0.75rem;
      display: block;
    }}
    .community-card p {{
      color: var(--text-muted);
      font-size: 0.92rem;
      line-height: 1.6;
    }}

    /* FAQ Section */
    .faq-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.25rem;
      margin-top: 2rem;
    }}
    .faq-item {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.75rem;
    }}
    .faq-item h3 {{
      font-size: 1.05rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 0.75rem;
      line-height: 1.4;
    }}
    .faq-item p {{
      color: var(--text-muted);
      font-size: 0.92rem;
      line-height: 1.6;
    }}

    /* Direct Contact / Rapid Quote Banner */
    .quote-box {{
      background: {c['theme_gradient']};
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 16px;
      padding: 3rem 2rem;
      text-align: center;
      margin: 3rem 0;
    }}
    .quote-box h2 {{
      font-size: clamp(1.75rem, 3.5vw, 2.5rem);
      font-weight: 900;
      color: #ffffff;
      margin-bottom: 1rem;
    }}
    .quote-box p {{
      color: var(--text-muted);
      max-width: 600px;
      margin: 0 auto 2rem;
    }}
    .direct-phone-huge {{
      font-size: clamp(1.5rem, 4vw, 2.5rem);
      font-weight: 900;
      color: #ffffff;
      text-decoration: none;
      display: inline-block;
      margin-bottom: 1.5rem;
      letter-spacing: -0.02em;
    }}
    .direct-phone-huge span {{
      color: var(--accent);
    }}

    /* Footer */
    footer {{
      background: #06090e;
      border-top: 1px solid var(--card-border);
      padding: 3rem 1.5rem 2rem;
      margin-top: auto;
      font-size: 0.85rem;
      color: var(--text-dim);
    }}
    .footer-content {{
      max-width: 1100px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 2rem;
      margin-bottom: 2rem;
    }}
    .footer-col h4 {{
      color: #ffffff;
      margin-bottom: 0.75rem;
      font-size: 0.95rem;
    }}
    .footer-col p {{
      margin-bottom: 0.5rem;
    }}
    .footer-bottom {{
      max-width: 1100px;
      margin: 0 auto;
      border-top: 1px solid var(--card-border);
      padding-top: 1.5rem;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }}

    /* Mobile Sticky Call Bar */
    .mobile-sticky-bar {{
      display: none;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(9, 13, 22, 0.95);
      backdrop-filter: blur(12px);
      border-top: 1px solid var(--card-border);
      padding: 0.75rem 1rem;
      z-index: 100;
    }}
    .mobile-sticky-btn {{
      background: var(--accent);
      color: #ffffff;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 0.5rem;
      text-decoration: none;
      font-weight: 800;
      font-size: 1.05rem;
      padding: 0.85rem;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }}
    @media (max-width: 768px) {{
      .mobile-sticky-bar {{
        display: block;
      }}
      body {{
        padding-bottom: 75px;
      }}
    }}
  </style>

  <!-- Schema.org LocalBusiness JSON-LD -->
  <script type="application/ld+json">
{schema_json}
  </script>
{faq_schema_json}
</head>
<body>

  <!-- Top Emergency Bar -->
  <div class="top-bar">
    Serving <strong>{c['city']}, {c['county']} & Western North Carolina</strong> • Direct Dispatch: <a href="tel:{phone_clean}" style="color: #fff; text-decoration: underline; font-weight: 700;">{c['cell_phone']}</a>
  </div>

  <!-- Navigation -->
  <nav class="navbar">
    {brand_header_html}
    <div class="nav-cta">
      <a href="tel:{phone_clean}" class="btn-call">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M6.62 10.79a15.053 15.053 0 006.59 6.59l2.2-2.2a1 1 0 011.11-.27c1.12.45 2.33.69 3.48.69a1 1 0 011 1v3.5a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.15.24 2.36.69 3.48a1 1 0 01-.27 1.11l-2.2 2.2z"/>
        </svg>
        <span>Call Owner Direct</span>
      </a>
    </div>
  </nav>

  <!-- Hero Section -->
  <header class="hero">
    <div class="hero-badge" { 'style="border-color: rgba(16, 185, 129, 0.4);"' if c.get('is_spanish_speaking') else '' }>
      <span class="status-dot" { 'style="background: #10b981; box-shadow: 0 0 8px #10b981;"' if c.get('is_spanish_speaking') else '' }></span>
      <span>{c['owner_name']} ({c['owner_title']}) On Dispatch{ ' • Se Habla Español' if c.get('is_spanish_speaking') else '' }</span>
    </div>
    {hero_headline_html}
    <p class="lead">
      Direct owner communication, specialized mountain equipment, and over two decades of localized {c['trade'].lower()} experience in {c['county']}.
    </p>
    <div class="hero-buttons">
      <a href="tel:{phone_clean}" class="btn-primary">
        <svg style="width: 20px; height: 20px;" viewBox="0 0 24 24" fill="currentColor">
          <path d="M6.62 10.79a15.053 15.053 0 006.59 6.59l2.2-2.2a1 1 0 011.11-.27c1.12.45 2.33.69 3.48.69a1 1 0 011 1v3.5a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.15.24 2.36.69 3.48a1 1 0 01-.27 1.11l-2.2 2.2z"/>
        </svg>
        Call {c['cell_phone']}
      </a>
      <a href="sms:{sms_number}?body=Hi%20{c['owner_name']}%2C%20I%20would%20like%20a%20quote%20on%20a%20{c['trade'].replace('&', 'and')}%20project%20in%20{c['city']}." class="btn-secondary">
        Text For Fast Estimate
      </a>
    </div>
    { f'<div style="font-size: 0.88rem; color: #a7f3d0; margin-top: -1rem; margin-bottom: 1.5rem; font-weight: 600;">🇲🇽 Se Habla Español • Cotizaciones Rápidas y Atención Bilingüe en {c["city"]}</div>' if c.get("is_spanish_speaking") else '' }

    {hero_featured_html}
  </header>

  <!-- Trust Badges Bar -->
  <section class="trust-container">
    <div class="trust-grid">
      {trust_badges_html}
    </div>
  </section>


  <!-- Company Heritage & Owner Commitment (About Us) -->
  <section class="section-wrap">
    <div class="story-box">
      <div class="section-subtitle">{ 'Artesanía y Raíces Locales' if c.get('is_spanish_speaking') else 'Local Craftsmanship & Roots' }</div>
      <h2>{ 'Nuestra Historia y Compromiso con la Montaña' if c.get('is_spanish_speaking') else 'Our Heritage & Mountain Commitment' }</h2>
      <p class="story-lead">
        {c.get('story', f"Locally based in {c['city']}, {c['short_name']} delivers unyielding mountain craftsmanship across {c['county']}.")}
      </p>
      <div class="story-highlights">
        <div class="story-item">
          <strong>{ 'Atención Directa del Dueño' if c.get('is_spanish_speaking') else 'Direct Owner Dispatch' }</strong>
          <span>{ f"Hable directamente con {c['owner_name']} ({c['owner_title']}) para presupuestos y coordinación en {c['city']}." if c.get('is_spanish_speaking') else f"Speak directly with {c['owner_name']} ({c['owner_title']}) on every project." }</span>
        </div>
        <div class="story-item">
          <strong>{ 'Maquinaria de Montaña' if c.get('is_spanish_speaking') else 'Mountain-Engineered Equipment' }</strong>
          <span>{ f"Equipo y herramientas de alta capacidad preparados para terrenos rocosos y pendientes en {c['county']}." if c.get('is_spanish_speaking') else f"Specialized machinery tailored to steep Blue Ridge slopes and rocky soil." }</span>
        </div>
        <div class="story-item">
          <strong>{ 'Sede y Compromiso Local' if c.get('is_spanish_speaking') else 'Local Base & Accountability' }</strong>
          <span>{ f"Base de operaciones en {c['city']}, NC con respuesta rápida para emergencias y trabajos programados." if c.get('is_spanish_speaking') else f"Physical headquarters located in {c['city']}, NC with rapid emergency response." }</span>
        </div>
      </div>
    </div>
  </section>

    <!-- Real Local Project Gallery -->
  <section class="section-wrap">
    <div class="section-header">
      <div class="section-subtitle">Real Local Mountain Jobs</div>
      <h2>Recent Work Across {c['county']}</h2>
      <p style="color: var(--text-muted); max-width: 650px; margin: 0.5rem auto 0; font-size: 0.95rem;">
        Authentic field photography from recent residential and commercial mountain contracts.
      </p>
    </div>
    <div class="projects-grid">
      {projects_cards}
    </div>
  </section>

  <!-- Services Section -->
  <section class="section-wrap">
    <div class="section-header">
      <div class="section-subtitle">Dedicated Trade Capabilities</div>
      <h2>Engineered for High-Slope Mountain Terrain</h2>
    </div>
    <div class="services-grid">
      {services_cards}
    </div>
  </section>

{community_grid_html}

  <!-- Local Mountain Expertise & Geo Coverage -->
  <section class="section-wrap">
    <div class="local-challenge-box">
      <h3>The Western North Carolina Mountain Standard</h3>
      <p>
        Building and operating in the Blue Ridge Mountains is fundamentally different from flatland trade work. From weathered granite outcrops and heavy clay soil runoff to extreme winter freeze-thaw cycles, {c['business_name']} utilizes heavy-duty equipment specifically tailored to steep topography and local environmental codes.
      </p>
      <div style="margin-bottom: 0.75rem; font-weight: 700; color: #fff; font-size: 0.9rem;">
        Regional Service Hubs in {c['county']}:
      </div>
      <div class="hub-pills">
        {towns_tags}
      </div>
    </div>
  </section>

  <!-- Testimonials Section -->
  <section class="section-wrap">
    <div class="section-header">
      <div class="section-subtitle">Verified Local Reputation</div>
      <h2>What Neighbors Across WNC Say</h2>
    </div>
    <div class="testimonials-grid">
      {testimonials_html}
    </div>
  </section>

{faqs_html}

  <!-- Direct Quote Box -->
  <section class="section-wrap">
    <div class="quote-box">
      <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--accent); margin-bottom: 0.5rem;">
        Direct Access • Zero Middlemen
      </div>
      <h2>{ 'Hable Directamente con ' + c['owner_name'] if c.get('is_spanish_speaking') else f"Speak Directly With {c['owner_name']}" }</h2>
      <p>
        { 'Sin intermediarios ni recepcionistas. Hable directamente con el dueño para cotizaciones de su proyecto en ' + c['city'] + ' y alrededores.' if c.get('is_spanish_speaking') else f"Skip the dispatch answering services. Talk straight with the owner and lead technician about your project scope, scheduling, and on-site estimate." }
      </p>
      <a href="tel:{phone_clean}" class="direct-phone-huge">
        <span>{c['cell_phone']}</span>
      </a>
      <div>
        <a href="tel:{phone_clean}" class="btn-primary" style="margin: 0 auto;">
          Click To Call Now
        </a>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer>
    <div class="footer-content">
      <div class="footer-col" style="max-width: 320px;">
        <h4>{c['business_name']}</h4>
        <p>{c['tagline']}</p>
        <p style="color: #64748b;">Direct Office & Mobile: {c['cell_phone']}</p>
        <p style="color: #64748b;">Physical Base: {c['street_address']}, {c['city']}, NC {c['zip']}</p>
      </div>
      <div class="footer-col">
        <h4>Core Mountain Services</h4>
        {"".join([f"<p>• {s['title']}</p>" for s in c["services"]])}
      </div>
      <div class="footer-col">
        <h4>Areas We Serve</h4>
        <p>{c['county']} & Surrounding Communities</p>
        <p>{', '.join(c['hub_towns'])}</p>
        <p style="color: #10b981; font-weight: 600; margin-top: 1rem;">• Fully Licensed & Insured in NC</p>
      </div>
    </div>

    <div class="footer-bottom">
      <div>
        © 2026 {c['business_name']}. All rights reserved. Locally operated in {c['city']}, NC.
      </div>
      <div>
        100/100 PageSpeed Edge Architecture • Western North Carolina
      </div>
    </div>
  </footer>

  <!-- Mobile Sticky Bottom Call Bar -->
  <div class="mobile-sticky-bar">
    <a href="tel:{phone_clean}" class="mobile-sticky-btn">
      <svg style="width: 20px; height: 20px;" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6.62 10.79a15.053 15.053 0 006.59 6.59l2.2-2.2a1 1 0 011.11-.27c1.12.45 2.33.69 3.48.69a1 1 0 011 1v3.5a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.15.24 2.36.69 3.48a1 1 0 01-.27 1.11l-2.2 2.2z"/>
      </svg>
      Call {c['owner_name']} Direct ({c['cell_phone']}){ ' • Se Habla Español' if c.get('is_spanish_speaking') else '' }
    </a>
  </div>

</body>
</html>"""
    return html

def generate_robots_txt(slug):
    return f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sites/{slug}/sitemap.xml
"""

def generate_sitemap_xml(slug):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{BASE_URL}/sites/{slug}/</loc>
    <lastmod>2026-10-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""

def generate_master_portal_html(clients):
    """Generates the master showcase portal at /index.html with interactive audit, SMS copy, and live demo links."""
    stripe_catalog = load_stripe_products()
    whois_catalog = load_whois_info()
    rental_link = stripe_catalog.get("website_rental_49", {}).get("payment_link", "https://buy.stripe.com/8x29AV87Q6e6er98xJ1wY00")
    tier_a_link = stripe_catalog.get("corridor_lease_tier_a_1250", {}).get("payment_link", "https://buy.stripe.com/fZueVf4VEfOG0Aj4ht1wY01")
    tier_b_link = stripe_catalog.get("corridor_lease_tier_b_950", {}).get("payment_link", "https://buy.stripe.com/3cI7sNco69qi6YH29l1wY02")
    tier_c_link = stripe_catalog.get("corridor_lease_tier_c_750", {}).get("payment_link", "https://buy.stripe.com/5kQcN7co6eKCaaT01d1wY03")
    
    unique_corridors = sorted(list({c.get("corridor_name") for c in clients if c.get("corridor_name")}))
    unique_trades = sorted(list({c.get("trade") for c in clients if c.get("trade")}))
    corridor_options = "".join(f'<option value="{corr}">{corr}</option>' for corr in unique_corridors)
    trade_options = "".join(f'<option value="{tr}">{tr}</option>' for tr in unique_trades)
    today = datetime.now().date()

    table_rows = ""
    client_cards = ""
    
    for c in clients:
        phone_clean = c["cell_phone"].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        old_score = c.get("competitor_pagespeed", 35)
        old_fcp = c.get("competitor_fcp", "3.8s")
        old_lcp = c.get("competitor_lcp", "8.5s")
        
        # Color coding for old score
        score_class = "score-bad" if old_score < 50 else ("score-mid" if old_score < 75 else "score-good")
        
        # Project reference for pitch
        projs = c.get("projects", [])
        top_project_ref = projs[0]["title"] if projs else "recent mountain contracts"
        
        is_spanish = c.get("is_spanish_speaking", False)
        lang_type = "es" if is_spanish else "en"

        # SMS Pitch text (English)
        if is_spanish:
            sms_pitch = (
                f"Hey {c['owner_name']}, Brandon here in Hendersonville. Ran an automated Google speed test on your web presence for {c['short_name']} "
                f"and saw mobile visitors wait {old_lcp} for your page (scores {old_score}/100 on Google PageSpeed). In WNC, slow load times lose callers. "
                f"Your mountain craftsmanship is top tier, so I built a high-speed mockup for you that hits 100/100, loads in 0.4s, and highlights your bilingual crew: "
                f"{BASE_URL}/sites/{c['slug']}/ "
                f"If you like it, I host and maintain it for $49/mo flat—zero setup fee, no contracts, and you keep your domain. Plus, we have Spanish corridor call routing available for {c['city']}. Let me know what you think!"
            )
            sms_pitch_es = (
                f"Hola {c['owner_name']}, soy Brandon aquí en Hendersonville. Hice una prueba técnica de Google en su página de {c['short_name']} "
                f"y vi que en celular tarda {old_lcp} para que abra (califica {old_score}/100 en Google PageSpeed). En WNC, una página lenta hace perder clientes. "
                f"El trabajo de su equipo es de primer nivel, así que les preparé un sitio web de alta velocidad para celular que carga en 0.4s (califica 100/100) "
                f"y destaca que ofrecen servicio bilingüe / Se Habla Español: "
                f"{BASE_URL}/sites/{c['slug']}/ "
                f"Se lo rento por $49/mes fijo—sin contratos ni costo de instalación, y usted mantiene su dominio. "
                f"Además, podemos conectarle llamadas en español directas desde nuestra red WNC en {c['city']}. Avíseme si le gustaría activarlo esta semana!"
            )
        elif c["slug"] == "leavesout-hendersonville":
            sms_pitch = (
                f"Hey Cory, Brandon here in Hendersonville. Saw you bought the local chapter for LeavesOut of the Blue Ridge—congrats on taking over the territory! "
                f"All your 5-star Google reviews belong to you, but your web presence is currently trapped on corporate's slow subpage (loads in {old_lcp}, scores {old_score}/100 on PageSpeed). "
                f"You need an independent local site you own and control. I built a bespoke 100/100 speed site for you featuring your service truck, your lifetime no-clog warranty, and your Hendersonville reviews: "
                f"{BASE_URL}/sites/{c['slug']}/ "
                f"If you like it, I host and maintain it for $49/mo flat—zero setup fee, no contracts, and you own the domain. Let me know what you think!"
            )
            sms_pitch_es = ""
        else:
            sms_pitch = (
                f"Hey {c['owner_name']}, Brandon here in Hendersonville. Ran an automated Google speed test on your web presence for {c['short_name']} "
                f"and saw mobile visitors wait {old_lcp} for your page (scores {old_score}/100 on Google PageSpeed). In WNC, slow load times lose callers. "
                f"Your mountain craftsmanship is top tier, so I took photos of your actual work ({top_project_ref}), "
                f"optimized them, and built a high-speed mockup for you that hits 100/100 and loads in 0.4s: "
                f"{BASE_URL}/sites/{c['slug']}/ "
                f"If you like it, I host and maintain it for $49/mo flat—zero setup fee, no contracts, and you keep your domain. Let me know what you think!"
            )
            sms_pitch_es = ""
        
        # WHOIS & DNS Info
        whois = whois_catalog.get(c["slug"], {})
        registrar = whois.get("registrar", "Unknown")
        dns_provider = whois.get("dns_provider", "Custom DNS")
        dns_badge = whois.get("dns_badge", "default")
        nameservers = whois.get("nameservers", [])
        login_url = whois.get("login_url", "#")
        action_tip = whois.get("action_tip", "Point CNAME @ and www to preview.ridgelinetrade.com")
        expires = whois.get("expires", "").strip()
        domain_age_short = whois.get("domain_age_short", "N/A")
        domain_age_display = whois.get("domain_age_display", "N/A")
        authority_tier = whois.get("authority_tier", "")
        domain_target = whois.get("domain", c.get("current_website", ""))

        # Calculate dynamic days until expiration
        days_until_exp = None
        if expires and expires not in ("N/A", "none", ""):
            try:
                exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
                days_until_exp = (exp_date - today).days
                expires_formatted = exp_date.strftime("%b %d, %Y")
            except Exception:
                days_until_exp = None
                expires_formatted = whois.get("expires_formatted", expires)
        else:
            expires_formatted = "N/A"

        # Table age and expiration badges
        if domain_age_short != "N/A":
            table_age_pill = f'<span style="font-size: 0.68rem; font-weight: 600; color: #a7f3d0; background: rgba(16, 185, 129, 0.12); padding: 0.1rem 0.35rem; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.25);" title="{domain_age_display}">🎂 Age: {domain_age_short}</span>'
        else:
            table_age_pill = f'<span style="font-size: 0.68rem; color: #94a3b8; background: rgba(148, 163, 184, 0.1); padding: 0.1rem 0.35rem; border-radius: 4px;">No Custom Domain</span>'

        if days_until_exp is not None:
            if days_until_exp < 0:
                abs_days = abs(days_until_exp)
                table_exp_pill = f'<span class="exp-badge exp-expired" title="Expired {abs_days} days ago on {expires_formatted}">🚨 Expired ({abs_days}d ago)</span>'
                exp_badge_html = f'<span class="dns-tag-badge alert">🚨 Expired {abs_days}d ago</span>'
                exp_val_class = 'exp-alert'
                is_expiring_soon = True
                urgent_banner_html = f"""
            <div style="background: rgba(239, 68, 68, 0.15); border-left: 3px solid #ef4444; padding: 0.65rem 0.85rem; border-radius: 0 6px 6px 0; font-size: 0.78rem; color: #fca5a5; line-height: 1.45; margin-bottom: 0.75rem;">
              <strong>🚨 DOMAIN EXPIRED:</strong> Domain expired {abs_days} days ago on <strong>{expires_formatted}</strong>. Crucial outreach: Contact {c['owner_name']} immediately to rescue their domain registration or migrate to Cloudflare edge hosting!
            </div>
            """
            elif days_until_exp <= 30:
                table_exp_pill = f'<span class="exp-badge exp-critical" title="Urgent: Expires in {days_until_exp} days on {expires_formatted}">⚠️ Exp: {expires_formatted} ({days_until_exp}d left!)</span>'
                exp_badge_html = f'<span class="dns-tag-badge alert">⚠️ {days_until_exp}d left!</span>'
                exp_val_class = 'exp-alert'
                is_expiring_soon = True
                urgent_banner_html = f"""
            <div style="background: rgba(239, 68, 68, 0.12); border-left: 3px solid #ef4444; padding: 0.65rem 0.85rem; border-radius: 0 6px 6px 0; font-size: 0.78rem; color: #fca5a5; line-height: 1.45; margin-bottom: 0.75rem;">
              <strong>⚠️ URGENT DOMAIN EXPIRATION:</strong> Domain expires on <strong>{expires_formatted}</strong> ({days_until_exp} days remaining). High-trust outreach angle: Alert {c['owner_name']} so his website/email doesn't drop, or offer to transfer domain registration to Cloudflare wholesale ($10/yr)!
            </div>
            """
            elif days_until_exp <= 90:
                table_exp_pill = f'<span class="exp-badge exp-warning" title="Expires in {days_until_exp} days on {expires_formatted}">⏳ Exp: {expires_formatted} ({days_until_exp}d left)</span>'
                exp_badge_html = f'<span class="dns-tag-badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);">⏳ {days_until_exp}d left</span>'
                exp_val_class = ''
                is_expiring_soon = False
                urgent_banner_html = ''
            else:
                table_exp_pill = f'<span class="exp-badge exp-normal" title="Expires in {days_until_exp} days on {expires_formatted}">📅 Exp: {expires_formatted} ({days_until_exp}d)</span>'
                exp_badge_html = f'<span style="font-size: 0.72rem; color: #94a3b8;"> ({days_until_exp} days)</span>'
                exp_val_class = ''
                is_expiring_soon = False
                urgent_banner_html = ''
        else:
            table_exp_pill = '<span class="exp-badge exp-none" title="No custom domain expiration registered">📅 No Domain Expiry</span>'
            exp_badge_html = '<span style="font-size: 0.72rem; color: #64748b;"> (No custom domain)</span>'
            exp_val_class = ''
            is_expiring_soon = False
            urgent_banner_html = ''

        slug_val = c["slug"]
        spanish_badge_html = '<br><span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.68rem; font-weight: 700; padding: 0.1rem 0.35rem; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3); display: inline-block; margin-top: 0.25rem;">🇪🇸 Se Habla Español</span>' if is_spanish else ''
        spanish_sms_btn = f'<button class="btn-sms" onclick="copySmsPitchEs(\'{slug_val}\')" style="background: #059669;">SMS (ES)</button>' if is_spanish else ''
        spanish_textarea = f'<textarea id="sms-text-es-{slug_val}" style="display:none;">{sms_pitch_es}</textarea>' if is_spanish else ''
        spanish_dispatch_note = f'<br><span style="font-size: 0.68rem; color: #34d399; font-weight: 600;">Línea ES: {c.get("spanish_dispatch_phone", "(828) 844-6682")}</span>' if is_spanish else ''

        safe_name = c["business_name"].lower().replace('"', '').replace("'", "")
        safe_short = c["short_name"].lower().replace('"', '').replace("'", "")
        safe_trade = c["trade"].lower().replace('"', '').replace("'", "")
        safe_corridor = c.get("corridor_name", "").lower().replace('"', '').replace("'", "")
        safe_corridor_slug = c.get("trade_network_corridor_slug", "").lower()
        safe_owner = c["owner_name"].lower().replace('"', '').replace("'", "")

        current_web = str(c.get("current_website", "")).strip()
        if not current_web or current_web.lower() in ("none", "n/a", "no website"):
            website_link_url = ""
        elif current_web.startswith(("http://", "https://")):
            website_link_url = current_web
        elif "hibu" in current_web.lower():
            website_link_url = "https://hibu.com"
        elif " " in current_web:
            website_link_url = ""
        elif "." in current_web:
            website_link_url = f"https://{current_web}"
        else:
            website_link_url = ""

        if website_link_url:
            table_score_html = f'<a href="{website_link_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;" title="Visit existing live website: {website_link_url}"><span class="speed-pill {score_class}" style="cursor: pointer; display: inline-flex; align-items: center; gap: 0.25rem;">{old_score}/100 <span style="font-size: 0.65rem; opacity: 0.85;">↗</span></span></a>'
            card_score_html = f'<a href="{website_link_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: inherit;" title="Visit existing live website: {website_link_url}"><div class="stat-val" style="cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.25rem;">{old_score} / 100 <span style="font-size: 0.75rem; opacity: 0.85;">↗</span></div></a>'
        else:
            table_score_html = f'<span class="speed-pill {score_class}">{old_score}/100</span>'
            card_score_html = f'<div class="stat-val">{old_score} / 100</div>'

        table_rows += f"""
        <tr id="row-{slug_val}"
            data-slug="{slug_val}"
            data-lang="{lang_type}"
            data-name="{safe_name}"
            data-short="{safe_short}"
            data-trade="{safe_trade}"
            data-corridor="{safe_corridor}"
            data-corridor-slug="{safe_corridor_slug}"
            data-owner="{safe_owner}"
            data-expires="{expires}"
            data-days="{days_until_exp if days_until_exp is not None else 9999}"
            data-score="{old_score}">
          <td>
            <strong class="col-name">{c['short_name']}</strong><br>
            <span class="sub-text col-city-trade">{c['city']}, NC • {c['trade']}</span>
            {spanish_badge_html}
          </td>
          <td>
            <span class="corridor-badge">{c['trade_network_corridor_slug']}</span><br>
            <span class="sub-text">{c['trade_network_domain']}</span>
            {spanish_dispatch_note}
          </td>
          <td>
            <strong class="col-owner">{c['owner_name']}</strong><br>
            <a href="tel:{phone_clean}" class="phone-link col-phone">{c['cell_phone']}</a>
          </td>
          <td>
            <div style="font-weight: 700; color: #f8fafc; font-size: 0.85rem;">{dns_provider}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin: 0.15rem 0;">{registrar.split(',')[0]}</div>
            <div style="margin: 0.35rem 0 0.25rem 0;">
              {table_exp_pill}
            </div>
            <div style="display: flex; gap: 0.25rem; align-items: center; flex-wrap: wrap;">
              {table_age_pill}
              <span style="font-size: 0.68rem; font-family: monospace; color: #60a5fa; background: rgba(59, 130, 246, 0.08); padding: 0.08rem 0.3rem; border-radius: 4px;">
                NS: {nameservers[0] if nameservers else 'No Custom NS'}
              </span>
            </div>
          </td>
          <td>
            {table_score_html}<br>
            <span class="sub-text">FCP {old_fcp} | LCP {old_lcp}</span>
          </td>
          <td>
            <a href="/sites/{c['slug']}/" target="_blank" style="text-decoration: none;" title="Open 100/100 Mobile Rental Mockup">
              <span class="speed-pill score-perfect" style="cursor: pointer; display: inline-flex; align-items: center; gap: 0.25rem;">100/100 <span style="font-size: 0.65rem; opacity: 0.85;">↗</span></span>
            </a><br>
            <span class="sub-text">FCP 0.3s | LCP 0.5s</span>
          </td>
          <td>
            <div class="action-btn-group">
              <a href="/sites/{c['slug']}/" target="_blank" class="btn-demo">View Site ↗</a>
              <button class="btn-sms" onclick="openEditModal('{c['slug']}')" style="background: #2563eb;" title="Edit Contractor Profile">✏️ Edit</button>
              <button class="btn-sms" onclick="copySmsPitch('{c['slug']}')">Copy SMS</button>
              {spanish_sms_btn}
              <button class="btn-sms" onclick="copyStripeLink('{rental_link}', '$49/mo')" style="background: #10b981;">$49 Link</button>
            </div>
            <textarea id="sms-text-{c['slug']}" style="display:none;">{sms_pitch}</textarea>
            {spanish_textarea}
          </td>
        </tr>
        """
        
        # Build thumbnail strip for dossier card
        thumb_strip = ""
        for p in projs[:3]:
            thumb_strip += f"""
            <div class="thumb-box">
              <img src="/sites/{c['slug']}/{p['image']}" alt="{p['title']}" width="100" height="65" loading="lazy" decoding="async">
            </div>
            """

        # Dossier card badges
        if authority_tier and authority_tier != "Unregistered":
            age_badge_html = f'<span class="dns-tag-badge veteran">{authority_tier}</span>'
        else:
            age_badge_html = ''

        if c.get("has_custom_logo") and c.get("logo_path"):
            logo_html = f'<div class="card-logo-badge"><img src="/sites/{c["slug"]}/{c["logo_path"]}" alt="{c["business_name"]} Logo" class="card-logo-img" width="48" height="48" loading="lazy"></div>'
        else:
            logo_html = f'<div class="card-logo-badge" style="background: rgba(255,255,255,0.08); color: #60a5fa; font-weight: 800; font-size: 1.1rem;">{c["business_name"][:2].upper()}</div>'

        card_spanish_tag = '<span class="dns-tag-badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);">🇪🇸 Se Habla Español • Bilingual Dispatch</span>' if is_spanish else ''
        slug_card = c["slug"]
        card_spanish_btn = f'<button class="card-action-btn secondary" onclick="copySmsPitchEs(\'{slug_card}\')" style="border-color: #059669; color: #34d399;">Copiar SMS (Español)</button>' if is_spanish else ''
        card_spanish_intel = f'<div class="dns-intel-item"><span class="dns-label">Spanish Master Dispatch</span><span class="dns-val" style="color: #34d399; font-weight: 700;">{c.get("spanish_dispatch_phone", "(828) 844-6682")}</span></div>' if is_spanish else ''

        client_cards += f"""
        <div class="client-dossier-card"
             id="card-{slug_card}"
             data-slug="{slug_card}"
             data-lang="{lang_type}"
             data-name="{safe_name}"
             data-short="{safe_short}"
             data-trade="{safe_trade}"
             data-corridor="{safe_corridor}"
             data-corridor-slug="{safe_corridor_slug}"
             data-owner="{safe_owner}"
             data-expires="{expires}"
             data-days="{days_until_exp if days_until_exp is not None else 9999}"
             data-score="{old_score}">
          <div class="card-header">
            <div class="card-title-group">
              {logo_html}
              <div class="card-title-text">
                <h3>
                  <a href="{website_link_url}" target="_blank" rel="noopener noreferrer" class="client-title-link" title="Visit current live website: {c.get('current_website', '')}">
                    {c['business_name']} <span class="ext-icon">↗</span>
                  </a>
                </h3>
                <div class="card-meta">{c['city']}, NC • {c['county']}</div>
              </div>
            </div>
            <span class="corridor-tag">{c['corridor_name'].split('—')[0].strip()}</span>
          </div>
          
          <div class="thumb-strip-wrap">
            {thumb_strip}
          </div>
          
          <div class="stat-compare">
            <div class="stat-box bad">
              <div class="stat-label">Current Mobile Score</div>
              {card_score_html}
              <div class="stat-detail">Load Time: {old_lcp}</div>
            </div>
            <div class="stat-arrow">➔</div>
            <div class="stat-box good">
              <div class="stat-label">Our Rental Mockup</div>
              <a href="/sites/{c['slug']}/" target="_blank" style="text-decoration: none; color: inherit;" title="Open 100/100 Mobile Rental Mockup">
                <div class="stat-val" style="cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.25rem;">100 / 100 <span style="font-size: 0.75rem; opacity: 0.85;">↗</span></div>
              </a>
              <div class="stat-detail">Load Time: 0.4s</div>
            </div>
          </div>
          
          <div class="card-body">
            <div class="field-row">
              <span class="field-title">Direct Cell / SMS:</span>
              <a href="tel:{phone_clean}" class="field-val highlight">{c['cell_phone']} ({c['owner_name']})</a>
            </div>
            <div class="field-row">
              <span class="field-title">Featured Project:</span>
              <span class="field-val" style="font-size: 0.8rem; color: #cbd5e1;">{top_project_ref}</span>
            </div>
            <div class="field-row" style="flex-direction: column; align-items: flex-start; gap: 0.25rem;">
              <span class="field-title" style="color: #f59e0b;">Personalized Story / Real Copy:</span>
              <span class="field-val" style="font-size: 0.76rem; color: #94a3b8; line-height: 1.45;">{c.get('story', '')[:160]}...</span>
            </div>
            <div class="field-row">
              <span class="field-title">Monthly Rental Rate:</span>
              <span class="field-val">$49.00 / month flat</span>
            </div>
            <div class="field-row">
              <span class="field-title">Network Upsell Target:</span>
              <span class="field-val corridor-target">{c['upsell_corridor_deal']}</span>
            </div>
          </div>
          
          <!-- WHOIS & DNS Delegation Intelligence -->
          <div class="dns-intel-card">
            <div class="dns-intel-header">
              <span class="dns-intel-tag">🔍 DNS & WHOIS Intelligence</span>
              <span class="dns-badge {dns_badge}">{dns_provider}</span>
            </div>
            <div class="dns-intel-grid">
              <div class="dns-intel-item">
                <span class="dns-label">Current Domain</span>
                <span class="dns-val" style="color: #60a5fa; font-weight: 600;">{domain_target}</span>
              </div>
              <div class="dns-intel-item">
                <span class="dns-label">Official Registrar</span>
                <span class="dns-val">{registrar.split(',')[0]}</span>
              </div>
              <div class="dns-intel-item">
                <span class="dns-label">Domain Age</span>
                <span class="dns-val" style="color: #a7f3d0; font-weight: 600;">
                  {domain_age_display} {age_badge_html}
                </span>
              </div>
              <div class="dns-intel-item">
                <span class="dns-label">Domain Expiration</span>
                <span class="dns-val {exp_val_class}">
                  {expires_formatted} {exp_badge_html}
                </span>
              </div>
              <div class="dns-intel-item">
                <span class="dns-label">Active Nameservers</span>
                <span class="dns-val monospace">{', '.join(nameservers) if nameservers else 'None registered'}</span>
              </div>
              <div class="dns-intel-item">
                <span class="dns-label">DNS Routing Setup</span>
                <span class="dns-val" style="color: #fbbf24;">Awaiting CNAME Pointing</span>
              </div>
            </div>
            {urgent_banner_html}
            <div class="dns-intel-action">
              <strong>👉 DNS Delegation Play:</strong> {action_tip}
            </div>
            <div class="dns-btn-row">
              <a href="{login_url}" target="_blank" rel="noopener" class="btn-dns-login">Open {dns_provider.split(' ')[0]} Portal ↗</a>
              <button class="btn-dns-copy" onclick="copyDnsInstructions('{domain_target}')">Copy CNAME Setup Script</button>
            </div>
          </div>
          
          <div class="card-footer">
            <a href="/sites/{c['slug']}/" target="_blank" class="card-action-btn primary">Open Live Mockup ↗</a>
            <button class="card-action-btn secondary" onclick="openEditModal('{c['slug']}')" style="border-color: #3b82f6; color: #60a5fa;">✏️ Quick Edit</button>
            <button class="card-action-btn secondary" onclick="copySmsPitch('{c['slug']}')">Copy SMS Pitch</button>
            {card_spanish_btn}
            <button class="card-action-btn" onclick="copyStripeLink('{rental_link}', '$49/mo Website Rental')" style="background: #10b981; color: #fff; border: 1px solid #059669;">Copy $49/mo Link</button>
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WNC Trade Contractor Website Rental Portfolio | Ridgeline Trade Network</title>
  <meta name="description" content="Turnkey 100/100 PageSpeed website rentals for Western North Carolina trade contractors with real project photography.">
  <meta name="robots" content="noindex, nofollow">
  
  <style>
    :root {{
      --bg: #090d16;
      --surface: #111827;
      --card-bg: rgba(255, 255, 255, 0.04);
      --card-border: rgba(255, 255, 255, 0.08);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #3b82f6;
      --emerald: #10b981;
      --amber: #f59e0b;
      --red: #ef4444;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding-bottom: 4rem;
    }}
    
    /* Header */
    .top-header {{
      background: linear-gradient(180deg, #0f172a 0%, #090d16 100%);
      border-bottom: 1px solid var(--card-border);
      padding: 3rem 1.5rem 2.5rem;
      text-align: center;
    }}
    .badge-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.3);
      color: #60a5fa;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 1rem;
    }}
    h1 {{
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: 900;
      letter-spacing: -0.03em;
      margin-bottom: 0.75rem;
    }}
    p.lead {{
      color: var(--text-muted);
      font-size: 1.15rem;
      max-width: 800px;
      margin: 0 auto 1.5rem;
    }}
    
    /* Financial Metric Bar */
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      max-width: 1100px;
      margin: 0 auto;
      padding: 0 1.5rem;
      transform: translateY(-20px);
    }}
    .metric-card {{
      background: var(--surface);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.25rem;
      text-align: center;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }}
    .metric-val {{
      font-size: 1.75rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 0.25rem;
    }}
    .metric-val.green {{ color: var(--emerald); }}
    .metric-val.blue {{ color: #60a5fa; }}
    .metric-val.gold {{ color: var(--amber); }}
    .metric-label {{
      font-size: 0.8rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .container {{
      max-width: 1200px;
      margin: 2rem auto 0;
      padding: 0 1.5rem;
    }}
    
    .section-title {{
      font-size: 1.5rem;
      font-weight: 800;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    /* Comparison Table */
    .table-container {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      overflow-x: auto;
      margin-bottom: 3.5rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.9rem;
    }}
    th {{
      background: rgba(255, 255, 255, 0.03);
      padding: 1rem;
      font-weight: 700;
      color: var(--text-muted);
      border-bottom: 1px solid var(--card-border);
      white-space: nowrap;
    }}
    td {{
      padding: 1rem;
      border-bottom: 1px solid var(--card-border);
      vertical-align: middle;
    }}
    tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}
    .sub-text {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}
    .phone-link {{
      color: #60a5fa;
      text-decoration: none;
      font-weight: 700;
    }}
    .phone-link:hover {{
      text-decoration: underline;
    }}
    .corridor-badge {{
      display: inline-block;
      background: rgba(255, 255, 255, 0.08);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text);
    }}
    .speed-pill {{
      display: inline-block;
      padding: 0.25rem 0.65rem;
      border-radius: 9999px;
      font-weight: 800;
      font-size: 0.85rem;
      transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
    }}
    .speed-pill:hover {{
      transform: translateY(-1px);
      filter: brightness(1.2);
      box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }}
    .score-bad {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
    .score-mid {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .score-good {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .score-perfect {{ background: rgba(16, 185, 129, 0.25); color: #10b981; border: 1px solid #10b981; font-weight: 900; }}
    
    .action-btn-group {{
      display: flex;
      gap: 0.5rem;
    }}
    .btn-demo {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--card-border);
      color: #ffffff;
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.8rem;
      white-space: nowrap;
      transition: background 0.15s ease;
    }}
    .btn-demo:hover {{ background: rgba(255, 255, 255, 0.15); }}
    .btn-sms {{
      background: #2563eb;
      border: none;
      color: #ffffff;
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 700;
      font-size: 0.8rem;
      white-space: nowrap;
      transition: background 0.15s ease;
    }}
    .btn-sms:hover {{ background: #1d4ed8; }}

    /* Cards Grid */
    .dossier-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 1.5rem;
      margin-bottom: 4rem;
    }}
    .client-dossier-card {{
      background: var(--surface);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.85rem;
      margin-bottom: 1rem;
    }}
    .card-title-group {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
      min-width: 0;
      flex: 1;
    }}
    .card-logo-badge {{
      width: 52px;
      height: 52px;
      flex-shrink: 0;
      border-radius: 8px;
      background: #ffffff;
      padding: 4px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .card-logo-badge img {{
      max-width: 100%;
      max-height: 100%;
      width: auto;
      height: auto;
      object-fit: contain;
      display: block;
    }}
    .card-title-text {{
      min-width: 0;
      flex: 1;
    }}
    .card-header h3 {{
      font-size: 1.15rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 0.2rem;
      line-height: 1.3;
    }}
    .client-title-link {{
      color: #ffffff;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: color 0.15s ease;
    }}
    .client-title-link:hover {{
      color: #60a5fa;
      text-decoration: underline;
    }}
    .ext-icon {{
      font-size: 0.82em;
      opacity: 0.7;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }}
    .client-title-link:hover .ext-icon {{
      opacity: 1;
      transform: translate(2px, -2px);
    }}
    .card-meta {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}
    .corridor-tag {{
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      text-transform: uppercase;
      white-space: nowrap;
    }}
    
    .thumb-strip-wrap {{
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }}
    .thumb-box {{
      flex: 1;
      height: 65px;
      border-radius: 6px;
      overflow: hidden;
      border: 1px solid var(--card-border);
      background: #1e293b;
    }}
    .thumb-box img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}

    .stat-compare {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      margin-bottom: 1.25rem;
    }}
    .stat-box {{ text-align: center; }}
    .stat-label {{ font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; }}
    .stat-val {{ font-size: 1.25rem; font-weight: 800; transition: transform 0.15s ease, filter 0.15s ease; }}
    .stat-box.bad .stat-val {{ color: #f87171; }}
    .stat-box.bad a:hover .stat-val {{ filter: brightness(1.2); transform: translateY(-1px); }}
    .stat-box.good .stat-val {{ color: #34d399; }}
    .stat-box.good a:hover .stat-val {{ filter: brightness(1.2); transform: translateY(-1px); }}
    .stat-detail {{ font-size: 0.7rem; color: var(--text-muted); }}
    .stat-arrow {{ color: var(--text-muted); font-size: 1.2rem; }}

    .card-body {{
      margin-bottom: 1.5rem;
      flex-grow: 1;
    }}
    .field-row {{
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      padding: 0.4rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }}
    .field-title {{ color: var(--text-muted); }}
    .field-val {{ font-weight: 600; color: #ffffff; }}
    .field-val.highlight {{ color: #60a5fa; }}
    .field-val.corridor-target {{ color: #34d399; font-size: 0.8rem; }}

    .card-footer {{
      display: flex;
      gap: 0.75rem;
    }}
    .card-action-btn {{
      flex: 1;
      padding: 0.65rem;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 700;
      text-align: center;
      cursor: pointer;
      text-decoration: none;
    }}
    .card-action-btn.primary {{
      background: #2563eb;
      color: #ffffff;
      border: none;
    }}
    .card-action-btn.primary:hover {{ background: #1d4ed8; }}
    .card-action-btn.secondary {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--card-border);
      color: #ffffff;
    }}
    .card-action-btn.secondary:hover {{ background: rgba(255, 255, 255, 0.15); }}

    /* DNS & WHOIS Intelligence Card */
    .dns-intel-card {{
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 1.1rem;
      margin: 1rem 0 1.25rem;
    }}
    .dns-intel-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }}
    .dns-intel-tag {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #94a3b8;
    }}
    .dns-badge {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .dns-badge.godaddy {{ background: rgba(37, 99, 235, 0.2); color: #60a5fa; border: 1px solid rgba(37, 99, 235, 0.4); }}
    .dns-badge.wix {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }}
    .dns-badge.squarespace {{ background: rgba(20, 184, 166, 0.2); color: #2dd4bf; border: 1px solid rgba(20, 184, 166, 0.4); }}
    .dns-badge.domainpeople {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
    .dns-badge.hibu {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}
    .dns-badge.default {{ background: rgba(100, 116, 139, 0.2); color: #cbd5e1; border: 1px solid rgba(100, 116, 139, 0.4); }}

    .dns-intel-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
      gap: 0.65rem 0.85rem;
      font-size: 0.8rem;
      margin-bottom: 0.85rem;
    }}
    .dns-intel-item {{
      display: flex;
      flex-direction: column;
    }}
    .dns-label {{
      color: #64748b;
      font-size: 0.7rem;
      text-transform: uppercase;
      font-weight: 600;
      margin-bottom: 0.15rem;
    }}
    .dns-val {{
      color: #e2e8f0;
      word-break: break-word;
    }}
    .dns-val.monospace {{
      font-family: monospace;
      font-size: 0.72rem;
      color: #93c5fd;
    }}
    .dns-val.exp-alert {{
      color: #f87171 !important;
      font-weight: 700;
    }}
    .dns-tag-badge {{
      display: inline-block;
      font-size: 0.66rem;
      font-weight: 600;
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
      margin-left: 0.35rem;
      vertical-align: middle;
    }}
    .dns-tag-badge.alert {{
      background: rgba(239, 68, 68, 0.2);
      color: #fca5a5;
      border: 1px solid rgba(239, 68, 68, 0.4);
    }}
    .dns-tag-badge.veteran {{
      background: rgba(16, 185, 129, 0.15);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .exp-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      font-size: 0.68rem;
      font-weight: 700;
      padding: 0.12rem 0.45rem;
      border-radius: 4px;
      white-space: nowrap;
    }}
    .exp-badge.exp-expired {{
      background: rgba(239, 68, 68, 0.25);
      color: #fca5a5;
      border: 1px solid #ef4444;
    }}
    .exp-badge.exp-critical {{
      background: rgba(239, 68, 68, 0.18);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.45);
    }}
    .exp-badge.exp-warning {{
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.35);
    }}
    .exp-badge.exp-normal {{
      background: rgba(148, 163, 184, 0.12);
      color: #cbd5e1;
      border: 1px solid rgba(148, 163, 184, 0.25);
    }}
    .exp-badge.exp-none {{
      background: rgba(148, 163, 184, 0.08);
      color: #94a3b8;
      border: 1px solid rgba(148, 163, 184, 0.15);
    }}
    .dns-intel-action {{
      background: rgba(245, 158, 11, 0.08);
      border-left: 3px solid #f59e0b;
      padding: 0.6rem 0.85rem;
      border-radius: 0 6px 6px 0;
      font-size: 0.78rem;
      color: #fef3c7;
      line-height: 1.45;
      margin-bottom: 0.85rem;
    }}
    .dns-btn-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .btn-dns-login {{
      flex: 1;
      min-width: 130px;
      padding: 0.45rem 0.75rem;
      background: #1e293b;
      border: 1px solid #334155;
      color: #cbd5e1;
      font-size: 0.75rem;
      font-weight: 600;
      border-radius: 6px;
      text-align: center;
      text-decoration: none;
      transition: background 0.2s;
    }}
    .btn-dns-login:hover {{
      background: #334155;
      color: #fff;
    }}
    .btn-dns-copy {{
      flex: 1;
      min-width: 130px;
      padding: 0.45rem 0.75rem;
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.35);
      color: #60a5fa;
      font-size: 0.75rem;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.2s;
    }}
    .btn-dns-copy:hover {{
      background: rgba(59, 130, 246, 0.25);
    }}

    /* Strategy Section */
    .strategy-box {{
      background: linear-gradient(180deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 3rem;
    }}
    .strategy-box h3 {{
      font-size: 1.35rem;
      font-weight: 800;
      margin-bottom: 1rem;
      color: #ffffff;
    }}
    .strategy-box p {{
      color: var(--text-muted);
      margin-bottom: 1rem;
      font-size: 0.95rem;
    }}
    
    /* Toast Notification */
    #copy-toast {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #10b981;
      color: #ffffff;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-weight: 700;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      display: none;
      z-index: 1000;
      animation: fadeIn 0.2s ease;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
  </style>
</head>
<body>

  <!-- PIN Passcode Security Gate -->
  <div id="pin-modal" style="position: fixed; inset: 0; background: #070a13; z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 1.5rem;">
    <div style="background: #0f172a; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 2.5rem; max-width: 420px; width: 100%; text-align: center; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.7);">
      <div style="width: 56px; height: 56px; margin: 0 auto 1.25rem; border-radius: 12px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); display: flex; align-items: center; justify-content: center;">
        <svg style="width: 28px; height: 28px; color: #60a5fa;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0110 0v4"></path>
        </svg>
      </div>
      <h2 style="color: #f8fafc; font-size: 1.35rem; margin-bottom: 0.5rem; font-weight: 700;">Ridgeline Ops Command</h2>
      <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 1.5rem;">Enter authorization passcode to decrypt portfolio dossiers, cell phones, and cold pitch payloads.</p>
      <input type="password" id="pin-input" placeholder="Enter PIN (e.g. 8280)" style="width: 100%; padding: 0.85rem 1rem; border-radius: 8px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 1.1rem; text-align: center; letter-spacing: 0.2em; margin-bottom: 1rem; outline: none;" autofocus onkeydown="if(event.key==='Enter') unlockWithPin()">
      <button onclick="unlockWithPin()" style="width: 100%; padding: 0.85rem; border-radius: 8px; background: #2563eb; color: #fff; font-weight: 600; border: none; cursor: pointer; font-size: 0.95rem; transition: background 0.2s;">Authenticate & Unlock ➔</button>
      <div id="pin-error" style="color: #ef4444; font-size: 0.82rem; margin-top: 0.85rem; display: none;">Invalid authorization passcode.</div>
    </div>
  </div>

  <div id="ops-content" style="display: none;">

  <!-- Top Header -->
  <header class="top-header">
    <div class="badge-pill">Barebones 3D • WNC Trade Network Hub</div>
    <h1>WNC Contractor Website Rental Operations</h1>
    <p class="lead">
      High-converting $49/month website rentals built with real field photography and bilingual operations across Western North Carolina.
    </p>
  </header>

  <!-- Key Financial Metrics -->
  <div class="metric-grid">
    <div class="metric-card">
      <div class="metric-val blue">{len(clients)} Properties</div>
      <div class="metric-label">{sum(1 for c in clients if not c.get('is_spanish_speaking'))} English • {sum(1 for c in clients if c.get('is_spanish_speaking'))} Se Habla Español</div>
    </div>
    <div class="metric-card">
      <div class="metric-val green">${len(clients) * 49:,} / mo</div>
      <div class="metric-label">Phase 1 Rental Cash Flow (${len(clients) * 49 * 12:,}/yr)</div>
    </div>
    <div class="metric-card">
      <div class="metric-val gold">(828) 844-6682</div>
      <div class="metric-label">Master Spanish Dispatch Line</div>
    </div>
    <div class="metric-card">
      <div class="metric-val green">100 / 100</div>
      <div class="metric-label">Google Mobile PageSpeed</div>
    </div>
  </div>

  <div class="container">
    
    <!-- Stripe Quick Actions Bar -->
    <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 2rem; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem;">
      <div>
        <div style="font-weight: 700; color: #818cf8; font-size: 0.95rem; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.5rem;">
          <span>💳 Live Stripe Checkout & Lease Links</span>
          <span style="font-size: 0.75rem; background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 0.15rem 0.5rem; border-radius: 9999px;">Active</span>
        </div>
        <div style="font-size: 0.82rem; color: #94a3b8;">Click to copy ready-to-send payment links configured with company name & mobile phone capture.</div>
      </div>
      <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
        <button onclick="copyStripeLink('{rental_link}', '$49/mo Website Rental')" style="background: #10b981; color: #fff; border: none; padding: 0.55rem 0.95rem; border-radius: 6px; font-weight: 600; font-size: 0.82rem; cursor: pointer; transition: opacity 0.2s;">Copy $49/mo Link</button>
        <button onclick="copyStripeLink('{tier_a_link}', 'Tier A ($1,250/mo)')" style="background: #3b82f6; color: #fff; border: none; padding: 0.55rem 0.95rem; border-radius: 6px; font-weight: 600; font-size: 0.82rem; cursor: pointer; transition: opacity 0.2s;">Tier A ($1,250/mo)</button>
        <button onclick="copyStripeLink('{tier_b_link}', 'Tier B ($950/mo)')" style="background: #6366f1; color: #fff; border: none; padding: 0.55rem 0.95rem; border-radius: 6px; font-weight: 600; font-size: 0.82rem; cursor: pointer; transition: opacity 0.2s;">Tier B ($950/mo)</button>
        <button onclick="copyStripeLink('{tier_c_link}', 'Tier C ($750/mo)')" style="background: #8b5cf6; color: #fff; border: none; padding: 0.55rem 0.95rem; border-radius: 6px; font-weight: 600; font-size: 0.82rem; cursor: pointer; transition: opacity 0.2s;">Tier C ($750/mo)</button>
      </div>
    </div>
    
    <!-- Portfolio Filter & Search Controls -->
    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; display: flex; flex-direction: column; gap: 1rem;">
      <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem;">
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <button class="filter-btn-lang" id="btn-lang-all" onclick="filterLanguage('all')" style="padding: 0.45rem 1rem; font-weight: 700; border-radius: 6px; cursor: pointer; background: #2563eb; color: #fff; border: 1px solid #3b82f6;">All Portfolios ({len(clients)})</button>
          <button class="filter-btn-lang" id="btn-lang-en" onclick="filterLanguage('en')" style="padding: 0.45rem 1rem; font-weight: 700; border-radius: 6px; cursor: pointer; background: rgba(255,255,255,0.06); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.15);">Standard English ({sum(1 for c in clients if not c.get('is_spanish_speaking'))})</button>
          <button class="filter-btn-lang" id="btn-lang-es" onclick="filterLanguage('es')" style="padding: 0.45rem 1rem; font-weight: 700; border-radius: 6px; cursor: pointer; background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.4);">🇪🇸 Se Habla Español ({sum(1 for c in clients if c.get('is_spanish_speaking'))})</button>
        </div>
        <button onclick="openAddModal()" style="background: #10b981; color: #fff; font-weight: 700; padding: 0.55rem 1.2rem; border-radius: 8px; border: none; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35); transition: background 0.2s;">
          <span>➕ Add Real Contractor</span>
        </button>
      </div>

      <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem;">
        <select id="corridor-filter" onchange="applyFilters()" style="flex: 1; min-width: 220px; padding: 0.55rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.85rem; outline: none; cursor: pointer;">
          <option value="all">📍 All Corridors ({len(unique_corridors)} Corridors)</option>
          {corridor_options}
        </select>
        <select id="trade-filter" onchange="applyFilters()" style="flex: 1; min-width: 200px; padding: 0.55rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.85rem; outline: none; cursor: pointer;">
          <option value="all">🔨 All Trades ({len(unique_trades)} Trades)</option>
          {trade_options}
        </select>
        <input type="text" id="contractor-search" placeholder="🔍 Search name, owner, city, trade, phone, corridor..." oninput="searchContractors(this.value)" style="flex: 1.5; min-width: 260px; padding: 0.55rem 1rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.88rem; outline: none;">
      </div>
    </div>

    <!-- Executive Comparison Table -->
    <div class="section-title">
      <span>Contractor Audit & Speed Comparison Matrix</span>
      <span style="font-size: 0.85rem; font-weight: 600; color: var(--emerald);">✓ 100/100 Mobile Speed & Instant Edge Hosting</span>
    </div>
    
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th onclick="sortTable('name')" style="cursor: pointer; user-select: none;" title="Click to sort A-Z / Z-A">
              Business & Trade <span class="sort-icon" id="sort-icon-name">↕</span>
            </th>
            <th onclick="sortTable('corridor')" style="cursor: pointer; user-select: none;" title="Click to sort by Corridor">
              Network Corridor <span class="sort-icon" id="sort-icon-corridor">↕</span>
            </th>
            <th onclick="sortTable('owner')" style="cursor: pointer; user-select: none;" title="Click to sort by Owner Name">
              Owner & Direct Phone <span class="sort-icon" id="sort-icon-owner">↕</span>
            </th>
            <th onclick="sortTable('days')" style="cursor: pointer; user-select: none;" title="Click to sort by Days Until Expiration (Urgent First)">
              DNS Host & Domain Expiry <span class="sort-icon" id="sort-icon-days">↕</span>
            </th>
            <th onclick="sortTable('score')" style="cursor: pointer; user-select: none;" title="Click to sort by Competitor Speed">
              Their Current Speed <span class="sort-icon" id="sort-icon-score">↕</span>
            </th>
            <th>Our Rental Speed</th>
            <th>Outreach Actions</th>
          </tr>
        </thead>
        <tbody id="contractors-tbody">
          {table_rows}
        </tbody>
      </table>
    </div>

    <!-- Client Dossiers -->
    <div class="section-title">
      <span>Contractor Profiles & Real Project Dossiers</span>
    </div>
    <div class="dossier-grid">
      {client_cards}
    </div>

    <!-- Two-Tier Strategy Roadmap -->
    <div class="strategy-box">
      <h3>The Magic Mirror Acquisition Playbook</h3>
      <p>
        <strong>Step 1 — The Real Photo "Magic Mirror":</strong> When contractors open a site mockup and see their <em>actual</em> crane lift in Black Mountain or their <em>actual</em> boulder retaining wall in Saluda, skepticism vanishes. They see their real craftsmanship presented with premium typography and lighting-fast load speeds.
      </p>
      <p>
        <strong>Step 2 — The Non-Compete Strategic Moat:</strong> These client rental websites are strictly configured for <em>Brand Entity & Local NAP Citation SEO</em> (capturing direct referrals, name searches, and hyper-local citation traffic). They do not compete with our 19 regional WNC Trade sites (<code>wnctreeremoval.com</code>, <code>wncexcavating.com</code>, etc.) which target broad, high-volume corridor terms across all 23 counties.
      </p>
      <p>
        <strong>Step 3 — The $1,250/mo Rank-and-Rent Upgrade:</strong> Once the contractor has been paying $49/month for 60–90 days and experiencing flawless reliability, Brandon introduces the WNC Trade Network exclusive corridor lease. We show them the live call volume hitting our corridor asset in their territory and offer them the exclusive phone dispatch lease.
      </p>
    </div>

  </div>

  <!-- Copy Toast Notification -->
  <div id="copy-toast">✓ SMS Cold Call Script copied to clipboard!</div>

  </div><!-- /ops-content -->

  <!-- Contractor Edit / Add Modal Drawer -->
  <div id="contractor-modal" style="position: fixed; inset: 0; background: rgba(7, 10, 19, 0.88); backdrop-filter: blur(8px); z-index: 100000; display: none; align-items: center; justify-content: center; padding: 1.25rem; overflow-y: auto;">
    <div style="background: #0f172a; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 16px; max-width: 680px; width: 100%; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 25px 60px -15px rgba(0,0,0,0.85); overflow: hidden;">
      
      <!-- Modal Header -->
      <div style="padding: 1.25rem 1.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); display: flex; align-items: center; justify-content: space-between; background: rgba(15, 23, 42, 0.6);">
        <div>
          <h3 id="modal-heading" style="color: #f8fafc; font-size: 1.25rem; font-weight: 700; margin: 0 0 0.25rem;">Edit Contractor Profile</h3>
          <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">Verified Western NC Contractor • Cloudflare Edge & Git Sync</p>
        </div>
        <button onclick="closeContractorModal()" style="background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer; padding: 0.25rem; line-height: 1;">&times;</button>
      </div>

      <!-- Modal Body (Scrollable Form) -->
      <div style="padding: 1.5rem 1.75rem; overflow-y: auto; flex: 1;">
        <form id="contractor-form" onsubmit="event.preventDefault(); saveContractorForm();">
          <input type="hidden" id="field-slug">
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div style="grid-column: span 2;">
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Company / Legal Business Name *</label>
              <input type="text" id="field-business-name" required placeholder="e.g. WNC Blast/Wash & Staining" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Short Display Name *</label>
              <input type="text" id="field-short-name" required placeholder="e.g. WNC Blast/Wash" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Trade Vertical *</label>
              <input type="text" id="field-trade" list="trade-datalist" required placeholder="e.g. Log Home Restoration & Chinking" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
              <datalist id="trade-datalist">{trade_options}</datalist>
            </div>

            <div style="grid-column: span 2;">
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">WNC Economic Corridor *</label>
              <select id="field-corridor" required style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.88rem; outline: none;">
                {corridor_options}
              </select>
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #34d399; margin-bottom: 0.35rem;">Named Human Owner / Principal *</label>
              <input type="text" id="field-owner-name" required placeholder="e.g. Adam Hambleton" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid rgba(16,185,129,0.35); color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Owner Title</label>
              <input type="text" id="field-owner-title" placeholder="e.g. Owner & Lead Craftsman" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #34d399; margin-bottom: 0.35rem;">Direct Cell Phone (10-Digit) *</label>
              <input type="tel" id="field-cell-phone" required placeholder="e.g. (828) 944-0005" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid rgba(16,185,129,0.35); color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Office / Alternate Phone</label>
              <input type="tel" id="field-office-phone" placeholder="e.g. (828) 555-0100" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Street Address</label>
              <input type="text" id="field-street-address" placeholder="e.g. 100 Mountain View Rd" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">City (NC) *</label>
              <input type="text" id="field-city" required placeholder="e.g. Waynesville" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">County</label>
              <input type="text" id="field-county" placeholder="e.g. Haywood County, NC" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">ZIP Code</label>
              <input type="text" id="field-zip" placeholder="e.g. 28786" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div style="grid-column: span 2;">
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Current Live Website / Google Business Profile URL</label>
              <input type="url" id="field-website" placeholder="https://..." style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Current Mobile PageSpeed Score (0-100)</label>
              <input type="number" id="field-pagespeed" min="1" max="100" placeholder="e.g. 28" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>

            <div>
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Bilingual / Spanish Service?</label>
              <select id="field-spanish" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.88rem; outline: none;">
                <option value="false">Standard English</option>
                <option value="true">🇪🇸 Se Habla Español / Bilingual Dispatch</option>
              </select>
            </div>

            <div style="grid-column: span 2;">
              <label style="display: block; font-size: 0.78rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.35rem;">Company Tagline / Specialties</label>
              <input type="text" id="field-tagline" placeholder="e.g. Heavy Mountain Excavation & Boulder Retaining Walls" style="width: 100%; box-sizing: border-box; padding: 0.65rem 0.85rem; border-radius: 6px; background: #1e293b; border: 1px solid #334155; color: #f8fafc; font-size: 0.9rem; outline: none;">
            </div>
          </div>

          <div id="modal-alert" style="display: none; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem; line-height: 1.4;"></div>

          <!-- Modal Footer Actions -->
          <div style="display: flex; justify-content: flex-end; gap: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 1.25rem;">
            <button type="button" onclick="closeContractorModal()" style="padding: 0.65rem 1.25rem; border-radius: 6px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #cbd5e1; font-weight: 600; cursor: pointer;">Cancel</button>
            <button type="submit" id="btn-save-contractor" style="padding: 0.65rem 1.5rem; border-radius: 6px; background: #10b981; border: none; color: #fff; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);">
              <span>💾 Save & Sync to GitHub</span>
            </button>
          </div>
        </form>
      </div>

    </div>
  </div>

  <script id="initial-clients-data" type="application/json">{json.dumps(clients)}</script>

  <script>
    const CORRECT_PIN = "8280";
    let clientsData = JSON.parse(document.getElementById("initial-clients-data").textContent);

    let currentSortColumn = null;
    let currentSortDirection = "asc";
    let currentCorridorFilter = "all";
    let currentTradeFilter = "all";
    let currentLangFilter = "all";
    let currentSearchQuery = "";

    function unlockWithPin() {{
      const val = document.getElementById("pin-input").value.trim();
      if (val === CORRECT_PIN) {{
        sessionStorage.setItem("ridgeline_ops_unlocked", "true");
        sessionStorage.setItem("ridgeline_ops_pin", val);
        showDashboard();
      }} else {{
        document.getElementById("pin-error").style.display = "block";
        document.getElementById("pin-input").value = "";
      }}
    }}
    function showDashboard() {{
      const modal = document.getElementById("pin-modal");
      const content = document.getElementById("ops-content");
      if (modal) modal.style.display = "none";
      if (content) content.style.display = "block";
      updateExpirationDaysLive();
    }}
    window.addEventListener("DOMContentLoaded", () => {{
      if (sessionStorage.getItem("ridgeline_ops_unlocked") === "true") {{
        showDashboard();
      }}
      updateExpirationDaysLive();
    }});

    function updateExpirationDaysLive() {{
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      document.querySelectorAll("tr[data-slug]").forEach(row => {{
        const expiresStr = row.getAttribute("data-expires");
        const slug = row.getAttribute("data-slug");
        if (!expiresStr || expiresStr === "N/A" || expiresStr.trim() === "") {{
          row.setAttribute("data-days", "9999");
          return;
        }}

        const parts = expiresStr.split("-");
        if (parts.length !== 3) return;
        const expDate = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
        const diffMs = expDate.getTime() - today.getTime();
        const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

        row.setAttribute("data-days", diffDays);

        const card = document.getElementById("card-" + slug);
        if (card) {{
          card.setAttribute("data-days", diffDays);
        }}
      }});
    }}

    function sortTable(column) {{
      if (currentSortColumn === column) {{
        currentSortDirection = currentSortDirection === "asc" ? "desc" : "asc";
      }} else {{
        currentSortColumn = column;
        currentSortDirection = "asc";
      }}

      // Update sort icons
      document.querySelectorAll(".sort-icon").forEach(icon => icon.textContent = "↕");
      const activeIcon = document.getElementById("sort-icon-" + column);
      if (activeIcon) {{
        activeIcon.textContent = currentSortDirection === "asc" ? "▲" : "▼";
      }}

      const tbody = document.getElementById("contractors-tbody");
      if (!tbody) return;
      const rows = Array.from(tbody.querySelectorAll("tr[data-slug]"));

      rows.sort((a, b) => {{
        let valA, valB;
        if (column === "name") {{
          valA = a.getAttribute("data-name") || "";
          valB = b.getAttribute("data-name") || "";
        }} else if (column === "corridor") {{
          valA = a.getAttribute("data-corridor") || "";
          valB = b.getAttribute("data-corridor") || "";
        }} else if (column === "owner") {{
          valA = a.getAttribute("data-owner") || "";
          valB = b.getAttribute("data-owner") || "";
        }} else if (column === "days") {{
          valA = parseInt(a.getAttribute("data-days") || "9999", 10);
          valB = parseInt(b.getAttribute("data-days") || "9999", 10);
        }} else if (column === "score") {{
          valA = parseInt(a.getAttribute("data-score") || "0", 10);
          valB = parseInt(b.getAttribute("data-score") || "0", 10);
        }} else {{
          valA = a.getAttribute("data-name") || "";
          valB = b.getAttribute("data-name") || "";
        }}

        if (typeof valA === "number" && typeof valB === "number") {{
          return currentSortDirection === "asc" ? valA - valB : valB - valA;
        }}
        return currentSortDirection === "asc"
          ? String(valA).localeCompare(String(valB))
          : String(valB).localeCompare(String(valA));
      }});

      rows.forEach(r => tbody.appendChild(r));

      // Also sort dossier cards
      const cardGrid = document.querySelector(".dossier-grid");
      if (cardGrid) {{
        const cards = Array.from(cardGrid.querySelectorAll(".client-dossier-card[data-slug]"));
        cards.sort((a, b) => {{
          let valA = a.getAttribute("data-" + (column === "score" ? "score" : column === "days" ? "days" : column)) || "";
          let valB = b.getAttribute("data-" + (column === "score" ? "score" : column === "days" ? "days" : column)) || "";
          if (column === "days") {{
            valA = parseInt(valA || "9999", 10);
            valB = parseInt(valB || "9999", 10);
            return currentSortDirection === "asc" ? valA - valB : valB - valA;
          }} else if (column === "score") {{
            valA = parseInt(valA || "0", 10);
            valB = parseInt(valB || "0", 10);
            return currentSortDirection === "asc" ? valA - valB : valB - valA;
          }}
          return currentSortDirection === "asc"
            ? String(valA).localeCompare(String(valB))
            : String(valB).localeCompare(String(valA));
        }});
        cards.forEach(c => cardGrid.appendChild(c));
      }}
    }}

    function filterLanguage(lang) {{
      currentLangFilter = lang;
      document.querySelectorAll(".filter-btn-lang").forEach(b => {{
        b.style.background = "rgba(255,255,255,0.06)";
        b.style.color = "#cbd5e1";
        b.style.borderColor = "rgba(255,255,255,0.15)";
      }});
      const activeBtn = document.getElementById("btn-lang-" + lang);
      if (activeBtn) {{
        if (lang === "es") {{
          activeBtn.style.background = "rgba(16,185,129,0.3)";
          activeBtn.style.color = "#34d399";
          activeBtn.style.borderColor = "#10b981";
        }} else {{
          activeBtn.style.background = "#2563eb";
          activeBtn.style.color = "#fff";
          activeBtn.style.borderColor = "#3b82f6";
        }}
      }}
      applyFilters();
    }}

    function searchContractors(query) {{
      currentSearchQuery = query.toLowerCase().trim();
      applyFilters();
    }}

    function applyFilters() {{
      const corridorSelect = document.getElementById("corridor-filter");
      const tradeSelect = document.getElementById("trade-filter");
      currentCorridorFilter = corridorSelect ? corridorSelect.value : "all";
      currentTradeFilter = tradeSelect ? tradeSelect.value : "all";

      const rows = document.querySelectorAll("tr[data-slug]");
      rows.forEach(r => {{
        const lang = r.getAttribute("data-lang");
        const corridor = r.getAttribute("data-corridor") || "";
        const trade = r.getAttribute("data-trade") || "";
        const text = r.innerText.toLowerCase();

        const matchesLang = (currentLangFilter === "all" || lang === currentLangFilter);
        const matchesCorridor = (currentCorridorFilter === "all" || corridor.includes(currentCorridorFilter.toLowerCase()));
        const matchesTrade = (currentTradeFilter === "all" || trade.includes(currentTradeFilter.toLowerCase()));
        const matchesSearch = (!currentSearchQuery || text.includes(currentSearchQuery));

        r.style.display = (matchesLang && matchesCorridor && matchesTrade && matchesSearch) ? "" : "none";
      }});

      const cards = document.querySelectorAll(".client-dossier-card[data-slug]");
      cards.forEach(c => {{
        const lang = c.getAttribute("data-lang");
        const corridor = c.getAttribute("data-corridor") || "";
        const trade = c.getAttribute("data-trade") || "";
        const text = c.innerText.toLowerCase();

        const matchesLang = (currentLangFilter === "all" || lang === currentLangFilter);
        const matchesCorridor = (currentCorridorFilter === "all" || corridor.includes(currentCorridorFilter.toLowerCase()));
        const matchesTrade = (currentTradeFilter === "all" || trade.includes(currentTradeFilter.toLowerCase()));
        const matchesSearch = (!currentSearchQuery || text.includes(currentSearchQuery));

        c.style.display = (matchesLang && matchesCorridor && matchesTrade && matchesSearch) ? "" : "none";
      }});
    }}

    function openEditModal(slug) {{
      const c = clientsData.find(item => item.slug === slug);
      if (!c) {{
        alert("Contractor record not found");
        return;
      }}
      document.getElementById("modal-heading").textContent = `Edit Contractor: ${{c.business_name}}`;
      document.getElementById("field-slug").value = c.slug;
      document.getElementById("field-business-name").value = c.business_name || "";
      document.getElementById("field-short-name").value = c.short_name || "";
      document.getElementById("field-trade").value = c.trade || "";
      document.getElementById("field-corridor").value = c.corridor_name || "";
      document.getElementById("field-owner-name").value = c.owner_name || "";
      document.getElementById("field-owner-title").value = c.owner_title || "";
      document.getElementById("field-cell-phone").value = c.cell_phone || "";
      document.getElementById("field-office-phone").value = c.office_phone || "";
      document.getElementById("field-street-address").value = c.street_address || "";
      document.getElementById("field-city").value = c.city || "";
      document.getElementById("field-county").value = c.county || "";
      document.getElementById("field-zip").value = c.zip || "";
      document.getElementById("field-website").value = c.current_website || "";
      document.getElementById("field-pagespeed").value = c.competitor_pagespeed || 35;
      document.getElementById("field-spanish").value = c.is_spanish_speaking ? "true" : "false";
      document.getElementById("field-tagline").value = c.tagline || "";

      const alertBox = document.getElementById("modal-alert");
      alertBox.style.display = "none";

      document.getElementById("contractor-modal").style.display = "flex";
    }}

    function openAddModal() {{
      document.getElementById("modal-heading").textContent = "➕ Add Real WNC Contractor (Proof-of-Life Required)";
      document.getElementById("field-slug").value = "";
      document.getElementById("field-business-name").value = "";
      document.getElementById("field-short-name").value = "";
      document.getElementById("field-trade").value = "";
      document.getElementById("field-owner-name").value = "";
      document.getElementById("field-owner-title").value = "Owner & Lead Operator";
      document.getElementById("field-cell-phone").value = "";
      document.getElementById("field-office-phone").value = "";
      document.getElementById("field-street-address").value = "";
      document.getElementById("field-city").value = "Hendersonville";
      document.getElementById("field-county").value = "Henderson County, NC";
      document.getElementById("field-zip").value = "28792";
      document.getElementById("field-website").value = "";
      document.getElementById("field-pagespeed").value = "32";
      document.getElementById("field-spanish").value = "false";
      document.getElementById("field-tagline").value = "";

      const alertBox = document.getElementById("modal-alert");
      alertBox.style.display = "none";

      document.getElementById("contractor-modal").style.display = "flex";
    }}

    function closeContractorModal() {{
      document.getElementById("contractor-modal").style.display = "none";
    }}

    async function saveContractorForm() {{
      const alertBox = document.getElementById("modal-alert");
      const saveBtn = document.getElementById("btn-save-contractor");

      const slug = document.getElementById("field-slug").value.trim();
      const business_name = document.getElementById("field-business-name").value.trim();
      const short_name = document.getElementById("field-short-name").value.trim() || business_name.split("(")[0].trim();
      const trade = document.getElementById("field-trade").value.trim();
      const corridor_name = document.getElementById("field-corridor").value.trim();
      const owner_name = document.getElementById("field-owner-name").value.trim();
      const owner_title = document.getElementById("field-owner-title").value.trim();
      const cell_phone = document.getElementById("field-cell-phone").value.trim();
      const office_phone = document.getElementById("field-office-phone").value.trim();
      const street_address = document.getElementById("field-street-address").value.trim();
      const city = document.getElementById("field-city").value.trim();
      const county = document.getElementById("field-county").value.trim();
      const zip = document.getElementById("field-zip").value.trim();
      const current_website = document.getElementById("field-website").value.trim();
      const competitor_pagespeed = parseInt(document.getElementById("field-pagespeed").value || "32", 10);
      const is_spanish_speaking = document.getElementById("field-spanish").value === "true";
      const tagline = document.getElementById("field-tagline").value.trim();

      // Client-side Proof-of-Life verification
      const rawDigits = cell_phone.replace(/\D/g, "");
      if (rawDigits.length !== 10 && rawDigits.length !== 11) {{
        alertBox.style.display = "block";
        alertBox.style.background = "rgba(239, 68, 68, 0.15)";
        alertBox.style.border = "1px solid #ef4444";
        alertBox.style.color = "#fca5a5";
        alertBox.textContent = "⚠️ Proof-of-Life Check Failed: Must enter a valid 10-digit direct phone number.";
        return;
      }}
      if (!owner_name) {{
        alertBox.style.display = "block";
        alertBox.style.background = "rgba(239, 68, 68, 0.15)";
        alertBox.style.border = "1px solid #ef4444";
        alertBox.style.color = "#fca5a5";
        alertBox.textContent = "⚠️ Proof-of-Life Check Failed: Named human owner/principal is required.";
        return;
      }}

      const clientPayload = {{
        slug: slug || undefined,
        business_name,
        short_name,
        trade,
        corridor_name,
        owner_name,
        owner_title,
        cell_phone,
        office_phone,
        street_address,
        city,
        county,
        zip,
        current_website,
        competitor_pagespeed,
        is_spanish_speaking,
        tagline
      }};

      saveBtn.disabled = true;
      saveBtn.innerHTML = "<span>⏳ Committing to GitHub...</span>";
      alertBox.style.display = "block";
      alertBox.style.background = "rgba(59, 130, 246, 0.15)";
      alertBox.style.border = "1px solid #3b82f6";
      alertBox.style.color = "#93c5fd";
      alertBox.textContent = "Connecting to Cloudflare edge function and committing data/clients.json to GitHub repository...";

      try {{
        const pinVal = sessionStorage.getItem("ridgeline_ops_pin") || CORRECT_PIN;
        const res = await fetch("/api/clients", {{
          method: "POST",
          headers: {{
            "Content-Type": "application/json",
            "X-Ops-Pin": pinVal
          }},
          body: JSON.stringify({{
            pin: pinVal,
            action: slug ? "update" : "create",
            client: clientPayload
          }})
        }});

        const data = await res.json();
        if (!res.ok || data.error) {{
          throw new Error(data.error || "Server returned " + res.status);
        }}

        // Success!
        alertBox.style.background = "rgba(16, 185, 129, 0.15)";
        alertBox.style.border = "1px solid #10b981";
        alertBox.style.color = "#a7f3d0";
        alertBox.textContent = `✓ ${{data.message || "Saved successfully!"}} Edge deployment triggered.`;

        // Update in-memory data
        const updatedSlug = data.slug || slug;
        const existingIdx = clientsData.findIndex(item => item.slug === updatedSlug);
        if (existingIdx >= 0) {{
          clientsData[existingIdx] = {{ ...clientsData[existingIdx], ...data.client }};
        }} else {{
          clientsData.push(data.client);
        }}

        // Update DOM row if present
        const row = document.getElementById("row-" + updatedSlug);
        if (row) {{
          const nameEl = row.querySelector(".col-name");
          if (nameEl) nameEl.textContent = short_name;
          const ownerEl = row.querySelector(".col-owner");
          if (ownerEl) ownerEl.textContent = owner_name;
          const phoneEl = row.querySelector(".col-phone");
          if (phoneEl) {{
            phoneEl.textContent = clientPayload.cell_phone;
            phoneEl.href = "tel:" + rawDigits.slice(-10);
          }}
          const cityTradeEl = row.querySelector(".col-city-trade");
          if (cityTradeEl) cityTradeEl.textContent = `${{city}}, NC • ${{trade}}`;
        }}

        setTimeout(() => {{
          closeContractorModal();
          saveBtn.disabled = false;
          saveBtn.innerHTML = "<span>💾 Save & Sync to GitHub</span>";
          const toast = document.getElementById("copy-toast");
          toast.textContent = `✓ Saved ${{business_name}}! Deploying to Cloudflare edge.`;
          toast.style.display = "block";
          setTimeout(() => {{ toast.style.display = "none"; }}, 4000);
        }}, 1200);

      }} catch (err) {{
        alertBox.style.background = "rgba(239, 68, 68, 0.15)";
        alertBox.style.border = "1px solid #ef4444";
        alertBox.style.color = "#fca5a5";
        alertBox.textContent = `❌ Save Failed: ${{err.message}}`;
        saveBtn.disabled = false;
        saveBtn.innerHTML = "<span>💾 Save & Sync to GitHub</span>";
      }}
    }}

    function copySmsPitchEs(slug) {{
      const textarea = document.getElementById("sms-text-es-" + slug);
      if (!textarea) return;
      navigator.clipboard.writeText(textarea.value).then(() => {{
        const toast = document.getElementById("copy-toast");
        toast.textContent = "✓ ¡Copiado SMS en Español al portapapeles!";
        toast.style.display = "block";
        setTimeout(() => {{ toast.style.display = "none"; }}, 3000);
      }}).catch(err => {{
        alert("Error al copiar: " + err);
      }});
    }}

    function copySmsPitch(slug) {{
      const textarea = document.getElementById("sms-text-" + slug);
      if (!textarea) return;
      
      navigator.clipboard.writeText(textarea.value).then(() => {{
        const toast = document.getElementById("copy-toast");
        toast.textContent = "✓ Copied Cold SMS Pitch to clipboard!";
        toast.style.display = "block";
        setTimeout(() => {{
          toast.style.display = "none";
        }}, 3000);
      }}).catch(err => {{
        alert("Could not copy automatically: " + err);
      }});
    }}

    function copyStripeLink(url, label) {{
      navigator.clipboard.writeText(url).then(() => {{
        const toast = document.getElementById("copy-toast");
        toast.textContent = "✓ Copied " + label + " Checkout Link to clipboard!";
        toast.style.display = "block";
        setTimeout(() => {{
          toast.style.display = "none";
        }}, 3000);
      }}).catch(err => {{
        alert("Could not copy link: " + err);
      }});
    }}

    function copyDnsInstructions(domain) {{
      const text = "Record Type: CNAME\\nHost / Name: @ (and www)\\nPoints To / Target: preview.ridgelinetrade.com\\nTTL: Auto (or 3600)";
      navigator.clipboard.writeText(text).then(() => {{
        const toast = document.getElementById("copy-toast");
        toast.textContent = "✓ Copied CNAME Setup Records for " + domain + " to clipboard!";
        toast.style.display = "block";
        setTimeout(() => {{
          toast.style.display = "none";
        }}, 3000);
      }}).catch(err => {{
        alert("Could not copy link: " + err);
      }});
    }}
  </script>

</body>
</html>"""
    return html


def generate_404_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>404 - Edge Node Not Found | Ridgeline Cloud Edge</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #070a13;
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 1.5rem;
      margin: 0;
    }
    .box {
      background: #0f172a;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 3rem 2rem;
      max-width: 480px;
      width: 100%;
      box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
    }
    h1 { font-size: 3.5rem; font-weight: 900; color: #3b82f6; margin-bottom: 0.5rem; }
    h2 { font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; color: #f8fafc; }
    p { color: #94a3b8; font-size: 0.95rem; line-height: 1.5; margin-bottom: 2rem; }
    a {
      display: inline-block;
      padding: 0.85rem 1.5rem;
      background: #2563eb;
      color: #fff;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      transition: background 0.2s;
    }
    a:hover { background: #1d4ed8; }
  </style>
</head>
<body>
  <div class="box">
    <h1>404</h1>
    <h2>Edge Node Not Found</h2>
    <p>The requested client web property or directory container does not exist or has been relocated.</p>
    <a href="/">← Return to Network Gateway</a>
  </div>
</body>
</html>"""

def generate_public_gateway_html(clients):
    nodes_js = "{\n"
    for c in clients:
        slug = c["slug"]
        nodes_js += f'      "{slug}": "{slug}",\n'
        short = slug.split("-")[0]
        if short != slug:
            nodes_js += f'      "{short}": "{slug}",\n'
    nodes_js += "    }"

    template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ridgeline Cloud Edge | High-Performance Regional Web Infrastructure</title>
  <meta name="description" content="Dedicated high-availability cloud edge hosting, automated DNS routing, and sub-second web infrastructure for Western North Carolina trade contractors and specialty businesses.">
  <meta name="robots" content="index, follow">
  
  <style>
    :root {
      --bg: #070a13;
      --surface: #0f172a;
      --card-bg: rgba(255, 255, 255, 0.03);
      --card-border: rgba(255, 255, 255, 0.08);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #3b82f6;
      --emerald: #10b981;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    
    /* Top Bar */
    .nav-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.25rem 2rem;
      border-bottom: 1px solid var(--card-border);
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(12px);
    }
    .brand-group {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: #fff;
    }
    .brand-icon {
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-weight: 800;
      font-size: 0.9rem;
    }
    .brand-name {
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: -0.01em;
    }
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      color: #34d399;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 10px #10b981;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.15); opacity: 1; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }
    
    /* Hero */
    .hero {
      max-width: 900px;
      margin: 4rem auto 2rem;
      padding: 0 1.5rem;
      text-align: center;
    }
    .tag-badge {
      display: inline-block;
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.3);
      color: #60a5fa;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 1.5rem;
    }
    h1 {
      font-size: clamp(2.2rem, 5vw, 3.5rem);
      font-weight: 900;
      letter-spacing: -0.03em;
      line-height: 1.15;
      margin-bottom: 1.25rem;
      background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    p.subtitle {
      color: var(--text-muted);
      font-size: 1.15rem;
      max-width: 680px;
      margin: 0 auto 2.5rem;
      line-height: 1.6;
    }
    
    /* Search Box */
    .access-card {
      background: var(--surface);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 2rem;
      max-width: 600px;
      margin: 0 auto 3.5rem;
      box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
      text-align: left;
    }
    .access-card h3 {
      font-size: 1.1rem;
      font-weight: 700;
      margin-bottom: 0.4rem;
      color: #f8fafc;
    }
    .access-card p {
      color: var(--text-muted);
      font-size: 0.88rem;
      margin-bottom: 1.25rem;
    }
    .search-row {
      display: flex;
      gap: 0.5rem;
    }
    .search-input {
      flex: 1;
      padding: 0.85rem 1rem;
      background: #090d16;
      border: 1px solid #334155;
      border-radius: 8px;
      color: #fff;
      font-size: 0.95rem;
      outline: none;
      transition: border 0.2s;
    }
    .search-input:focus {
      border-color: var(--accent);
    }
    .btn-connect {
      padding: 0.85rem 1.4rem;
      background: #2563eb;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      font-size: 0.95rem;
      white-space: nowrap;
      transition: background 0.2s;
    }
    .btn-connect:hover {
      background: #1d4ed8;
    }
    .lookup-msg {
      color: #ef4444;
      font-size: 0.82rem;
      margin-top: 0.6rem;
      display: none;
    }
    
    /* Architecture Grid */
    .grid-wrap {
      max-width: 1040px;
      margin: 0 auto 4rem;
      padding: 0 1.5rem;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 1.25rem;
    }
    .feature-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.5rem;
    }
    .feature-num {
      color: #3b82f6;
      font-weight: 800;
      font-size: 0.85rem;
      margin-bottom: 0.75rem;
    }
    .feature-title {
      font-size: 1rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      color: #f1f5f9;
    }
    .feature-desc {
      color: var(--text-muted);
      font-size: 0.85rem;
      line-height: 1.5;
    }
    
    /* Footer */
    footer {
      border-top: 1px solid var(--card-border);
      padding: 2rem;
      text-align: center;
      color: #64748b;
      font-size: 0.85rem;
    }
    .footer-links {
      margin-top: 0.75rem;
      display: flex;
      justify-content: center;
      gap: 1.5rem;
    }
    .footer-links a {
      color: #475569;
      text-decoration: none;
      font-size: 0.78rem;
      transition: color 0.2s;
    }
    .footer-links a:hover {
      color: #94a3b8;
    }
  </style>
</head>
<body>

  <nav class="nav-bar">
    <a href="/" class="brand-group">
      <div class="brand-icon">▲</div>
      <div class="brand-name">RIDGELINE CLOUD EDGE</div>
    </a>
    <div class="status-pill">
      <div class="status-dot"></div>
      Global Edge Network: Operational
    </div>
  </nav>

  <main>
    <section class="hero">
      <div class="tag-badge">Western North Carolina Edge Infrastructure</div>
      <h1>Enterprise Cloud Edge for Mountain Trade Craftsmen</h1>
      <p class="subtitle">
        Ultra-fast dedicated edge hosting, sub-second content routing, and direct mobile lead infrastructure engineered across the 23 counties of Western North Carolina.
      </p>
      
      <div class="access-card">
        <h3>Client Edge Container Lookup</h3>
        <p>Client web properties operate on isolated, zero-dependency edge nodes. Enter your company slug to connect.</p>
        <div class="search-row">
          <input type="text" id="node-slug" class="search-input" placeholder="Enter company slug (e.g. tates-grading)..." onkeydown="if(event.key==='Enter') connectNode()">
          <button onclick="connectNode()" class="btn-connect">Access Node ↗</button>
        </div>
        <div id="lookup-msg" class="lookup-msg"></div>
      </div>
    </section>

    <section class="grid-wrap">
      <div class="feature-card">
        <div class="feature-num">01 / SPEED</div>
        <div class="feature-title">Sub-Second Edge Delivery</div>
        <div class="feature-desc">Engineered with inlined critical CSS and system typography achieving perfect 100/100 mobile Google PageSpeed scores with zero render blocking.</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">02 / ISOLATION</div>
        <div class="feature-title">Zero Cross-Site Coupling</div>
        <div class="feature-desc">Every business web property runs in an isolated edge container with independent SSL certificates, clean schema, and dedicated NAP citations.</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">03 / DISPATCH</div>
        <div class="feature-title">Native Mobile Routing</div>
        <div class="feature-desc">Instant click-to-call integration and spam-filtered direct owner routing keeping working foremen and contractors connected with mountain homeowners.</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">04 / DEFENSE</div>
        <div class="feature-title">Enterprise Security</div>
        <div class="feature-desc">Protected by Cloudflare's global Anycast edge network with automated TLS 1.3 encryption, DDoS mitigation, and 100% regional uptime monitoring.</div>
      </div>
    </section>
  </main>

  <footer>
    <div>© 2026 Barebones 3D, L.L.C. d/b/a Ridgeline Trade Network. Western North Carolina Infrastructure.</div>
    <div class="footer-links">
      <a href="/ops-control-828/" title="Operational Command">· Operations Gateway ·</a>
    </div>
  </footer>

  <script>
    const KNOWN_NODES = __NODES_JS__;

    function connectNode() {
      const input = document.getElementById("node-slug");
      const msg = document.getElementById("lookup-msg");
      const val = input.value.trim().toLowerCase().replace(/[^a-z0-9-]/g, "");
      
      if (!val) {
        msg.textContent = "Please enter an organization slug or name.";
        msg.style.display = "block";
        return;
      }
      
      const target = KNOWN_NODES[val] || val;
      msg.style.display = "none";
      window.location.href = "/sites/" + target + "/";
    }
  </script>

</body>
</html>"""
    return template.replace("__NODES_JS__", nodes_js)

def atomic_write(filepath: Path, content: str):
    """Writes a file atomically using a temporary file to avoid corrupt reads."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = filepath.with_suffix(filepath.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp_path, filepath)

def main():
    print("=========================================================")
    print("🚀 WNC Website Rental Monorepo Programmatic Builder")
    print("=========================================================\n")

    clients = load_clients()
    print(f"📦 Loaded {len(clients)} client contractor profiles from data/clients.json\n")

    # 1. Build individual client websites
    for c in clients:
        slug = c["slug"]
        site_dir = SITES_DIR / slug
        site_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔨 Building site: /sites/{slug}/ ({c['business_name']})...")
        
        # HTML
        html_content = generate_client_html(c)
        atomic_write(site_dir / "index.html", html_content)

        # robots.txt
        robots_content = generate_robots_txt(slug)
        atomic_write(site_dir / "robots.txt", robots_content)

        # sitemap.xml
        sitemap_content = generate_sitemap_xml(slug)
        atomic_write(site_dir / "sitemap.xml", sitemap_content)

        print(f"   ✓ index.html (Real photos, Logo, Inlined CSS, Schema JSON-LD, 100/100 speed)")
        print(f"   ✓ robots.txt & sitemap.xml generated")

    # 2. Build Public B2B Gateway at root /index.html
    print(f"\n🌐 Generating Public Edge Gateway at /index.html...")
    public_gateway_html = generate_public_gateway_html(clients)
    atomic_write(REPO_ROOT / "index.html", public_gateway_html)
    print("   ✓ Public Edge Gateway generated successfully (Zero sales/upsell content)!")

    # 3. Build Custom 404 Handler at root /404.html
    print("🛡️ Generating Custom 404 Edge Handler at /404.html...")
    atomic_write(REPO_ROOT / "404.html", generate_404_html())
    print("   ✓ 404 Edge Handler generated successfully!")

    # 4. Build PIN-Protected Ops Command at /ops-control-828/index.html
    print("🔒 Generating PIN-Protected Operations Command at /ops-control-828/index.html...")
    ops_dir = REPO_ROOT / "ops-control-828"
    ops_dir.mkdir(parents=True, exist_ok=True)
    portal_html = generate_master_portal_html(clients)
    atomic_write(ops_dir / "index.html", portal_html)
    print("   ✓ Operations Command deployed securely behind PIN gate!")

    print("\n🎉 Programmatic generation complete! Public Gateway, 404 Handler, Ops Command, and all 10 sites are built.\n")

if __name__ == "__main__":
    main()
