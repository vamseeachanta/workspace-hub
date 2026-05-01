# B1528 SIROCCO Rudder Source Pack and Benchmark Extraction

> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2569  
> Repo source: https://github.com/vamseeachanta/acma-projects/tree/main/B1528  
> Extraction date: 2026-05-01  
> Vessel aliases: `SIROCCO`, `Sirocco`, user spelling `Sorrocco`.

## Purpose

This source pack records the B1528/SIROCCO rudder geometry, yaw-moment workbook inputs, and available turning/track benchmark evidence before downstream static-yaw and time-trace calculations are implemented.

The pack deliberately separates:

- **authoritative source values** read directly from B1528 files,
- **derived workbook values** produced by formulas in the B1528 workbook,
- **narrative benchmark evidence** extracted from notes, and
- **gaps/limitations** that must not be silently filled in by later calculations.

## Source inventory

| Source | Repo path | Status | Use |
|---|---|---|---|
| Rudder workbook | `B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx` | authoritative workbook source for this pack | geometry, Barrass/PNA sheet formulas, source values |
| Converted workbook script | `B1528/excel_to_py/rudder_force_yaw_moment.py` | derived/convenience script | formula reconnaissance only; not treated as canonical over workbook |
| Breakaway notes | `B1528/ref/SIROCCO breakaway notes.docx` | narrative evidence | VDR/Rosepoint time-heading-speed benchmark extraction |
| ECDIS context note | `B1528/ref/ECDIS Mar 26 Midnight LT.docx` | context only | riverbank/depth context; not a numeric track dataset |
| GA plan | `B1528/excel_to_py/27. SIROCCO-000272-GA Plan.pdf` | referenced drawing | rudder scale/geometry source named by workbook |

Local `acma-projects` checkout was verified current with origin but sparse; `B1528/` was not materialized locally. Extraction therefore used GitHub API/raw downloads into `/tmp/b1528/`.

## Workbook sheets and key cells

| Sheet | Cell(s) | Value / formula | Classification | Notes |
|---|---:|---|---|---|
| `Rudder Area and Ctr` | `D7` | `225.5 m` | authoritative workbook value | Length Between Perpendiculars (LBP). |
| `Rudder Area and Ctr` | `D8` | `32.26 m` | authoritative workbook value | Molded breadth. |
| `Rudder Area and Ctr` | `D10` | `12.2 m` | authoritative workbook value | Design draft. |
| `Rudder Area and Ctr` | `C25` | `44.939563193699 m²` | derived workbook geometry | Total rudder area from scaled sub-areas. |
| `Rudder Area and Ctr` | `C26` | `-1.052026137895 m` | derived workbook geometry | Center of rudder area aft of AP. Negative means forward of AP under workbook sign. |
| `Rudder Area and Ctr` | `C27` | `-1.402701517193` | derived workbook geometry | Rudder center frame number. |
| `Barrass` | `C17` | `600` | selected workbook constant | Barrass rudder constant β. |
| `Barrass` | `C19` | `1.065` | selected workbook constant | Port rudder prop-rotation factor. Workbook note also gives `0.935` for starboard. |
| `Barrass` | `B29` | `135.300000 m` | derived workbook lever | `0.6 * LBP`; legacy yaw lever, not automatically equivalent to CG-to-rudder arm. |
| `Barrass` | `B30` | `1000.535365 mt-m` | derived workbook case | Workbook default case, not the user-requested ±1° case. |

## Formula crosswalk

### Barrass workbook family

The `Barrass` sheet presents both transverse-force text and evaluated cell formulas. The evaluated workbook cells are:

```text
F  = β * AR * V² * Cr                      (Barrass!C20)
Ft = F * sin(α) * cos(α)                   (Barrass!C21, transverse force)
Fn = F * sin(α)                            (Barrass!C22, workbook normal-force proxy)
Yaw moment = (Fn / 1000 / g) * (0.6 * LBP) (Barrass!C23 * Barrass!B29 -> Barrass!B30)
```

The workbook text at `Barrass!B28` says `Ft * LBP * 0.60`, but the evaluated yaw-moment cell uses `C23`, which is derived from `Fn`, not `Ft`. Downstream #2570 must preserve this distinction: workbook-regression mode should reproduce the evaluated workbook, while any transverse-force or reusable `digitalmodel_static_yaw` mode must be separately labeled.

- `AR` is rudder area in m²,
- `V` is hydrodynamic speed in m/s,
- `α` is rudder angle relative to centerline / local inflow assumption in degrees,
- `Cr` is propeller-rotation factor (`1.065` port, `0.935` starboard in workbook notes),
- `β = 600` in the workbook case,
- `g` is approximately `9.8066–9.808 m/s²` depending on workbook cell family.

### Important lever-arm boundary

The workbook yaw lever `0.6 * LBP = 135.300 m` is a legacy Barrass-style moment arm. It must not be silently mapped to `digitalmodel`'s `x_rudder_from_cg_m` without explicit evidence. Downstream reports must label workbook-regression output separately from reusable `digitalmodel_static_yaw` output if both are shown.

## User-requested operating point hand check

For a workbook-regression mode using `V = 2.5 kn`, `AR = 44.939563193699 m²`, `β = 600`, and the legacy yaw lever `135.300 m`:

| Case | Cr | Transverse force Ft (N) | Workbook normal-force proxy Fn (N) | Evaluated-workbook yaw moment (mt-m) | Evaluated-workbook yaw moment (kN-m) | Classification |
|---|---:|---:|---:|---:|---:|---|
| `+1°` | 1.065 | 828.835511 | 828.961765 | 11.436987 | 112.158527 | derived hand-check target |
| `-1°` | 0.935 | -727.663101 | -727.773944 | -10.040923 | -98.467815 | derived hand-check target |

These values are regression targets for #2570 workbook-regression mode. They are not a full ship maneuvering prediction.

## Benchmark extraction summary

Structured benchmark evidence is stored in:

- `docs/projects/acma/B1528/sirocco-turning-benchmark.yaml`

Extracted source families:

1. **VDR narrative points** from `SIROCCO breakaway notes.docx`, parsed with docx paragraph-index traceability (including empty paragraphs). These include UTC time, ship heading, SOG, sometimes COG, and later rudder/engine commands.
2. **Rosepoint salvage video narrative points** from the same notes, parsed with docx paragraph-index traceability. These include local time, approximate speed in mph, and qualitative/relative heading to river current.

The benchmark YAML intentionally marks this as a narrative benchmark, not an original telemetry export. There are no x/y track coordinates in the extracted notes, and tug/current/propulsion/anchor/bank effects mean these points are context for qualitative comparison and time-trace sanity checking, not validation of an isolated rudder-only model.

## Gaps and limitations

- No original VDR CSV/AIS/position time series was present in the files inspected for this pack.
- No project-specific Nomoto `K`/`T` coefficients were found in the inspected sources.
- No direct CG location or mass moment of inertia source was extracted here.
- No class/IMO compliance claim is supported by this source pack.
- The legacy workbook yaw lever is a workbook assumption and requires a mapping decision before it is used in reusable `digitalmodel` coordinates.

## Downstream issue use

- #2570 should cite this pack for B1528 geometry and workbook-regression targets.
- #2571 should cite `sirocco-turning-benchmark.yaml` for benchmark/source-gap behavior and must not invent missing trajectory coordinates or `K/T` coefficients.
