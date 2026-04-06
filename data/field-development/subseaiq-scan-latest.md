# Field Development Intelligence — Gulf of Mexico & Global Deepwater

## Overview
This report compiles publicly available data on offshore field developments, designed to
feed directly into the digitalmodel/field_development module for concept selection,
CAPEX/OPEX estimation, and FDP (Field Development Plan) generation.

## 1. Gulf of Mexico — Major Field Developments (Deepwater)

### Perdido (Shell)
- Water depth: 2,438 m (8,000 ft) — deepest spar in the world
- Host facility: Spar (SPAR hull), installed 2010
- Fields: Great White, Tobago, Silvertip (tied back)
- Production capacity: 100,000 bbl/d oil, 200 MMcf/d gas
- Subsea infrastructure: 21 subsea wells, 110 km flowlines
- Technology: Subsea boosting, subsea compression trial

### Appomattox (Shell)
- Water depth: 2,250 m (7,400 ft)
- Host facility: Semi-submersible, installed 2019
- Production: 125,000 bbl/d, 300 MMcf/d
- Tied-back fields: Vito (future phase)

### Whale (Shell)
- Water depth: 2,100 m (6,900 ft)
- Host facility: Spar (Bluewater Gulf of Mexico), online 2024
- Production: 45,000 bbl/d

### Atlantis (BP)
- Water depth: 2,150 m (7,050 ft)
- Host facility: Semi-submersible, installed 2007, expanded 2012
- Production: 200,000 bbl/d, 240 MMcf/d
- Tiebacks: NA Kika, Mad Dog (partial)

### Thunder Horse (BP)
- Water depth: 1,844 m (6,050 ft)
- Host facility: Semi-submersible (largest in GoM), installed 2008
- Production: 250,000 bbl/d, 200 MMcf/d
- Expansion: Thunder Horse South (2021)

### Mars (Shell)
- Water depth: 896 m (2,940 ft)
- Host facility: TLP (Tension Leg Platform), installed 1996
- Expansion: Mars B (Olympus TLP, 2014)
- Production: 100,000 bbl/d

### Mad Dog (BP)
- Water depth: 1,480 m (4,850 ft)
- Host facility: Spar → Mad Dog 2 (Semi-sub, 2022)
- Production: 80,000 bbl/d (original), 140,000 bbl/d (expansion)
- Notable: First GoM field with subsea boosting upgrade

### Stones (Shell)
- Water depth: 2,900 m (9,500 ft) — world's deepest floating platform
- Host facility: ETLP (Enhanced Tension Leg Platform), installed 2016
- Production: 20,000 bbl/d, 35 MMcf/d
- Technology: Deepest subsea tieback (20 km to host)

### Walker Ridge (Multiple operators)
- Host facility: Multiple (TLP, Spar, Semi)
- Notable fields: Lucius (LLOG), Hadrian South (ExxonMobil)

## 2. Host Facility Type Selection Patterns

### Spar Platforms
- Range: 1,200–3,000m water depth
- Key GoM Spars: Perdido, Holstein, Boomvang, Nansens, Medusa, Devils Tower
- Advantage: Superior motion performance for steep-wave riser systems
- CAPEX range: $3–7B for deepwater GoM

### Semi-submersibles
- Range: 600–2,500m water depth
- Key GoM Semis: Appomattox, Atlantis, Thunder Horse, Independence Hub
- Advantage: Deck load capacity, drilling capability
- CAPEX range: $4–10B for deepwater GoM

### TLPs
- Range: 300–1,800m water depth
- Key GoM TLPs: Ursa, Mars, Marco Polo, Auger, Magnolia
- Advantage: Minimal motion, dry tree capability
- CAPEX range: $2–6B

### FPSOs (Emerging in GoM)
- Range: 600–3,000m water depth
- First GoM FPSO: Cascade/Chinook (Chevron, upcoming)
- Advantage: Storage capability, mobile, re-deployable
- CAPEX range: $5–12B

## 3. Deepwater Field Development Trends

