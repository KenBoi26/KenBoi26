import sys
import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

# Add scripts directory to path for config import
sys.path.append(str(Path(__file__).parent))
import config

def remove_background_rembg(pil_img: Image.Image) -> Image.Image:
    """Attempts to remove background using rembg library."""
    try:
        from rembg import remove
        return remove(pil_img)
    except Exception as e:
        print(f"[prep_photo] rembg background removal skipped or failed ({e}), using luminance threshold fallback.")
        return None

def fallback_background_removal(cv_img: np.ndarray) -> np.ndarray:
    """Fallback background isolation using OpenCV thresholding and mask."""
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    # Threshold dark background vs foreground subject
    _, mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    # Smooth mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask

def process_photo(input_path: Path, output_path: Path):
    """Preps photo with CLAHE contrast enhancement and white background composition."""
    if not input_path.exists():
        print(f"Error: Input photo not found at {input_path}")
        sys.exit(1)

    print(f"[prep_photo] Processing {input_path} -> {output_path}...")

    # Load PIL image
    pil_img = Image.open(input_path).convert("RGBA")

    # Step 1: Remove background
    rembg_res = remove_background_rembg(pil_img)

    if rembg_res is not None:
        rgba = np.array(rembg_res)
    else:
        cv_bgr = cv2.imread(str(input_path))
        mask = fallback_background_removal(cv_bgr)
        rgba = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2BGRA)
        rgba[:, :, 3] = mask

    # Separate RGB and Alpha
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3] / 255.0

    # Step 2: Convert RGB to Grayscale
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Step 3: Apply CLAHE (Contrast-Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # Step 4: Composite onto pure white background for non-subject areas
    # Alpha = 1 -> keep enhanced_gray, Alpha = 0 -> 255 (white)
    white_bg = np.ones_like(enhanced_gray) * 255
    final_gray = (enhanced_gray * alpha + white_bg * (1.0 - alpha)).astype(np.uint8)

    # Save result
    res_img = Image.fromarray(final_gray)
    res_img.save(output_path, "PNG")
    print(f"[prep_photo] Prepped photo saved successfully to {output_path}")

if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else config.SOURCE_PHOTO_PATH
    out = config.PREPPED_PHOTO_PATH
    process_photo(src, out)
