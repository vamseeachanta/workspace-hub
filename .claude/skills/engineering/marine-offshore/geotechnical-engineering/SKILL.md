---
name: geotechnical-engineering
version: "1.0.0"
updated: 2026-02-26
category: engineering/marine-offshore
description: |
  Domain expertise for offshore geotechnical analysis planning — soil
  classification, foundation design method selection, pile/anchor capacity,
  on-bottom stability, and scour prediction.
tags: [geotechnical, soil, foundation, pile, anchor, scour, offshore]
platforms: [linux, macos, windows]
invocation: geotechnical-engineering
depends_on: []
requires: []
see_also:
  - mooring-analysis
  - structural-analysis
  - marine-offshore-engineering
---

# Geotechnical Engineering Skill

Offshore geotechnical analysis domain expertise for planning soil
investigations, selecting foundation design methods, and sizing geotechnical
elements (piles, anchors, mudmats, scour protection).

## When to Use This Skill

- Planning a geotechnical analysis campaign
- Selecting bearing capacity or pile capacity methods
- Choosing anchor type for given soil and loading conditions
- Reviewing soil parameter derivation from CPT or borehole data
- Mapping standards coverage for geotechnical calculations

## Soil Classification Systems

### USCS (Unified Soil Classification System)
| Symbol | Description | Typical su (kPa) | Typical φ' (°) |
|--------|-------------|-------------------|-----------------|
| CH | Fat clay | 20–200 | — |
| CL | Lean clay | 10–100 | — |
| ML | Silt | 5–50 | 25–30 |
| SM | Silty sand | — | 28–34 |
| SP | Poorly graded sand | — | 30–36 |
| SW | Well graded sand | — | 33–40 |
| GP | Poorly graded gravel | — | 35–42 |

### Robertson CPT Classification (1990/2009)
| Zone | Ic Range | Soil Behaviour Type |
|------|----------|---------------------|
| 1 | — | Sensitive fine grained |
| 2 | > 3.60 | Organic soils / peat |
| 3 | 2.95–3.60 | Clays (clay to silty clay) |
| 4 | 2.60–2.95 | Silt mixtures |
| 5 | 2.05–2.60 | Sand mixtures |
| 6 | 1.31–2.05 | Sands (clean to silty) |
| 7 | < 1.31 | Gravelly sand to dense sand |

## Method Selection Decision Tree

### Bearing Capacity
```
Undrained (clay)?
  ├── Yes → Brinch Hansen general formula (DNV-RP-C212 Sec 5)
  │         Nc = 5.14 for strip, shape/depth/inclination factors
  └── No (sand) → Terzaghi/Meyerhof drained bearing capacity
                   Nq, Nγ from friction angle
```

### Pile Capacity
```
Soil type?
  ├── Clay → Alpha method (API RP 2GEO Sec 6.4)
  │          f = α × su; α from su/σ'v ratio
  ├── Sand → Beta method (API RP 2GEO Sec 6.5)
  │          f = K × σ'v × tan(δ); K from Table 6.5.3-1
  └── Layered → Sum unit shaft resistance per layer
```

### Anchor Type Selection
| Soil Type | Load Direction | Recommended Anchor | Standard |
|-----------|---------------|-------------------|----------|
| Soft clay | Catenary | Drag (Stevpris/Vryhof) | DNVGL-RP-E301 |
| Soft clay | Vertical/taut | Suction caisson | DNV-RP-E303 |
| Stiff clay | Catenary | Drag (high capacity) | DNVGL-RP-E301 |
| Sand | Catenary | Drag anchor | DNVGL-RP-E301 |
| Any | Vertical (TLP) | Suction/driven pile | API RP 2GEO |
| Deep water | Taut leg | Torpedo/SEPLA | project-specific |

## Typical Parameter Ranges

| Parameter | Symbol | Soft Clay | Stiff Clay | Sand |
|-----------|--------|-----------|------------|------|
| Undrained shear strength | su | 5–25 kPa | 50–250 kPa | — |
| Friction angle | φ' | — | — | 28–40° |
| Submerged unit weight | γ' | 4–7 kN/m³ | 7–10 kN/m³ | 8–11 kN/m³ |
| OCR | OCR | 1–3 | 3–20 | 1–5 |
| CPT cone factor | Nkt | 10–18 | 15–25 | — |
| su/σ'v (NC clay) | — | 0.20–0.30 | — | — |

## Standard Reference Map

| Standard | Key Sections | Topic |
|----------|-------------|-------|
| API RP 2GEO | Sec 6 (piles), Sec 8 (foundations) | Pile + foundation design |
| DNV-RP-C212 | Sec 5 (bearing), Sec 6 (piles) | Soil mechanics |
| DNV-RP-E303 | Sec 4–7 | Suction anchor capacity |
| DNVGL-RP-E301 | Sec 3–5 | Drag/fluke anchor design |
| DNV-RP-F109 | Sec 3 | Pipeline on-bottom stability |
| DNV-RP-F107 | Sec 5 | Scour assessment |
| ISO 19901-4 | Sec 7–10 | Foundation design |
| API RP 2SK | Sec 6 | Mooring anchor requirements |

## Module Import Paths

```python
from digitalmodel.geotechnical.soil_models import SoilProfile, SoilLayer
from digitalmodel.geotechnical.piles import PileCapacityAnalysis
from digitalmodel.geotechnical.foundations import ShallowFoundation
from digitalmodel.geotechnical.anchors import AnchorCapacity
from digitalmodel.geotechnical.on_bottom_stability import OnBottomStability
from digitalmodel.geotechnical.scour import ScourPrediction
```

## Related Skills

- `mooring-analysis` — mooring system design consuming anchor capacity
- `structural-analysis` — structural loads feeding foundation design
- `marine-offshore-engineering` — general offshore engineering context

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-26 | Initial skill — method selection, parameter ranges, standards map |
