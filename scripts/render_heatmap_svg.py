import json
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
import config

def render_heatmap(json_path: Path, output_path: Path):
    """Renders data/contributions.json into an animated SVG heatmap graph."""
    if not json_path.exists():
        print(f"[render_heatmap_svg] {json_path} not found. Running fetch_contributions...")
        import fetch_contributions
        fetch_contributions.main()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    days = data.get("days", [])

    svg_w = 860
    svg_h = 215

    is_static = os.getenv("STATIC") == "1"

    # Layout constants
    offset_x = 45
    offset_y = 52
    cell_size = 11
    cell_gap = 3
    stride = cell_size + cell_gap  # 14px step

    # Color palette mapping (0 to 5)
    palette = config.HEATMAP_PALETTE

    # Animation CSS
    anim_css = """
      @keyframes boxDiagonalSlide {
        0% { opacity: 0; transform: translateY(-8px) scale(0.85); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
      }
      .anim-box {
        animation: boxDiagonalSlide 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        transform-origin: center;
      }
    """ if not is_static else ".anim-box { opacity: 1; }"

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">',
        '  <defs>',
        '    <style>',
        '      @import url("https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&amp;display=swap");',
        f'      {anim_css}',
        '      .bg { fill: #0d1117; rx: 8px; ry: 8px; stroke: #30363d; stroke-width: 1.5; }',
        '      .title-bar { fill: #161b22; }',
        '      .dot-red { fill: #ff5f56; }',
        '      .dot-yellow { fill: #ffbd2e; }',
        '      .dot-green { fill: #27c93f; }',
        '      .header-title { font-family: "Fira Code", monospace; font-size: 11px; fill: #7d8590; font-weight: 600; }',
        '      .label-month { font-family: "Fira Code", monospace; font-size: 10px; fill: #7d8590; font-weight: 500; }',
        '      .label-day { font-family: "Fira Code", monospace; font-size: 10px; fill: #7d8590; font-weight: 500; }',
        '      .meta-stats { font-family: "Fira Code", monospace; font-size: 11px; fill: #c9d1d9; font-weight: 500; }',
        '      .meta-highlight { fill: #39d353; font-weight: 600; }',
        '      .legend-text { font-family: "Fira Code", monospace; font-size: 10px; fill: #7d8590; }',
        '    </style>',
        '  </defs>',
        f'  <rect width="{svg_w}" height="{svg_h}" class="bg"/>',
        # Header bar
        f'  <path d="M 0 8 Q 0 0 8 0 L {svg_w-8} 0 Q {svg_w} 0 {svg_w} 8 L {svg_w} 28 L 0 28 Z" class="title-bar"/>',
        f'  <line x1="0" y1="28" x2="{svg_w}" y2="28" stroke="#30363d" stroke-width="1"/>',
        '  <circle cx="16" cy="14" r="4.5" class="dot-red"/>',
        '  <circle cx="29" cy="14" r="4.5" class="dot-yellow"/>',
        '  <circle cx="42" cy="14" r="4.5" class="dot-green"/>',
        f'  <text x="{svg_w/2}" y="17" text-anchor="middle" class="header-title">contributions.sh --year</text>',
    ]

    # Weekday Labels (Mon, Wed, Fri)
    weekday_labels = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    for w_name, w_row in weekday_labels:
        wy = offset_y + w_row * stride + 9
        svg_lines.append(f'  <text x="20" y="{wy}" class="label-day">{w_name}</text>')

    # Group days into 53 weeks x 7 days
    # Parse dates and map to week index
    week_cols = [[] for _ in range(53)]
    month_headers = []

    last_month = None

    if days:
        first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
        for d in days:
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
            delta_days = (dt - first_date).days
            col_idx = delta_days // 7
            row_idx = delta_days % 7

            if col_idx < 53:
                week_cols[col_idx].append((row_idx, d))

                # Month label tracking
                m_name = dt.strftime("%b")
                if m_name != last_month and col_idx < 50:
                    month_headers.append((col_idx, m_name))
                    last_month = m_name

    # Render Month Headers
    for col_idx, m_name in month_headers:
        mx = offset_x + col_idx * stride
        svg_lines.append(f'  <text x="{mx}" y="{offset_y - 8}" class="label-month">{m_name}</text>')

    # Render Heatmap Grid with Diagonal Staggered Animation
    svg_lines.append('  <g>')
    for col_idx in range(53):
        col_days = week_cols[col_idx]
        for row_idx, d_info in col_days:
            x = offset_x + col_idx * stride
            y = offset_y + row_idx * stride
            lvl = d_info["level"]
            lvl = min(max(lvl, 0), len(palette) - 1)
            fill_color = palette[lvl]

            # Diagonal animation delay formula
            delay = (col_idx + row_idx) * 0.015

            anim_attr = f' class="anim-box" style="animation-delay: {delay:.3f}s;"' if not is_static else ''

            svg_lines.append(
                f'    <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{fill_color}"{anim_attr}>'
                f'<title>{d_info["count"]} contributions on {d_info["date"]}</title>'
                f'</rect>'
            )
    svg_lines.append('  </g>')

    # Footer Statistics Bar
    total_cnt = data.get("total_contributions", 0)
    streak_cnt = data.get("current_streak", 0)

    footer_y = offset_y + 7 * stride + 22

    svg_lines.extend([
        f'  <g transform="translate({offset_x}, {footer_y})">',
        f'    <text x="0" y="0" class="meta-stats">'
        f'<tspan class="meta-highlight">{total_cnt:,}</tspan> contributions in the last year  •  '
        f'streak: <tspan class="meta-highlight">{streak_cnt}</tspan> days'
        f'</text>',
        '  </g>',
        # Legend (Less -> More)
        f'  <g transform="translate({svg_w - 180}, {footer_y - 10})">',
        '    <text x="0" y="9" class="legend-text">Less</text>',
    ])

    for i, color in enumerate(palette):
        lx = 32 + i * 14
        svg_lines.append(f'    <rect x="{lx}" y="0" width="10" height="10" rx="2" ry="2" fill="{color}"/>')

    svg_lines.extend([
        '    <text x="120" y="9" class="legend-text">More</text>',
        '  </g>',
        '</svg>'
    ])

    output_path.write_text("\n".join(svg_lines), encoding="utf-8")
    print(f"[render_heatmap_svg] Generated {output_path} ({svg_w}x{svg_h}px)")

if __name__ == "__main__":
    render_heatmap(config.CONTRIBUTIONS_JSON_PATH, config.HEATMAP_SVG_PATH)
