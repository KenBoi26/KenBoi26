import os
from pathlib import Path

# Repository / Account Settings
USERNAME = os.getenv("GITHUB_USERNAME", "KenBoi26")

# Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"

# File Paths
SOURCE_PHOTO_PATH = BASE_DIR / "source-photo.jpg"
PREPPED_PHOTO_PATH = BASE_DIR / "source-prepped.png"
ASCII_SVG_PATH = BASE_DIR / "avi-ascii.svg"
INFO_CARD_SVG_PATH = BASE_DIR / "info-card.svg"
CONTRIBUTIONS_JSON_PATH = DATA_DIR / "contributions.json"
HEATMAP_SVG_PATH = BASE_DIR / "contrib-heatmap.svg"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ASCII Art Settings
ASCII_RAMP = " .`:-=+*cs#%@"
ASCII_WIDTH = 100
ASCII_HEIGHT = 53
CHARACTER_ASPECT_RATIO = 0.48  # Font width / height ratio for monospace

# Neofetch Info Card Metadata
INFO_CARD_DATA = {
    "title": "kenneth@github",
    "os": "Arch Linux x86_64 / Windows",
    "host": "Software Developer (India)",
    "uptime": "DSA & Problem Solving",
    "shell": "zsh 5.9 (x86_64-pc-linux-gnu)",
    "now": "Improving DSA Concepts (C++, Java, Py)",
    "prev": "Fullstack & Systems Exploration",
    "stack": "C++, Java, Python, HTML/CSS, Git",
    "highlights": "Guitarist 🎸, Runner 🏃‍♂️, Rubik's Solver 🧩",
}

# Heatmap Palette (GitHub Dark Mode standard green ramp)
HEATMAP_PALETTE = [
    "#161b22",  # Level 0 (None)
    "#0e4429",  # Level 1
    "#006d32",  # Level 2
    "#26a641",  # Level 3
    "#39d353",  # Level 4
    "#69f0a0"   # Level 5 (Top vibrant neon)
]
