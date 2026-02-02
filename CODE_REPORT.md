# Smart City Satellite Image Generation Pipeline - Code Report

## Project Overview

This project implements an **AI-powered urban planning visualization system** that combines **ControlNet** and **Stable Diffusion** to analyze satellite imagery and generate smart city visualizations. The system performs evidence-based urban analysis from segmentation masks and uses generative AI purely for visualization purposes.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Satellite Image (.png)     +     Segmentation Mask (.png)          │
│  (Aerial photograph)              (Color-coded land use classes)    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ANALYSIS LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│  1. Coverage Computation (compute_coverage.py)                      │
│  2. Spatial Metrics Analysis                                        │
│  3. Urban Layout Analysis                                           │
│  4. Issue Detection & Planning Suggestions                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GENERATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  ControlNet + Stable Diffusion Inpainting Pipeline                  │
│  - Preserves immutable regions (Roads, Rivers, Forests)             │
│  - Regenerates editable regions (Residential, Unused, Agricultural) │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│  Generated Smart City Image  +  Urban Analysis Report (.md)         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Coverage Computation Module (`compute_coverage.py`)

**Purpose:** Calculates the percentage area coverage for each land use class from segmentation masks.

**Key Features:**

- Supports both BGR color masks (3-channel) and single-channel label masks
- Uses OpenCV for image loading and processing
- Computes pixel-by-pixel classification

**Land Use Classes Recognized:**

| Label ID | Class Name        | BGR Color     |
| -------- | ----------------- | ------------- |
| 1        | Residential Area  | (128, 0, 0)   |
| 2        | Road              | (0, 128, 0)   |
| 3        | River             | (0, 0, 128)   |
| 4        | Forest            | (0, 128, 128) |
| 5        | Unused Land       | (128, 128, 0) |
| 6        | Agricultural Area | (128, 0, 128) |

**Algorithm:**

```
For each pixel in mask:
    Match pixel color to predefined class color
    Increment class pixel count
Calculate: coverage_percent = (class_pixels / total_pixels) × 100
```

---

### 2. Satellite Image Generation Module (`generate_satellite_image.py`)

This is the main pipeline module containing multiple sub-components:

#### 2.1 Spatial Analysis Functions

**`compute_connected_components(binary_mask)`**

- Uses 8-connectivity to identify distinct regions
- Employs SciPy's `ndimage.label()` function
- Returns labeled array and component count

**`compute_spatial_metrics(seg_mask, class_colors)`**

- Computes comprehensive spatial metrics including:
  - Per-class pixel counts and coverage percentages
  - Number of connected components per class
  - Component size statistics (average, median, largest, smallest)
  - Compactness ratio (largest_component / total_class_area)
  - Fragmentation index for key classes
  - Adjacency relationships between classes

#### 2.2 Urban Layout Analysis

**`analyze_urban_layout(coverage, spatial_metrics)`**

Performs evidence-based urban analysis with the following assessments:

**Derived Indicators Computed:**

- Green space percentage (Forest + Agricultural)
- Built area percentage (Residential + Road)
- Open space percentage (Unused + Forest + Agricultural + River)
- Development intensity ratio
- Green-to-residential ratio

**Density Assessment:**
| Residential Coverage | Classification |
|---------------------|----------------|
| ≥ 50% | High |
| 30% - 50% | Medium |
| < 30% | Low |

**Issue Detection Categories:**

1. **Density Constraint** - High residential coverage with limited unused land
2. **Green Space Deficit** - Low green-to-residential ratio (< 0.5)
3. **Ventilation Constraint** - High compactness with no fragmentation opportunity
4. **Infrastructure Gap** - Low road coverage relative to residential density

#### 2.3 Suggestion Generation

**`generate_suggestions(analysis)`**

Generates evidence-linked planning recommendations:

**Constraints (Immutable Classes):**

- Roads - Must preserve circulation patterns
- Rivers - Cannot modify hydrological features
- Forests - Ecological services protection

**Interventions:**

- Micro-open spaces for density constraints
- Green integration for green space deficits
- Internal courtyards for ventilation issues
- Mixed-use development for unused land opportunities

#### 2.4 Report Generation

**`create_report(image_path, mask_path, analysis, suggestions)`**

Generates comprehensive technical assessment reports including:

- Data summary and image properties
- Area coverage breakdown
- Computed spatial indicators
- Density and open space assessments
- Identified issues with severity ratings
- Recommended interventions
- Generation constraints and editable regions

