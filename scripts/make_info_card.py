import os
import sys
import html
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
import config

def generate_info_card_svg(output_path: Path):
    """Hand-authors a Neofetch-style SVG info card with clean layout and staggered animations."""
    is_static = os.getenv("STATIC") == "1"

    data = config.INFO_CARD_DATA
    width = 490
    height = 674  # Matches ASCII portrait height for side-by-side alignment

    # Key / Value pairs to display
    lines = [
        ("OS", data["os"], "#79c0ff"),
        ("Host", data["host"], "#79c0ff"),
        ("Focus", data["uptime"], "#7ee787"),
        ("Shell", data["shell"], "#7ee787"),
        ("---", "--------------------------------------", "#30363d"),
        ("Learning", data["now"], "#ffa657"),
        ("Languages", "C++, Java, Python, HTML/CSS, SQL", "#d2a8ff"),
        ("Skills", "DSA, OOP, System Design, Git", "#79c0ff"),
        ("Interests", data["highlights"], "#ff7b72"),
    ]

    # Staggered animation CSS - opacity only or relative Y offset
    anim_css = """
      @keyframes fadeInSlide {
        0% { opacity: 0; transform: translateY(8px); }
        100% { opacity: 1; transform: translateY(0px); }
      }
      .anim-line {
        animation: fadeInSlide 0.5s ease-out forwards;
        opacity: 0;
      }
    """ if not is_static else ".anim-line { opacity: 1; }"

    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '  <defs>',
        '    <style>',
        '      @import url("https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&amp;display=swap");',
        f'      {anim_css}',
        '      .card-bg { fill: #0d1117; rx: 8px; ry: 8px; stroke: #30363d; stroke-width: 1.5; }',
        '      .title-bar { fill: #161b22; }',
        '      .dot-red { fill: #ff5f56; }',
        '      .dot-yellow { fill: #ffbd2e; }',
        '      .dot-green { fill: #27c93f; }',
        '      .header-title { font-family: "Fira Code", monospace; font-size: 11px; fill: #7d8590; font-weight: 600; }',
        '      .user-host { font-family: "Fira Code", monospace; font-size: 15px; font-weight: 700; fill: #58a6ff; }',
        '      .sep-line { font-family: "Fira Code", monospace; font-size: 12px; fill: #30363d; }',
        '      .label { font-family: "Fira Code", monospace; font-size: 12px; font-weight: 600; fill: #8b949e; }',
        '      .val-text { font-family: "Fira Code", monospace; font-size: 12px; font-weight: 400; }',
        '      .palette-box { width: 16px; height: 16px; rx: 3px; ry: 3px; }',
        '    </style>',
        '  </defs>',
        f'  <rect width="{width}" height="{height}" class="card-bg"/>',
        # Window Header Bar
        f'  <path d="M 0 8 Q 0 0 8 0 L {width-8} 0 Q {width} 0 {width} 8 L {width} 28 L 0 28 Z" class="title-bar"/>',
        f'  <line x1="0" y1="28" x2="{width}" y2="28" stroke="#30363d" stroke-width="1"/>',
        '  <circle cx="16" cy="14" r="4.5" class="dot-red"/>',
        '  <circle cx="29" cy="14" r="4.5" class="dot-yellow"/>',
        '  <circle cx="42" cy="14" r="4.5" class="dot-green"/>',
        f'  <text x="{width/2}" y="17" text-anchor="middle" class="header-title">neofetch --card</text>',
        '  <g transform="translate(28, 42)">',
    ]

    # User@Host Header Row
    delay = 0.1
    svg_content.append(
        f'    <g class="anim-line" style="animation-delay: {delay:.2f}s;">'
        f'      <text x="0" y="22" class="user-host">{html.escape(data["title"])}</text>'
        f'    </g>'
    )

    # Separator Line
    delay += 0.1
    svg_content.append(
        f'    <g class="anim-line" style="animation-delay: {delay:.2f}s;">'
        f'      <text x="0" y="40" class="sep-line">--------------------------------------------</text>'
        f'    </g>'
    )

    y_offset = 68
    for key, val, color in lines:
        delay += 0.08
        if key == "---":
            svg_content.append(
                f'    <g class="anim-line" style="animation-delay: {delay:.2f}s;">'
                f'      <text x="0" y="{y_offset}" class="sep-line">{val}</text>'
                f'    </g>'
            )
            y_offset += 24
        else:
            escaped_key = html.escape(key)
            escaped_val = html.escape(val)

            # Check for multi-line / word wrap if string is long
            if len(escaped_val) > 36:
                words = escaped_val.split(", ")
                mid = len(words) // 2
                val_line1 = ", ".join(words[:mid]) + ","
                val_line2 = ", ".join(words[mid:])

                svg_content.append(
                    f'    <g class="anim-line" style="animation-delay: {delay:.2f}s;">'
                    f'      <text x="0" y="{y_offset}" class="label">{escaped_key:<10}:</text>'
                    f'      <text x="100" y="{y_offset}" class="val-text" fill="{color}">{val_line1}</text>'
                    f'      <text x="100" y="{y_offset + 18}" class="val-text" fill="{color}">{val_line2}</text>'
                    f'    </g>'
                )
                y_offset += 42
            else:
                svg_content.append(
                    f'    <g class="anim-line" style="animation-delay: {delay:.2f}s;">'
                    f'      <text x="0" y="{y_offset}" class="label">{escaped_key:<10}:</text>'
                    f'      <text x="100" y="{y_offset}" class="val-text" fill="{color}">{escaped_val}</text>'
                    f'    </g>'
                )
                y_offset += 32

    # Terminal Palette Blocks wrapped in outer transform <g> so CSS transform does NOT overwrite SVG translate!
    delay += 0.15
    palette_colors = ["#161b22", "#ff7b72", "#7ee787", "#ffa657", "#79c0ff", "#d2a8ff", "#a5d6ff", "#f0f6fc"]
    palette_svg = []
    for idx, pcolor in enumerate(palette_colors):
        px = idx * 22
        palette_svg.append(f'<rect x="{px}" y="0" class="palette-box" fill="{pcolor}"/>')

    palette_y = y_offset + 25
    svg_content.append(
        f'    <g transform="translate(0, {palette_y})">'
        f'      <g class="anim-line" style="animation-delay: {delay:.2f}s;">'
        f'        {"".join(palette_svg)}'
        f'      </g>'
        f'    </g>'
    )

    svg_content.extend([
        '  </g>',
        '</svg>'
    ])

    output_path.write_text("\n".join(svg_content), encoding="utf-8")
    print(f"[make_info_card] Generated {output_path} ({width}x{height}px)")

if __name__ == "__main__":
    generate_info_card_svg(config.INFO_CARD_SVG_PATH)
