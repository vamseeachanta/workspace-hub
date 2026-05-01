---
title: B1528 Rudder Force and Yaw Moments Workbook
tags: [source, workbook, rudder, yaw-moment, naval-architecture]
added: 2026-05-01
last_updated: 2026-05-01
sources:
  - github://vamseeachanta/acma-projects/B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx
  - github://vamseeachanta/acma-projects/B1528/excel_to_py/rudder_force_yaw_moment.py
domain: acma-projects
cross_links:
  - ../entities/b1528-sirocco-breakaway.md
  - ../concepts/b1528-sirocco-rudder-yaw-moment-inputs.md
---

# B1528 Rudder Force and Yaw Moments Workbook

Workbook: `B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx`  
Converted script: `B1528/excel_to_py/rudder_force_yaw_moment.py`

## Sheets

- `Rudder Area and Ctr` — GA-derived rudder area and longitudinal center.
- `PNA89` — SNAME PNA Vol. III Chapter 9 rudder normal-force formula reference and input stubs.
- `Barrass` — transverse rudder force, yaw moment, tug/current balance calculations.
- `Barrass-chk` — independent Barrass worked-example check.

## Key workbook evidence

### Rudder geometry

| Field | Cell / source | Value |
|---|---|---:|
| LBP | `Rudder Area and Ctr!D7` | `225.5 m` |
| Design draft | `Rudder Area and Ctr!D10` | `12.2 m` |
| Rudder area | `Rudder Area and Ctr!C25` | `44.9395631937 m²` |
| Center of rudder area aft of AP | `Rudder Area and Ctr!C26` | `-1.0520261379 m` |
| Center frame | `Rudder Area and Ctr!C27` | `-1.4027015172` |

### Existing Barrass calculation case

The `Barrass` sheet contains an existing case with ship SOG `0.1 kn`, current `4 kn`, hydrodynamic speed `2.1090082400 m/s`, rudder angle `34.6 deg`, rudder constant `β = 600`, and prop rotation factor `Cr = 1.065`.

Key evaluated workbook values:

| Field | Cell | Value |
|---|---|---:|
| Hydrodynamic speed | `Barrass!C15` | `2.1090082400 m/s` |
| Rudder force parallel to CL | `Barrass!C20` | `127728.043 N` |
| Transverse rudder force | `Barrass!C21` | `59701.727 N` |
| Rudder normal force | `Barrass!C22` | `72529.570 N` |
| Rudder normal force | `Barrass!C23` | `7.394940 mt` |
| 60% LBP lever | `Barrass!B29` | `135.3 m` |
| Rudder yaw moment | `Barrass!B30` | `1000.535 mt-m` |
| Current yaw moment at 175° | `Barrass!B68` | `6611.8 mt-m` |

### 2.5 kn / ±1° preliminary operating point

Using the workbook Barrass formula family with SIROCCO rudder area, speed `2.5 kn` (`1.2861 m/s`), `β = 600`, and lever `0.6 * LBP = 135.3 m`:

| Case | Cr | Rudder angle | Normal force | Yaw moment |
|---|---:|---:|---:|---:|
| Port sensitivity | 1.065 | `+1 deg` | `0.084519 mt` | `+11.435 mt-m` (`+112.143 kN-m`) |
| Starboard sensitivity | 0.935 | `-1 deg` | `-0.074202 mt` | `-10.040 mt-m` (`-98.454 kN-m`) |
| Symmetric Cr sensitivity | 1.000 | `+1 deg` | `+0.079361 mt` | `+10.737 mt-m` (`+105.299 kN-m`) |
| Symmetric Cr sensitivity | 1.000 | `-1 deg` | `-0.079361 mt` | `-10.737 mt-m` (`-105.299 kN-m`) |

These values are preliminary and should be reproduced by a checked-in input file/report before being treated as calculation output.

## Modeling caveats

- The workbook mixes/labels transverse force and normal force in the yaw-moment note. The evaluated `Barrass!B30` uses `C23` (rudder normal force in metric tons) times `0.6 LBP`.
- The workbook contains an explicit note: “However, in 4 knots of current she will make only 2.5 knots effective forward speed.” This should be preserved as an operating-point assumption, not silently converted into a generic vessel speed.
- PNA89 formula content is source context; its worksheet has input stubs and no final computed `FN` at `B69`.

## Related pages

- [B1528 SIROCCO Breakaway](../entities/b1528-sirocco-breakaway.md)
- [B1528 SIROCCO rudder yaw-moment inputs](../concepts/b1528-sirocco-rudder-yaw-moment-inputs.md)