---

### 3. Image Generation Pipeline

**Technology Stack:**

- **Stable Diffusion** - Base generative model
- **ControlNet** - Structure-guided generation using Canny edge detection
- **Inpainting Pipeline** - Selective region regeneration

**Region Handling:**

| Class Type    | Classes                                          | Behavior                           |
| ------------- | ------------------------------------------------ | ---------------------------------- |
| **Editable**  | Residential Area, Unused Land, Agricultural Area | Regenerated as smart city elements |
| **Immutable** | Road, River, Forest                              | Preserved exactly via compositing  |

**Pipeline Flow:**

1. Load satellite image and segmentation mask
2. Compute coverage and spatial metrics
3. Analyze urban layout and detect issues
4. Generate planning suggestions
5. Create inpainting mask (editable regions = white)
6. Apply ControlNet with Canny edge detection
7. Run Stable Diffusion inpainting with smart city prompt
8. Composite immutable regions back onto generated image
9. Output final visualization and analysis report

---

## Key Algorithms

### Fragmentation Index Calculation

```
fragmentation_index = 1 - (largest_component_area / total_class_area)
```

- **0** = Completely contiguous (single block)
- **1** = Highly fragmented (many small pieces)

### Adjacency Detection

```
1. Create binary mask for residential areas
2. Dilate mask by 2 pixels to find boundary region
3. Compute boundary = dilated_mask - original_mask
4. Check overlap between boundary and other class masks
5. Classify adjacency strength: Strong (>1000px), Moderate (>200px), Weak
```

### Compactness Classification

| Compactness Ratio | Classification |
| ----------------- | -------------- |
| ≥ 0.8             | High           |
| 0.5 - 0.8         | Medium         |
| < 0.5             | Low            |

---

## Dependencies

### Core Libraries

| Library      | Purpose                                            |
| ------------ | -------------------------------------------------- |
| PyTorch      | Deep learning framework with CUDA support          |
| Diffusers    | Pre-trained Stable Diffusion and ControlNet models |
| Transformers | Hugging Face transformers for text encoding        |
| OpenCV       | Image loading and processing                       |
| NumPy        | Numerical computations                             |
| SciPy        | Connected component analysis                       |
| PIL/Pillow   | Image manipulation                                 |

### Model Weights

- **Stable Diffusion v1.5** - Base generation model
- **ControlNet Canny** - Edge-guided structure control
- Optional: Custom aerial/satellite LoRA weights

---

## Usage Modes

### 1. Single Image Generation

```bash
python src/generate_satellite_image.py \
  --image dataset/images/output_337.png \
  --mask dataset/masks/output_337.png \
  --output output/generated_smart_city.png
```

### 2. Batch Processing

```bash
python src/generate_satellite_image.py --batch
```

### 3. Low VRAM Mode (4GB GPUs)

```bash
python src/generate_satellite_image.py --low_vram
```

### 4. Coverage Analysis Only

```bash
python src/compute_coverage.py dataset/masks/output_337.png
```

---

## Output Artifacts

1. **Generated Image** - Smart city visualization preserving original structure
2. **Urban Analysis Report** (Markdown) - Comprehensive technical assessment
3. **Console Output** - Progress updates and summary statistics

---

## Design Philosophy

> **"Diffusion is NOT the decision-maker."**

The system is designed with a clear separation of concerns:

- **Analysis Phase** - All urban metrics, issues, and suggestions are computed BEFORE image generation
- **Generation Phase** - ControlNet + Stable Diffusion serves purely as a visualization tool
- **Evidence-Based** - Every conclusion is tied to computed spatial indicators

This ensures reproducibility and allows the analytical findings to stand independently of the generative output.

---

## File Structure Summary

```
src/
├── generate_satellite_image.py   # Main pipeline (1939 lines)
│   ├── Spatial analysis functions
│   ├── Urban layout analysis
│   ├── Suggestion generation
│   ├── Report generation
│   └── Image generation pipeline
│
└── compute_coverage.py           # Coverage computation (138 lines)
    └── Per-class area percentage calculation
```

---

## Technical Notes

- **Image Format:** All masks use BGR color convention (OpenCV standard)
- **Connectivity:** 8-connectivity used for connected component analysis
- **Adjacency Detection:** 2-pixel dilation boundary detection
- **CUDA Acceleration:** Full GPU support for inference
- **Memory Optimization:** Sequential attention and model CPU offload available

---

_Report generated for academic/project documentation purposes._
