import sys
import html
import numpy as np
from PIL import Image
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
import config
import prep_photo

def image_to_ascii_grid(img_path: Path, width: int = 100, aspect_ratio: float = 0.48):
    """Converts a grayscale prepped image into a grid of ASCII characters."""
    if not img_path.exists():
        print(f"[make_ascii_svg] {img_path} not found. Running prep_photo first...")
        prep_photo.process_photo(config.SOURCE_PHOTO_PATH, img_path)

    img = Image.open(img_path).convert("L")
    orig_w, orig_h = img.size

    # Calculate height preserving aspect ratio with font factor
    height = int((orig_h / orig_w) * width * aspect_ratio)
    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    arr = np.array(resized)

    ramp = config.ASCII_RAMP
    ramp_len = len(ramp)

    ascii_rows = []
    for row in arr:
        line_chars = []
        for pixel in row:
            # Map 0 (dark) -> high index (dense char), 255 (bright) -> 0 (space)
            # Invert so 255 is space (' ') and 0 is '@'
            idx = int((255 - pixel) / 256.0 * ramp_len)
            idx = min(max(idx, 0), ramp_len - 1)
            line_chars.append(ramp[idx])
        ascii_rows.append("".join(line_chars))

    return ascii_rows, width, height

def generate_ascii_svg(ascii_rows, cols, rows, output_path: Path):
    """Generates a self-typing animated SVG from ASCII rows."""
    font_size = 11
    char_width = 6.6
    line_height = 13
    padding_x = 20
    padding_y = 25

    svg_w = int(cols * char_width + padding_x * 2)
    svg_h = int(rows * line_height + padding_y * 2)

    # Animation parameters
    total_anim_duration = 3.5  # total seconds for whole portrait typing
    row_duration = total_anim_duration / rows

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">',
        '  <defs>',
        '    <style>',
        '      @import url("https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&amp;display=swap");',
        '      .bg { fill: #0d1117; rx: 8px; ry: 8px; stroke: #30363d; stroke-width: 1.5; }',
        '      .ascii-text { font-family: "Fira Code", Consolas, "Cascadia Code", monospace; font-size: 11px; fill: #8b949e; letter-spacing: 0px; white-space: pre; }',
        '      .title-bar { fill: #161b22; }',
        '      .dot-red { fill: #ff5f56; }',
        '      .dot-yellow { fill: #ffbd2e; }',
        '      .dot-green { fill: #27c93f; }',
        '      .header-title { font-family: "Fira Code", monospace; font-size: 11px; fill: #7d8590; font-weight: 600; }',
        '    </style>',
    ]

    # Clip paths for row-by-row horizontal wipe animation
    for i in range(rows):
        start_time = i * row_duration
        svg_lines.append(
            f'    <clipPath id="row-clip-{i}">'
            f'<rect x="{padding_x}" y="{padding_y + i * line_height - 2}" width="0" height="{line_height + 2}">'
            f'<animate attributeName="width" from="0" to="{svg_w - padding_x * 2}" begin="{start_time:.3f}s" dur="{row_duration:.3f}s" fill="freeze" calcMode="linear"/>'
            f'</rect></clipPath>'
        )

    svg_lines.extend([
        '  </defs>',
        f'  <rect width="{svg_w}" height="{svg_h}" class="bg"/>',
        # Header bar
        f'  <path d="M 0 8 Q 0 0 8 0 L {svg_w-8} 0 Q {svg_w} 0 {svg_w} 8 L {svg_w} 28 L 0 28 Z" class="title-bar"/>',
        f'  <line x1="0" y1="28" x2="{svg_w}" y2="28" stroke="#30363d" stroke-width="1"/>',
        '  <circle cx="16" cy="14" r="4.5" class="dot-red"/>',
        '  <circle cx="29" cy="14" r="4.5" class="dot-yellow"/>',
        '  <circle cx="42" cy="14" r="4.5" class="dot-green"/>',
        f'  <text x="{svg_w/2}" y="17" text-anchor="middle" class="header-title">portrait.ascii</text>',
        '  <g class="ascii-text">',
    ])

    # Add text rows with row clip paths
    for i, line in enumerate(ascii_rows):
        y_pos = padding_y + 15 + i * line_height
        escaped_line = html.escape(line)
        svg_lines.append(
            f'    <text x="{padding_x}" y="{y_pos}" clip-path="url(#row-clip-{i})">{escaped_line}</text>'
        )

    # Add typing cursor animation block attached to the active typing row
    svg_lines.append(
        f'    <rect width="7" height="12" fill="#58a6ff" opacity="0.85">'
        f'<animate attributeName="x" from="{padding_x}" to="{svg_w - padding_x * 1.5}" begin="0s" dur="{total_anim_duration:.3f}s" fill="freeze"/>'
        f'<animate attributeName="y" from="{padding_y + 4}" to="{padding_y + (rows-1) * line_height + 4}" begin="0s" dur="{total_anim_duration:.3f}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="0.95;0;0.95" dur="0.6s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    svg_lines.extend([
        '  </g>',
        '</svg>'
    ])

    output_path.write_text("\n".join(svg_lines), encoding="utf-8")
    print(f"[make_ascii_svg] Generated {output_path} ({svg_w}x{svg_h}px, {rows} rows)")

if __name__ == "__main__":
    rows, cols_cnt, rows_cnt = image_to_ascii_grid(
        config.PREPPED_PHOTO_PATH, width=config.ASCII_WIDTH, aspect_ratio=config.CHARACTER_ASPECT_RATIO
    )
    generate_ascii_svg(rows, cols_cnt, rows_cnt, config.ASCII_SVG_PATH)