### Technology Trends (2020–2026)
- Subsea boosting: Increasingly standard for tiebacks >15 km
- Subsea compression: First commercial (Asgard, Norway), GoM pilots underway
- Subsea processing: Separation, pumping, compression at seabed
- Digital twins: Real-time monitoring of host + subsea infrastructure
- Standardized host concepts: Reducing CAPEX through design reuse

### Field Development Economics
- Ultra-deepwater GoM: $50–75/bbl breakeven (2024–2026)
- Subsea tieback to existing host: $15–30/bbl breakeven
- Typical project IRR target: >15% for deepwater
- Average discovery-to-FDP timeline: 5–8 years
- Average FDP-to-first-oil timeline: 3–5 years

### Water Depth Breakdown (GoM Active Developments)
| Category | Depth Range | Count | Typical Host |
|----------|-------------|-------|--------------|
| Deepwater | 300–1,500m | ~80 | TLP, Semi |
| Ultra-deepwater | 1,500–3,000m | ~30 | Spar, Semi, TLP |
| Ultra-ultra-deepwater | >3,000m | ~5 | ETLP, SPAR |

## 4. Global Field Development Parallels

### Brazil Pre-salt
- Lula, Sapinhoá, Búzios: FPSO-hosted giant fields
- Water depth: 2,000–2,500m
- Production: 250,000+ bbl/d per field
- Key lesson: FPSO dominance over fixed hosts in deepwater

### West Africa
- Kaombo (TotalEnergies, Angola): FPSO cluster, 2,000m WD
- Jubilee/Fifty (Ghana): FPSO, 1,100m WD
- Key lesson: Subsea-to-FPSO standard architecture

### Norwegian North Sea
- Johan Sverdrup, Johan Castberg: Semi-sub and FPSO
- Key lesson: Electrification from shore, carbon-neutral target

### Australia NWS
- Ichthys (INPEX): Semi-sub + pipeline, 250m WD
- Gorgon (Chevron): Fixed platform (shallow water)
- Key lesson: LNG-tied developments favor fixed + pipeline

## 5. Implications for digitalmodel/field_development Module

### Concept Selection Framework Inputs
- Water depth drives host type: <300m fixed, 300–1800m TLP, >1500m Spar/Semi/FPSO
- Reservoir size drives production capacity: <50MMbbl tieback, 50–500MMbbl mini-platform, >500MMbbl host
- Distance to infrastructure: <15km subsea tieback preferred
- Fluid type: Oil-ratio vs gas-ratio affects processing needs

### CAPEX Estimation Benchmarks
| Facility Type | CAPEX Range | Typical Payback |
|---------------|-------------|-----------------|
| Subsea tieback (<10km) | $200–500M | 2–4 years |
| Subsea tieback (>20km) | $500M–1.2B | 3–6 years |
| TLP host | $2–6B | 5–8 years |
| Spar host | $3–7B | 5–10 years |
| Semi host | $4–10B | 5–10 years |
| FPSO | $5–12B | 5–10 years |

### Data Sources for Module Integration
- BSEE.gov: GoM well, platform, production data (public API)
- BOEM.gov: Lease blocks, field boundaries, environmental data
- EIA.gov: Production forecasts, reserves
- SubseaIQ.com: Commercial field development database
- Rystad Energy: Commercial market intelligence

## 6. Recommended Module Structure

```python
class FieldDevelopmentAnalysis:
    def concept_selection(water_depth, reservoir_size, distance_to_infra, fluid_type)
    def estimate_capex(host_type, production_capacity, water_depth)
    def estimate_opex(host_type, production_capacity, field_age)
    def subsea_tieback_economics(distance, production_rate, fluid_ratio)
    def host_comparison_matrix(water_depth, production_capacity, options)
    def generate_fdp_summary(concept, capex, opex, reserves, production_profile)
    def benchmark_against_goM_fields(water_depth, host_type, production_rate)
    def sensitivity_analysis(capex_range, oil_price_range, production_range)
```
