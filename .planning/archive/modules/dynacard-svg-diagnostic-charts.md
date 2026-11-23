---
title: "Dynacard SVG Diagnostic Charts"
description: Engineering-quality SVG schematics and diagnostic card gallery for the dynacard marketing brochure
version: 1.0.0
module: digitalmodel/marine_ops/artificial_lift/dynacard
status: ready
session:
  id: dynacard-svg-charts
  agent: claude-opus-4-6
review: pending
---

# Dynacard SVG Diagnostic Charts

## Context

The marketing brochure (`docs/marketing/dynacard-ai-diagnostics-brochure.md`) uses ASCII art for the rod pump schematic and diagnostic card gallery. This doesn't render in VS Code preview and is not engineering quality. Need to replace with proper SVG diagrams that render on GitHub.com, VS Code, and in presentations.

**Reference pattern**: `src/digitalmodel/hydrodynamics/hull_library/schematic_generator.py` — pure-Python SVG generation with `CoordMapper`, SVG primitives, and `save_all()`. Proven to render on GitHub.

## Approach: visualization/ Subpackage

A single file would exceed the 400-line limit. Create a `visualization/` subpackage under the dynacard package with modular renderers.

## Deliverables

1. **Rod pump system schematic** — Vertical cross-section SVG with labeled components + normal card
2. **18-card diagnostic gallery** — 3-column grid organized by tier with colored headers
3. **Annotated diagnostic card** — Single card (Fluid Pound) with ML results overlay
4. **18 individual card SVGs** — One per failure mode
5. **Interactive Plotly HTML gallery** — Optional clickable dashboard

## New Files

### `src/.../dynacard/visualization/` subpackage

| File | Responsibility | Est. Lines |
|------|---------------|-----------|
| `svg_primitives.py` | `CoordMapper`, SVG helpers, `COLORS` dict, `draw_card_grid()` | ~150 |
| `card_renderer.py` | `CardRenderer` — single card SVG (standalone + compact for embedding) | ~200 |
| `gallery_renderer.py` | `GalleryRenderer` — 18-card grid with tier headers | ~250 |
| `rod_pump_schematic.py` | `RodPumpSchematicGenerator` — pump system cross-section | ~350 |
| `diagnostic_annotator.py` | `DiagnosticAnnotator` — card with ML annotations panel | ~200 |
| `plotly_gallery.py` | Optional Plotly HTML gallery (18 subplots) | ~200 |
| `__init__.py` | Public API re-exports | ~30 |

### Test file

`tests/marine_ops/artificial_lift/dynacard/test_visualization.py` (~250 lines)

### Generated SVG output

```
docs/marketing/schematics/
    rod_pump_system.svg
    diagnostic_gallery.svg
    diagnostic_fluid_pound.svg
    cards/
        normal.svg
        gas_interference.svg
        ... (18 total)
    gallery.html  (Plotly)
```

## Key Design Decisions

### Color scheme
```python
COLORS = {
    "background": "#ffffff",  "grid": "#e0e0e0",
    "text": "#333333",        "frame": "#666666",
    "card_trace": "#1a3a5c",  "card_fill": "#e8f0f8",
    "ideal_card": "#00bcd4",
    "tier_1": "#2e7d32",      # Green (core)
    "tier_2": "#f57f17",      # Amber (field failures)
    "tier_3": "#c62828",      # Red (mechanical)
    "annotation": "#6a1b9a",  # Purple (ML callouts)
}
```

### Gallery layout: 3 columns, tier header bands
- Tier 1 (7 modes): 3 rows (3+3+1)
- Tier 2 (5 modes): 2 rows (3+2)
- Tier 3 (6 modes): 2 rows (3+3)
- Full-width colored tier header between groups
- Each card auto-scaled to fill its cell (handles small cards like STUCK_PUMP)
- ~920 x 2200 px total

### Card rendering
- `render()` returns standalone SVG string
- `render_compact()` returns `<g>` fragment for gallery embedding
- Auto-scales axes per card (no shared axes — each card fills its cell)

### Rod pump schematic
- Left 60%: vertical cross-section (surface unit → wellbore → pump → reservoir)
- Right 40%: normal dynamometer card with data flow arrow
- Simple geometric shapes (rectangles, arcs, lines) — not photorealistic

### GitHub SVG constraints
- Inline attributes only (no `<style>` blocks, no `<script>`)
- `xmlns="http://www.w3.org/2000/svg"` required
- `font-family="sans-serif"` for text
- No `<foreignObject>` (stripped by GitHub)

## Implementation Sequence (TDD)

| Step | What | Tests First |
|------|------|-------------|
| 1 | `svg_primitives.py` — CoordMapper + all helpers | CoordMapper mapping, SVG string validation |
| 2 | `card_renderer.py` — single card rendering | Valid SVG, polyline present, XML parse, 18-mode parametrized |
| 3 | `gallery_renderer.py` — 18-card grid | 18 traces, tier headers, valid XML |
| 4 | `rod_pump_schematic.py` — pump system | Component labels, card inclusion, valid XML |
| 5 | `diagnostic_annotator.py` — annotated card | Classification text, confidence, valid XML |
| 6 | `plotly_gallery.py` — HTML gallery | HTML output exists, contains plotly div |
| 7 | Generate all SVGs, update brochure | File existence, brochure image refs |

## Modified Files

- `docs/marketing/dynacard-ai-diagnostics-brochure.md` — Replace ASCII art sections with `![caption](schematics/filename.svg)` references
- `src/.../dynacard/__init__.py` — Optionally expose `visualization` subpackage

## Critical Reference Files

- `src/digitalmodel/hydrodynamics/hull_library/schematic_generator.py` — SVG pattern to follow
- `src/digitalmodel/marine_ops/artificial_lift/dynacard/card_generators.py` — ALL_GENERATORS registry
- `src/digitalmodel/marine_ops/artificial_lift/dynacard/diagnostics.py` — FAILURE_MODES, tier definitions
- `src/digitalmodel/marine_ops/artificial_lift/dynacard/models.py` — CardData, DiagnosticResult

## Verification

```bash
# Run visualization tests
cd /mnt/local-analysis/workspace-hub/digitalmodel
PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/marine_ops/artificial_lift/dynacard/test_visualization.py -v --tb=short --noconftest -c /dev/null

# Generate all SVGs
PYTHONPATH="src:../assetutilities/src" python3 -c "
from pathlib import Path
from digitalmodel.marine_ops.artificial_lift.dynacard.visualization import *
out = Path('docs/marketing/schematics')
generate_gallery(out / 'diagnostic_gallery.svg')
generate_rod_pump_schematic(out / 'rod_pump_system.svg')
generate_sample_diagnostic(out / 'diagnostic_fluid_pound.svg')
render_all_individual_cards(out / 'cards')
print('All SVGs generated')
"

# Verify SVGs are valid XML
python3 -c "
import xml.etree.ElementTree as ET
from pathlib import Path
for svg in Path('docs/marketing/schematics').rglob('*.svg'):
    ET.parse(svg)
    print(f'OK: {svg}')
"
```
