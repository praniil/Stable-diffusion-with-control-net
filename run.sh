#!/bin/bash
# Run Smart City Satellite Image Generation Pipeline
#
# Usage:
#   ./run.sh                           # Single run with defaults
#   ./run.sh --image X --mask Y        # Custom image/mask
#   ./run.sh --batch                   # Process all pairs in dataset/
#   ./run.sh --analysis_only           # Analysis only, skip generation
#
# Examples:
#   ./run.sh --image dataset/images/output_179.png --mask dataset/masks/output_179.png
#   ./run.sh --batch --low_vram
#   ./run.sh --sharpen --denoise
#   ./run.sh --size 768 --steps 50

set -e
cd "$(dirname "$0")"

# Activate virtual environment
if [[ -d "venv" ]]; then
    source venv/bin/activate
else
    echo "Error: venv not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Run from project root; defaults use dataset/images and dataset/masks
mkdir -p output

python3 src/generate_satellite_image.py \
    --image "${IMAGE:-../dataset/images/output_337.png}" \
    --mask "${MASK:-../dataset/masks/output_337.png}" \
    --output "${OUTPUT:-../output/smart_city_generated.png}" \
    "$@"
