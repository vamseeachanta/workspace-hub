# Pipeline Engineering Study
> WRK-5060 Feature Spec

## Scope

Model subsea/offshore pipeline engineering calculations: wall thickness design, on-bottom stability, free span analysis, lateral buckling, installation mechanics, and expansion/walking — for fast-running Python assessment tools.

## Key Parameters

| Symbol | Description | Units |
|--------|-------------|-------|
| OD/WT | Pipe outer diameter / wall thickness | m |
| p_d | Design pressure | MPa |
| SMYS | Specified minimum yield strength | MPa |
| Hs/Tp | Significant wave height / peak period | m / s |
| Vc | Current velocity | m/s |
| L_span | Free span length | m |
| f_n | Natural frequency of free span | Hz |
| delta_T | Temperature difference (expansion) | K |

## Sub-domains

1. **Wall thickness** — pressure containment (API 1111, DNV-ST-F101), combined loading
2. **On-bottom stability** — hydrodynamic loading (DNV-RP-F109), soil resistance
3. **Free span** — static/dynamic response, VIV screening (DNV-RP-F105), fatigue
4. **Lateral buckling** — Hobbs solutions, controlled buckling, post-buckling strain
5. **Installation** — S-lay/J-lay catenary, stinger departure angle, residual curvature
6. **Expansion & walking** — axial expansion, walking mechanisms

## Child WRKs

| WRK | Title | Status |
|-----|-------|--------|
| TBD | Literature gathering | pending |
| TBD | Method assessment & selection | pending |
| TBD | Python implementation | pending |

## Output Deliverables

- `digitalmodel/docs/domains/pipelines/pipeline-engineering-literature.md`
- `digitalmodel/docs/domains/pipelines/pipeline-engineering-method-selection.md`
- `digitalmodel/src/digitalmodel/pipelines/` (new namespace)
