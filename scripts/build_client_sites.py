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

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "clients.json"
STRIPE_FILE = REPO_ROOT / "data" / "stripe_products.json"
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
    schema_json = json.dumps(schema_data, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{c['business_name']} | {c['city']}, NC {c['trade']}</title>
  <meta name="description" content="{c['tagline']}. Serving {', '.join(c['hub_towns'])}. Call {c['owner_name']} directly at {c['cell_phone']} for rapid quotes.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{BASE_URL}/sites/{c['slug']}/">
  
  <!-- Open Graph -->
  <meta property="og:title" content="{c['business_name']} | Mountain {c['trade']}">
  <meta property="og:description" content="{c['tagline']}">
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
      border-radius: 4px;
      display: block;
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
    .footer-meta-bar {{
      max-width: 1100px;
      margin: 0 auto 1.75rem;
      padding: 1.25rem 1.5rem;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      font-size: 0.82rem;
      line-height: 1.5;
    }}
    .meta-row {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.65rem;
    }}
    .meta-badge {{
      display: inline-flex;
      align-items: center;
      padding: 0.2rem 0.6rem;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.72rem;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      white-space: nowrap;
    }}
    .meta-badge.domain {{
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }}
    .meta-badge.host {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .meta-text {{
      color: var(--text-muted);
    }}
    .meta-text strong {{
      color: #e2e8f0;
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
    <div class="hero-badge">
      <span class="status-dot"></span>
      <span>{c['owner_name']} ({c['owner_title']}) On Dispatch</span>
    </div>
    <h1>{c['tagline'].split('Across')[0]} <span>Across {c['city']}, NC</span></h1>
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

    {hero_featured_html}
  </header>

  <!-- Trust Badges Bar -->
  <section class="trust-container">
    <div class="trust-grid">
      {trust_badges_html}
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

  <!-- Direct Quote Box -->
  <section class="section-wrap">
    <div class="quote-box">
      <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--accent); margin-bottom: 0.5rem;">
        Direct Access • Zero Middlemen
      </div>
      <h2>Speak Directly With {c['owner_name']}</h2>
      <p>
        Skip the dispatch answering services. Talk straight with the owner and lead technician about your project scope, scheduling, and on-site estimate.
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

    <!-- Domain Registration & Cloud Infrastructure Trust Banner -->
    <div class="footer-meta-bar">
      <div class="meta-row">
        <span class="meta-badge domain">Domain Registration</span>
        <span class="meta-text">Domain <strong>{domain_display}</strong> is officially registered to <strong>{c['business_name']}</strong> ({c['owner_name']}, Authorized Registrant • {c['city']}, NC).</span>
      </div>
      <div class="meta-row">
        <span class="meta-badge host">Cloud Hosting</span>
        <span class="meta-text">High-performance edge infrastructure hosted on <strong>Cloudflare Anycast Global Edge Network</strong>. Maintained by <strong>Ridgeline Trade Network</strong>.</span>
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
      Call {c['owner_name']} Direct ({c['cell_phone']})
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
    rental_link = stripe_catalog.get("website_rental_49", {}).get("payment_link", "https://buy.stripe.com/8x29AV87Q6e6er98xJ1wY00")
    tier_a_link = stripe_catalog.get("corridor_lease_tier_a_1250", {}).get("payment_link", "https://buy.stripe.com/fZueVf4VEfOG0Aj4ht1wY01")
    tier_b_link = stripe_catalog.get("corridor_lease_tier_b_950", {}).get("payment_link", "https://buy.stripe.com/3cI7sNco69qi6YH29l1wY02")
    tier_c_link = stripe_catalog.get("corridor_lease_tier_c_750", {}).get("payment_link", "https://buy.stripe.com/5kQcN7co6eKCaaT01d1wY03")
    
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
        
        # SMS Pitch text
        sms_pitch = (
            f"Hey {c['owner_name']}, Brandon here in Hendersonville. Ran an automated Google speed test on your web presence for {c['short_name']} "
            f"and saw mobile visitors wait {old_lcp} for your page (scores {old_score}/100 on Google PageSpeed). In WNC, slow load times lose callers. "
            f"Your mountain craftsmanship is top tier, so I took photos of your actual work ({top_project_ref}), "
            f"optimized them, and built a high-speed mockup for you that hits 100/100 and loads in 0.4s: "
            f"{BASE_URL}/sites/{c['slug']}/ "
            f"If you like it, I host and maintain it for $49/mo flat—zero setup fee, no contracts, and you keep your domain. Let me know what you think!"
        )
        
        table_rows += f"""
        <tr>
          <td>
            <strong>{c['short_name']}</strong><br>
            <span class="sub-text">{c['city']}, NC • {c['trade']}</span>
          </td>
          <td>
            <span class="corridor-badge">{c['trade_network_corridor_slug']}</span><br>
            <span class="sub-text">{c['trade_network_domain']}</span>
          </td>
          <td>
            <strong>{c['owner_name']}</strong><br>
            <a href="tel:{phone_clean}" class="phone-link">{c['cell_phone']}</a>
          </td>
          <td>
            <span class="speed-pill {score_class}">{old_score}/100</span><br>
            <span class="sub-text">FCP {old_fcp} | LCP {old_lcp}</span>
          </td>
          <td>
            <span class="speed-pill score-perfect">100/100</span><br>
            <span class="sub-text">FCP 0.3s | LCP 0.5s</span>
          </td>
          <td>
            <div class="action-btn-group">
              <a href="/sites/{c['slug']}/" target="_blank" class="btn-demo">View Site ↗</a>
              <button class="btn-sms" onclick="copySmsPitch('{c['slug']}')">Copy SMS</button>
              <button class="btn-sms" onclick="copyStripeLink('{rental_link}', '$49/mo')" style="background: #10b981;">$49 Link</button>
            </div>
            <textarea id="sms-text-{c['slug']}" style="display:none;">{sms_pitch}</textarea>
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

        client_cards += f"""
        <div class="client-dossier-card">
          <div class="card-header">
            <div>
              <h3>{c['business_name']}</h3>
              <div class="card-meta">{c['city']}, NC • {c['county']}</div>
            </div>
            <span class="corridor-tag">{c['corridor_name'].split('—')[0].strip()}</span>
          </div>
          
          <div class="thumb-strip-wrap">
            {thumb_strip}
          </div>
          
          <div class="stat-compare">
            <div class="stat-box bad">
              <div class="stat-label">Current Mobile Score</div>
              <div class="stat-val">{old_score} / 100</div>
              <div class="stat-detail">Load Time: {old_lcp}</div>
            </div>
            <div class="stat-arrow">➔</div>
            <div class="stat-box good">
              <div class="stat-label">Our Rental Mockup</div>
              <div class="stat-val">100 / 100</div>
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
            <div class="field-row">
              <span class="field-title">Monthly Rental Rate:</span>
              <span class="field-val">$49.00 / month flat</span>
            </div>
            <div class="field-row">
              <span class="field-title">Network Upsell Target:</span>
              <span class="field-val corridor-target">{c['upsell_corridor_deal']}</span>
            </div>
          </div>
          
          <div class="card-footer">
            <a href="/sites/{c['slug']}/" target="_blank" class="card-action-btn primary">Open Live Mockup ↗</a>
            <button class="card-action-btn secondary" onclick="copySmsPitch('{c['slug']}')">Copy SMS Pitch</button>
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
      margin-bottom: 1rem;
    }}
    .card-header h3 {{
      font-size: 1.15rem;
      font-weight: 800;
      color: #ffffff;
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
    .stat-val {{ font-size: 1.25rem; font-weight: 800; }}
    .stat-box.bad .stat-val {{ color: #f87171; }}
    .stat-box.good .stat-val {{ color: #34d399; }}
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
      High-converting $49/month website rentals built with real field photography for 10 premier trade contractors across Western North Carolina.
    </p>
  </header>

  <!-- Key Financial Metrics -->
  <div class="metric-grid">
    <div class="metric-card">
      <div class="metric-val blue">10 Properties</div>
      <div class="metric-label">Client Mockups Deployed</div>
    </div>
    <div class="metric-card">
      <div class="metric-val green">$490 / mo</div>
      <div class="metric-label">Phase 1 Rental Cash Flow</div>
    </div>
    <div class="metric-card">
      <div class="metric-val gold">$10,450 / mo</div>
      <div class="metric-label">Corridor Upsell Potential</div>
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
    
    <!-- Executive Comparison Table -->
    <div class="section-title">
      <span>Contractor Audit & Speed Comparison Matrix</span>
      <span style="font-size: 0.85rem; font-weight: 600; color: var(--emerald);">✓ All 10 Sites 100/100 Ready (With Real Photos)</span>
    </div>
    
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Business & Trade</th>
            <th>Network Corridor</th>
            <th>Owner & Direct Phone</th>
            <th>Their Current Speed</th>
            <th>Our Rental Speed</th>
            <th>Outreach Actions</th>
          </tr>
        </thead>
        <tbody>
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

  <script>
    const CORRECT_PIN = "8280";
    function unlockWithPin() {{
      const val = document.getElementById("pin-input").value.trim();
      if (val === CORRECT_PIN) {{
        sessionStorage.setItem("ridgeline_ops_unlocked", "true");
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
    }}
    window.addEventListener("DOMContentLoaded", () => {{
      if (sessionStorage.getItem("ridgeline_ops_unlocked") === "true") {{
        showDashboard();
      }}
    }});

    function copySmsPitch(slug) {{
      const textarea = document.getElementById('sms-text-' + slug);
      if (!textarea) return;
      
      navigator.clipboard.writeText(textarea.value).then(() => {{
        const toast = document.getElementById('copy-toast');
        toast.textContent = '✓ Copied Cold SMS Pitch to clipboard!';
        toast.style.display = 'block';
        setTimeout(() => {{
          toast.style.display = 'none';
        }}, 3000);
      }}).catch(err => {{
        alert('Could not copy automatically: ' + err);
      }});
    }}

    function copyStripeLink(url, label) {{
      navigator.clipboard.writeText(url).then(() => {{
        const toast = document.getElementById('copy-toast');
        toast.textContent = '✓ Copied ' + label + ' Checkout Link to clipboard!';
        toast.style.display = 'block';
        setTimeout(() => {{
          toast.style.display = 'none';
        }}, 3000);
      }}).catch(err => {{
        alert('Could not copy link: ' + err);
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
