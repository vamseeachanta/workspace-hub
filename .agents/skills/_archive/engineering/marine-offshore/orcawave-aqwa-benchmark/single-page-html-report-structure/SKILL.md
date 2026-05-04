---
name: orcawave-aqwa-benchmark-single-page-html-report-structure
description: 'Sub-skill of orcawave-aqwa-benchmark: Single-Page HTML Report Structure
  (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Single-Page HTML Report Structure (+3)

## Single-Page HTML Report Structure


Sections flow top-to-bottom:
1. **Header** — Vessel name, date, overall consensus badge
2. **Input Comparison** — Solver-column table with geometry, mass, environment, damping
3. **Consensus Summary** — Per-DOF badges (FULL/SPLIT/NO_CONSENSUS)
4. **Per-DOF Analysis** — 2-column grid (text left 45%, plot right 55%)
5. **Full Overlay Plots** — Combined amplitude/phase plots
6. **Notes** — Auto-generated observations

## Significance Filtering


Auto-omit headings with negligible response (< 1% of DOF peak amplitude). Standard omissions for a barge:
- Surge: omit 90deg (beam seas — no surge excitation)
- Sway: omit 0deg, 180deg (head/following — no sway excitation)
- Roll: omit 0deg, 180deg (head/following — no roll excitation)
- Pitch: omit 90deg (beam seas — no pitch excitation)
- Yaw: omit 0deg, 90deg, 180deg (symmetric body — minimal yaw)

## Solver-Column Comparison Tables


Group by heading (rows), solver names as column headers:
```
| Heading | AQWA Amplitude | OrcaWave Amplitude | AQWA Phase | OrcaWave Phase |
|---------|----------------|---------------------|------------|----------------|
| 0deg    | 1.234          | 1.231               | -89.5      | -90.1          |
```

## Revision Tracking


Store outputs in `benchmark_output/barge_benchmark/<revision>/` with `revision.json`:
```json
{
  "revision": "r4_per_dof_report",
  "timestamp": "2026-02-08T20:09:49",
  "previous_revision": "r3_input_comparison",
  "source_files": { "orcawave": "...", "aqwa": "..." }
}
```
