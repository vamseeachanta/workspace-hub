# Engineering Animation Pipeline

Manim-based animated explainers for GTM demos, README collateral, and client outreach.

## Quick Start

```bash
# --- Catenary Riser Explainer ---
# Render (low quality, fast preview)
mamba run -n manim-env manim -ql --media_dir scripts/animations/media \
  scripts/animations/scenes/catenary_riser.py CatenaryRiserExplainer

# Render at 720p (production quality)
mamba run -n manim-env manim -qm --media_dir scripts/animations/media \
  scripts/animations/scenes/catenary_riser.py CatenaryRiserExplainer

# Render static thumbnail
mamba run -n manim-env manim -ql --media_dir scripts/animations/media -s \
  scripts/animations/scenes/catenary_riser.py CatenaryRiserThumbnail

# Create GIF from MP4 (for README / GitHub embedding)
ffmpeg -y -i scripts/animations/media/videos/catenary_riser/480p15/CatenaryRiserExplainer.mp4 \
  -vf "fps=10,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
  scripts/animations/media/catenary_riser_explainer.gif

# --- Mooring Layout Explainer ---
# Render (low quality, fast preview)
mamba run -n manim-env manim -ql --media_dir scripts/animations/media \
  scripts/animations/scenes/mooring_layout.py MooringLayoutExplainer

# Render at 720p (production quality)
mamba run -n manim-env manim -qm --media_dir scripts/animations/media \
  scripts/animations/scenes/mooring_layout.py MooringLayoutExplainer

# Render static thumbnail
mamba run -n manim-env manim -ql --media_dir scripts/animations/media -s \
  scripts/animations/scenes/mooring_layout.py MooringLayoutThumbnail

# Create GIF
ffmpeg -y -i scripts/animations/media/videos/mooring_layout/480p15/MooringLayoutExplainer.mp4 \
  -vf "fps=10,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
  scripts/animations/media/mooring_layout_explainer.gif
```

## Directory Layout

```
scripts/animations/
├── README.md                  # this file
├── __init__.py
├── catenary_math.py           # reusable catenary riser calculations
├── mooring_math.py            # mooring layout geometry + force calcs
├── scenes/
│   ├── catenary_riser.py      # SCR geometry + fatigue explainer
│   ├── mooring_layout.py      # spread mooring force + excursion explainer
│   └── template.py            # copy-and-customize template
├── data/
│   └── mooring_config.yaml    # representative 8-line spread mooring fixture
└── media/                     # rendered outputs (gitignored except GIFs)
    ├── videos/                # MP4 renders at various qualities
    ├── images/                # static thumbnails (PNG)
    └── *.gif                  # optimised GIFs for web embedding
```

## Creating a New Animation

1. Copy `scenes/template.py` to `scenes/your_scenario.py`
2. Implement the five `_build_*` / `_animate_*` methods
3. Use helpers from template: `make_callout_box()`, `make_depth_environment()`
4. Put engineering math in a separate module (like `catenary_math.py`)
5. Render and iterate

## Four-Phase Scene Structure

Every engineering explainer follows the same story arc:

| Phase | Duration | Content |
|-------|----------|---------|
| 1. Setup | ~2s | Physical environment — seabed, water, vessel |
| 2. Static | ~4s | Engineering geometry with labels and specs |
| 3. Dynamic | ~12s | Parameter sweep — offset, load, wave height |
| 4. Results | ~5s | Assessment callout — utilisation, fatigue, pass/fail |

## Environment Setup

```bash
# One-time: create the Manim conda environment
mamba create -n manim-env -y python=3.12 manim -c conda-forge
```

Requires: ffmpeg (system), conda/mamba. LaTeX optional (for MathTex).

## Candidate Future Animations

| Priority | Scenario | Data Source | Issue |
|----------|----------|-------------|-------|
| Done | Catenary riser geometry + fatigue | fatigue-scr-touchdown.yaml | #2035 |
| Done | Mooring layout / force explainer | mooring_config.yaml + mooring-failures knowledge | #2037, #2043 |
| Next | Installation sequence / operability | vessel data (#1798, #1799) | #2038 |
| Later | Wall thickness code comparison | Demo 2 data | — |
| Later | VIV response / fatigue coupling | Demo 1 data | — |

## GTM Integration

- **GIF outputs** feed #1809 (demo screencasts) and README embedding
- **MP4 outputs** feed #2022 (aceengineer.com content) and LinkedIn posts
- **Thumbnails** feed #2016 (client conversion pipeline) collateral
- All outputs compatible with #1809 recording guidelines (< 5 MB, 1024x768)
