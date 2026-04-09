---
title: "Cross-Wiki Link Index"
created: 2026-04-09
last_updated: 2026-04-09
total_cross_references: 25
auto_generated: true
generator: scripts/knowledge/wiki-cross-links.py
---

# Cross-Wiki Link Index

Bidirectional cross-references discovered between the engineering wiki and the three domain wikis (marine-engineering, maritime-law, naval-architecture). Initially created manually by issue #2044, now maintained by `scripts/knowledge/wiki-cross-links.py` (issue #2011). Run `bash scripts/knowledge/wiki-cross-links.sh --apply` to regenerate.

## Engineering <-> Marine-Engineering (15 links)

| # | Source Wiki | Source Page | Target Wiki | Target Page | Link Type |
|---|------------|------------|-------------|-------------|-----------|
| 1 | engineering | concepts/cathodic-protection-design | marine-engineering | concepts/cathodic-protection-system | Complementary CP design coverage (DNV-RP-B401) |
| 2 | engineering | concepts/cathodic-protection-design | marine-engineering | concepts/corrosion-control | CP as one of five corrosion control strategies |
| 3 | engineering | concepts/cathodic-protection-design | marine-engineering | concepts/coating-breakdown | Coating breakdown tables driving CP current demand |
| 4 | engineering | concepts/cathodic-protection-design | marine-engineering | entities/anode | Sacrificial anode materials and design parameters |
| 5 | engineering | concepts/pipeline-integrity-assessment | marine-engineering | concepts/corrosion-control | Corrosion strategies affecting pipeline degradation |
| 6 | engineering | concepts/pipeline-integrity-assessment | marine-engineering | concepts/sour-service | H2S cracking as pipeline integrity threat |
| 7 | engineering | concepts/viv-riser-fatigue | marine-engineering | concepts/mooring-line-failure | Fatigue methodology applicable to mooring lines |
| 8 | engineering | concepts/cfd-offshore-hydrodynamics | marine-engineering | concepts/long-period-swell-resonance | CFD/diffraction for resonant vessel response |
| 9 | engineering | concepts/cfd-offshore-hydrodynamics | marine-engineering | concepts/mooring-line-failure | Hydrodynamic loads on moored vessels |
| 10 | engineering | concepts/sn-curve-fatigue-definitions | marine-engineering | concepts/mooring-line-failure | S-N methodology for mooring component fatigue |
| 11 | engineering | concepts/energy-field-economics | marine-engineering | concepts/process-safety | Safety systems as capex/opex in field development |
| 12 | engineering | entities/orcaflex-solver | marine-engineering | entities/lng-carrier-mooring | OrcaFlex for LNG carrier mooring analysis |
| 13 | engineering | entities/orcaflex-solver | marine-engineering | concepts/mooring-line-failure | OrcaFlex for dynamic mooring load prediction |
| 14 | engineering | standards/dnv-rp-c205 | marine-engineering | concepts/long-period-swell-resonance | Wave spectra and drift forces for swell loads |
| 15 | marine-engineering | concepts/process-safety | maritime-law | entities/deepwater-horizon-2010 | DWH as process safety failure case |

## Engineering <-> Naval-Architecture (8 links)

| # | Source Wiki | Source Page | Target Wiki | Target Page | Link Type |
|---|------------|------------|-------------|-------------|-----------|
| 16 | engineering | concepts/cfd-offshore-hydrodynamics | naval-architecture | concepts/seakeeping | CFD for vessel RAO and seakeeping optimization |
| 17 | engineering | concepts/cfd-offshore-hydrodynamics | naval-architecture | concepts/resistance-propulsion | CFD for resistance prediction |
| 18 | engineering | concepts/fea-structural-analysis | naval-architecture | concepts/ship-structures | FEA for hull girder and ship structural analysis |
| 19 | engineering | concepts/sn-curve-fatigue-definitions | naval-architecture | concepts/ship-structures | S-N curve fatigue for ship structures |
| 20 | engineering | standards/dnv-rp-c203 | naval-architecture | concepts/ship-structures | Fatigue standard for ship structural details |
| 21 | engineering | standards/dnv-rp-c205 | naval-architecture | concepts/seakeeping | Wave spectra and RAO computation methods |
| 22 | engineering | entities/aqwa-solver | naval-architecture | concepts/seakeeping | AQWA for vessel motion RAOs |
| 23 | engineering | entities/aqwa-solver | naval-architecture | concepts/hydrostatics | AQWA uses hydrostatic properties as inputs |

