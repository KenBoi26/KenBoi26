import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
import config

def generate_portfolio_banner_svg(portfolio_url: str, output_path: Path):
    """Generates a vibrant, poppy, magazine-style animated portfolio banner SVG."""
    width = 860
    height = 140

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      @import url("https://fonts.googleapis.com/css2?family=Outfit:wght@600;800;900&amp;family=Plus+Jakarta+Sans:wght@500;700&amp;display=swap");

      @keyframes glossSweep {{
        0% {{ transform: translateX(-100%) rotate(25deg); }}
        100% {{ transform: translateX(200%) rotate(25deg); }}
      }}

      @keyframes floatBadge {{
        0%, 100% {{ transform: translateY(0px) rotate(-2deg); }}
        50% {{ transform: translateY(-5px) rotate(1deg); }}
      }}

      @keyframes pulseGlow {{
        0%, 100% {{ filter: drop-shadow(0 0 8px rgba(255, 0, 128, 0.6)); }}
        50% {{ filter: drop-shadow(0 0 18px rgba(0, 242, 254, 0.9)); }}
      }}

      .banner-bg {{
        rx: 16px; ry: 16px;
        fill: url(#popGrad);
        stroke: rgba(255, 255, 255, 0.25);
        stroke-width: 2;
      }}

      .gloss-line {{
        fill: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
        animation: glossSweep 4.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
      }}

      .mag-tag {{
        font-family: "Outfit", sans-serif;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        fill: #ffd166;
        text-transform: uppercase;
      }}

      .mag-title {{
        font-family: "Outfit", sans-serif;
        font-size: 26px;
        font-weight: 900;
        fill: #ffffff;
        letter-spacing: -0.5px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
      }}

      .mag-sub {{
        font-family: "Plus Jakarta Sans", sans-serif;
        font-size: 13px;
        font-weight: 600;
        fill: rgba(255, 255, 255, 0.9);
      }}

      .action-pill {{
        animation: floatBadge 3s ease-in-out infinite, pulseGlow 2.5s ease-in-out infinite;
        cursor: pointer;
      }}

      .btn-bg {{
        fill: #ffffff;
        rx: 24px; ry: 24px;
        filter: drop-shadow(0 4px 12px rgba(0,0,0,0.25));
      }}

      .btn-text {{
        font-family: "Outfit", sans-serif;
        font-size: 13px;
        font-weight: 800;
        fill: #111827;
        letter-spacing: 0.5px;
      }}

      .sparkle {{
        font-size: 16px;
      }}
    </style>

    <linearGradient id="popGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ff007a"/>
      <stop offset="50%" stop-color="#7928ca"/>
      <stop offset="100%" stop-color="#00f2fe"/>
    </linearGradient>

    <clipPath id="bannerClip">
      <rect width="{width}" height="{height}" rx="16" ry="16"/>
    </clipPath>
  </defs>

  <a xlink:href="{portfolio_url}" target="_blank" style="text-decoration: none;">
    <g clip-path="url(#bannerClip)">
      <!-- Main Pop Gradient Background -->
      <rect width="{width}" height="{height}" class="banner-bg"/>

      <!-- Animated Shimmer Gloss Bar -->
      <rect x="-100" y="-50" width="150" height="250" fill="url(#glossGrad)" opacity="0.3" class="gloss-line"/>

      <!-- Decorative Pop Stickers & Stars -->
      <circle cx="50" cy="25" r="3" fill="#ffffff" opacity="0.6"/>
      <circle cx="120" cy="115" r="4" fill="#ffd166" opacity="0.8"/>
      <circle cx="480" cy="20" r="3" fill="#ffffff" opacity="0.7"/>
      <circle cx="820" cy="120" r="5" fill="#00f2fe" opacity="0.8"/>

      <!-- Left Column: Magazine Headline -->
      <g transform="translate(35, 38)">
        <text x="0" y="0" class="mag-tag">✦ KENNETH'S DIGITAL PLAYGROUND  •  ISSUE #01 ✦</text>
        <text x="0" y="32" class="mag-title">Welcome to My Creative Universe ✨</text>
        <text x="0" y="56" class="mag-sub">Projects, Music, Code &amp; Visual Design  •  Tap to Explore Live 🚀</text>
      </g>

      <!-- Right Column: Animated Floating CTA Button -->
      <g transform="translate(630, 44)" class="action-pill">
        <rect width="195" height="48" class="btn-bg"/>
        <text x="97" y="29" text-anchor="middle" class="btn-text">EXPLORE PORTFOLIO ➔</text>
      </g>
    </g>
  </a>
</svg>"""

    output_path.write_text(svg_content, encoding="utf-8")
    print(f"[make_portfolio_banner] Generated magazine banner SVG {output_path} ({width}x{height}px)")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/KenBoi26"
    generate_portfolio_banner_svg(url, config.BASE_DIR / "portfolio-banner.svg")
