# OrcaFlex Modular Examples — Quick Reference

One-page map of all 49 modular example categories. Full parameter details in
`docs/domains/orcaflex/examples/PARAMETER_REFERENCE.md`.

---

## Example Map

| Code | Model type | Analysis | Key features | Primary skill(s) |
|------|-----------|----------|--------------|-----------------|
| **A01** | Flexible riser | Time-domain | Cat / lazy wave / pliant / steep variants; 2-stage | orcaflex-modeling |
| **A02** | S-riser | Time-domain | Lazy S / pliant S / steep S; current 1 m/s | orcaflex-modeling |
| **A03** | Deep riser | Time-domain | No WD in params; embedded in master.yml | orcaflex-modeling |
| **A04** | Deepwater riser | Time-domain | 200m WD; large Hs=14.2m; 4-stage | orcaflex-modeling |
| **A05** | Riser + vessel | Deep water | FPS units (semi/spar/FPSO); WD 2950–6560 ft | orcaflex-modeling |
| **A06** | VIV (SHEAR7) | VIV | FPS units; current-driven; Hs=0 | orcaflex-modeling |
| **B01** | Drilling riser | Drilling ops | 1020m WD; BOP stack | orcaflex-modeling |
| **B06** | Drilling riser | Current-only | 234m WD; no waves | orcaflex-modeling |
| **C03** | Multi-body | Mooring | High current 2 m/s; long dynamic 500s | orcaflex-modeling, orcaflex-mooring-iteration |
| **C05** | Jack-up | Full environment | time_step=0.1; wind+current+waves | orcaflex-modeling |
| **C06** | CALM buoy | Mooring | Wind+current only; buoy with hawser | orcaflex-modeling |
| **C07** | Semi-sub mooring | Deepwater | 500m WD; Hs=13m | orcaflex-modeling, orcaflex-mooring-iteration |
| **C08** | Shallow structure | Static | 40m WD; still conditions | orcaflex-modeling |
| **C09** | Platform | Fine time step | time_step=0.01; small Hs | orcaflex-modeling |
| **C10** | Multi-statics | YAML sweep | Multiple static runs from YAML input | orcaflex-batch-manager, orcaflex-model-generator |
| **D02** | Manifold lowering | 4-stage installation | 137m WD; current-only | orcaflex-installation-analysis |
| **D03** | Subsea | 5-stage | 300m WD; complex sequence | orcaflex-installation-analysis |
| **D04** | Subsea | 2-stage | 120m WD; small Hs=3m | orcaflex-installation-analysis |
| **E01** | S-lay stinger | Pipelay | Explicit + simple geometry variants | orcaflex-installation-analysis |
| **E02** | S-lay | Pipelay | Current-only | orcaflex-installation-analysis |
| **E03** | S-lay | Pipelay | Current | orcaflex-installation-analysis |
| **E04** | S-lay | Pipelay | Single current | orcaflex-installation-analysis |
| **E05** | S-lay (complex) | Pipelay | 8-stage sequence; Hs=0.75m | orcaflex-installation-analysis |
| **E08** | Lay table | YAML batch | Automated lay-table parameter sweep | orcaflex-batch-manager |
| **F01** | Subsea install | Crane ops | Lowered cone / manifold / trapped water | orcaflex-installation-analysis |
| **F02** | Subsea | No waves | 100m WD; current-free | orcaflex-installation-analysis |
| **F03** | Heave winch | Crane | Heave-compensated winch + vessel | orcaflex-installation-analysis |
| **F04** | Subsea | Cross-seas | wave_direction=270° | orcaflex-installation-analysis |
| **F06** | Subsea | Mild waves | Hs=2m; Tp=7s | orcaflex-installation-analysis |
| **F07** | Floating | Wind+current | No water_depth; oblique waves | orcaflex-modeling |
| **G04** | Deepwater mooring | Current-only | 500m WD | orcaflex-mooring-iteration |
| **H01** | Ship ops (shallow) | Passing ship | 28m WD; Hs=8m; oblique dir=350° | orcaflex-modeling |
| **H02** | Ship ops | Still water | No current/wave in params | orcaflex-modeling |
| **H03** | Ship ops | Harsh sea | Hs=13.2m; current=1.67 m/s | orcaflex-modeling |
| **I01** | VIV (native) | OrcaFlex VIV | High current=2 m/s; Hs=2m | orcaflex-modeling |
| **J01** | Jack-up / riser | Multi-stage | 5-stage; 250m WD; no waves | orcaflex-modeling |
| **K01** | FOWT spar (5MW) | Offshore wind | Wind=15 m/s dominant; Hs=6m | orcaflex-modeling |
| **K02** | Wind turbine | External wind | External .bts wind file; no waves | orcaflex-modeling |
| **K03** | FOWT | Wind-dominated | Wind=17.1 m/s; no wave params | orcaflex-modeling |
| **K06** | FPV array | Floating solar | water_density=1025 kg/m³; Hs=0.5m | orcaflex-modeling |
| **L01** | Default vessel | Vessel motions | Standard environment; 100m WD | orcaflex-vessel-setup |
| **L02** | Vessel (FPSO) | Wind+current | wind_speed=15 m/s; no waves | orcaflex-vessel-setup |
| **L03** | Semi-sub | Oblique sea | wave_direction=135° | orcaflex-vessel-setup |
| **L04** | Semi-sub | Hs=5m | WD not in params; embedded | orcaflex-vessel-setup |
| **L05** | Semi-sub | Same as L04 | Identical params to L04 | orcaflex-vessel-setup |
| **M01** | Seabed pipeline | Thermal/walking | Long duration 550–6400 s; no current | orcaflex-modeling |
| **Pipeline spanning** | Pipeline | Seabed lay | 500s; still water | orcaflex-installation-analysis |
| **Z02** | Edge case | In-air | water_density=0.00128 (air density) | orcaflex-modeling |

---

## Skill-to-Example Matrix

| Skill | Primary examples |
|-------|-----------------|
| `orcaflex-modeling` | A01–A06, C03, C05–C09, F07, G04, H01–H03, I01, J01, K01–K06, M01, Z02 |
| `orcaflex-installation-analysis` | D02–D04, E01–E08, F01–F06, Pipeline spanning |
| `orcaflex-batch-manager` | C10 (multi-statics), E08 (lay table) |
| `orcaflex-mooring-iteration` | C03, C07, G04 |
| `orcaflex-vessel-setup` | L01–L05 |
| `orcaflex-model-generator` | A01 (riser spec), C10 (multi-static sweep), any spec.yml workflow |
| `orcaflex-post-processing` | All examples with .sim outputs |

---

*Generated from audit of 62 `inputs/parameters.yml` files. See
`docs/domains/orcaflex/examples/PARAMETER_REFERENCE.md` for full parameter detail.*