## Engineering <-> Maritime-Law (4 links)

| # | Source Wiki | Source Page | Target Wiki | Target Page | Link Type |
|---|------------|------------|-------------|-------------|-----------|
| 24 | engineering | concepts/pipeline-integrity-assessment | maritime-law | concepts/environmental-liability | Pipeline spills trigger strict liability |
| 25 | engineering | concepts/energy-field-economics | maritime-law | concepts/environmental-liability | Environmental liability as field development risk |
| 26 | engineering | concepts/energy-field-economics | maritime-law | concepts/opa-90 | OPA 90 unlimited liability impacts project economics |
| 27 | maritime-law | entities/deepwater-horizon-2010 | marine-engineering | concepts/process-safety | DWH as landmark process safety failure |

## Summary

| Wiki Pair | Cross-References | Direction |
|-----------|-----------------|-----------|
| engineering <-> marine-engineering | 15 | Bidirectional |
| engineering <-> naval-architecture | 8 | Bidirectional |
| engineering <-> maritime-law | 4 | Bidirectional |
| marine-engineering <-> maritime-law | 2 | Bidirectional (via process-safety/DWH) |
| **Total** | **27** | |

## Pages Modified

### Engineering Wiki (11 pages)
- `concepts/cathodic-protection-design.md` — +4 cross-wiki links
- `concepts/cfd-offshore-hydrodynamics.md` — +4 cross-wiki links
- `concepts/energy-field-economics.md` — +3 cross-wiki links
- `concepts/fea-structural-analysis.md` — +1 cross-wiki link
- `concepts/pipeline-integrity-assessment.md` — +3 cross-wiki links
- `concepts/sn-curve-fatigue-definitions.md` — +2 cross-wiki links
- `concepts/viv-riser-fatigue.md` — +1 cross-wiki link
- `entities/aqwa-solver.md` — +2 cross-wiki links
- `entities/orcaflex-solver.md` — +2 cross-wiki links
- `standards/dnv-rp-c203.md` — +1 cross-wiki link
- `standards/dnv-rp-c205.md` — +2 cross-wiki links

### Marine-Engineering Wiki (8 pages)
- `concepts/cathodic-protection-system.md` — +1 cross-wiki link
- `concepts/coating-breakdown.md` — +1 cross-wiki link
- `concepts/corrosion-control.md` — +2 cross-wiki links
- `concepts/long-period-swell-resonance.md` — +2 cross-wiki links
- `concepts/mooring-line-failure.md` — +4 cross-wiki links
- `concepts/process-safety.md` — +2 cross-wiki links
- `concepts/sour-service.md` — +1 cross-wiki link
- `entities/anode.md` — +1 cross-wiki link
- `entities/lng-carrier-mooring.md` — +1 cross-wiki link

### Naval-Architecture Wiki (4 pages)
- `concepts/hydrostatics.md` — +1 cross-wiki link
- `concepts/resistance-propulsion.md` — +1 cross-wiki link
- `concepts/seakeeping.md` — +3 cross-wiki links
- `concepts/ship-structures.md` — +3 cross-wiki links

### Maritime-Law Wiki (3 pages)
- `concepts/environmental-liability.md` — +2 cross-wiki links
- `concepts/opa-90.md` — +1 cross-wiki link
- `entities/deepwater-horizon-2010.md` — +1 cross-wiki link
