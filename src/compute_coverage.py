"""
Compute per-class percentage area coverage from satellite image annotation masks.
Uses BGR format (OpenCV convention) to match generate_satellite_image.py.
Supports both color masks (3ch BGR) and single-channel label masks (1ch).

Usage:
    1. Set DEFAULT_MASK_PATH below and run: python compute_coverage.py
    2. Or pass image path as argument: python compute_coverage.py <mask_image_path>
    3. Or import and call: from compute_coverage import compute_coverage

Example:
    python compute_coverage.py ../dataset/Annotation/annotated_masks/output_117.png
"""

import numpy as np
import cv2
import argparse
import sys
import os


# ============================================================
# SET YOUR MASK IMAGE PATH HERE (change this as needed)
# ============================================================
DEFAULT_MASK_PATH = "../dataset/images/output_338.png"
# ============================================================


# BGR color mapping (matches generate_satellite_image.py)
BGR_TO_CLASS = {
    (128, 0, 0): "Residential Area",   # label 1
    (0, 128, 0): "Road",               # label 2
    (0, 0, 128): "River",              # label 3
    (0, 128, 128): "Forest",           # label 4
    (128, 128, 0): "Unused Land",      # label 5
    (128, 0, 128): "Agricultural Area",  # label 6
}

LABEL_TO_CLASS = {
    1: "Residential Area",
    2: "Road",
    3: "River",
    4: "Forest",
    5: "Unused Land",
    6: "Agricultural Area",
}

CLASS_NAMES = list(LABEL_TO_CLASS.values())


def compute_coverage(mask_path: str) -> dict:
    """
    Compute per-class coverage percentage for an annotation mask.
    Loads mask in BGR format (cv2) for consistency with generate_satellite_image.
    Supports color masks (3ch) and label masks (1ch).

    Args:
        mask_path: Path to the annotation mask (PNG)

    Returns:
        Dictionary with class names and their coverage percentages
    """
    mask = cv2.imread(str(mask_path))
    if mask is None:
        raise FileNotFoundError(f"Could not load mask: {mask_path}")

    h, w = mask.shape[:2]
    total_pixels = h * w
    coverage = {name: 0.0 for name in CLASS_NAMES}

    if len(mask.shape) == 2:
        # Single-channel label mask
        for label_id, class_name in LABEL_TO_CLASS.items():
            pixel_count = np.sum(mask == label_id)
            coverage[class_name] = round((pixel_count / total_pixels) * 100, 2)
    else:
        # Color mask (BGR)
        pixels_flat = mask.reshape(-1, 3)
        unique_colors = np.unique(pixels_flat, axis=0)
        for color in unique_colors:
            color_tuple = tuple(int(c) for c in color)
            if color_tuple in BGR_TO_CLASS:
                class_name = BGR_TO_CLASS[color_tuple]
                matches = np.all(pixels_flat == color, axis=1)
                pixel_count = np.sum(matches)
                coverage[class_name] = round((pixel_count / total_pixels) * 100, 2)

    return coverage


def main():
    parser = argparse.ArgumentParser(
        description="Compute per-class percentage area coverage from annotation mask"
    )
    parser.add_argument(
        "mask_path",
        type=str,
        nargs="?",
        default=DEFAULT_MASK_PATH,
        help="Path to the annotation mask image (PNG). If not provided, uses DEFAULT_MASK_PATH."
    )
    
    args = parser.parse_args()
    
    # Resolve relative path from script directory if needed
    mask_path = args.mask_path
    if not os.path.isabs(mask_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mask_path = os.path.join(script_dir, mask_path)
    
    try:
        coverage = compute_coverage(mask_path)
        
        print("\n" + "=" * 50)
        print("  AREA COVERAGE (%)")
        print("=" * 50)
        
        # Sort by percentage descending
        sorted_items = sorted(coverage.items(), key=lambda x: -x[1])
        
        for class_name, percentage in sorted_items:
            bar_length = int(percentage / 2)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"  {class_name:<20s}: {percentage:6.2f}% |{bar[:25]}|")
        
        print("=" * 50 + "\n")
        
    except FileNotFoundError:
        print(f"Error: File not found: {args.mask_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
