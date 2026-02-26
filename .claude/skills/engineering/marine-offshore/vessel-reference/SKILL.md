---
name: vessel-reference
description: Engineering reference data for the 82,000 DWT Kamsarmax bulk carrier — principal
  particulars, MAN B&W 5S60MC-C8 engine specs, BV classification notations, hydrostatics,
  and OrcaFlex/OrcaWave modeling parameters.
version: 1.0.0
updated: 2026-02-25
category: marine-offshore
tags:
  - kamsarmax
  - bulk-carrier
  - vessel-data
  - principal-particulars
  - man-bw
  - bv-class
  - orcaflex
  - hydrostatics
triggers:
  - vessel reference
  - kamsarmax
  - bulk carrier particulars
  - 82000 DWT
  - 82k DWT
  - MAN B&W 5S60MC
  - vessel principal particulars
  - BV bulk carrier
  - vessel OrcaFlex parameters
see_also:
  - orcaflex-vessel-setup
  - naval-architecture
  - ship-dynamics-6dof
  - diffraction-analysis
  - orcawave-analysis
---

# Vessel Reference — 82,000 DWT Kamsarmax Bulk Carrier

Engineering reference for the 82k DWT Kamsarmax bulk carrier. Use for OrcaFlex/OrcaWave
modeling, hydrostatic analysis, structural checks, and general engineering reference.

Source: Principal Particulars drawing (bilingual EN/CN), cross-validated against published
Kamsarmax fleet data and MAN B&W engine project guide.

---

## Principal Particulars

| Parameter | Value | Notes |
|-----------|-------|-------|
| Length O.A. | abt. 229.00 m | Kamsarmax limit (Port of Kamsar, Guinea) |
| Length B.P. | 225.50 m | Used for hydrostatics / Fn calculations |
| Breadth (MLD) | 32.26 m | Max original Panama Canal beam |
| Depth (MLD) | 20.05 m | |
| Designed Draft | 12.20 m | Operating condition |
| Scantling Draft | 14.45 m | Structural limit / classification draft |
| Deadweight (scantling) | abt. 82,000 t | |
| Service Speed | 14.1 knots | At CSR, T = 12.2 m, 15% sea margin |
| Endurance | abt. 22,000 n.miles | |
| Complement | 27 persons | |

### Vessel Class

**Kamsarmax** — longest sub-class of the Panamax family. Distinguishing constraints:

| Class | LOA limit | Beam limit | DWT range | Constraint |
|-------|-----------|------------|-----------|------------|
| Panamax | ~225 m | 32.26 m | 65–80k t | Panama Canal original locks |
| **Kamsarmax** | **229 m** | **32.26 m** | **80–82k t** | Port of Kamsar, Guinea |
| Post-Panamax | — | >32.3 m | >80k t | No Panama Canal transit |

---

## Main Engine — MAN B&W 5S60MC-C8 (Tier II)

### Designation Decoded

- `5` — 5 cylinders
- `S` — Super long stroke (stroke/bore ≈ 4.0)
- `60` — 600 mm bore
- `MC` — Mechanically controlled (cam-shaft fuel injection & exhaust)
- `C` — Compact (stiffer crankshaft vs standard MC)
- `8` — Mark 8 (8th generation)

### Key Engine Data

| Parameter | Value |
|-----------|-------|
| Type | 2-stroke, uniflow scavenged, crosshead diesel |
| Cylinders | 5 |
| Bore | 600 mm |
| Stroke | 2,400 mm |
| Stroke/bore ratio | 4.0 |
| MCR power (L1) | 11,275 kW at 105 RPM |
| Power/cylinder at MCR | 2,255 kW |
| Typical CSR (85–90% MCR) | ~9,590–10,150 kW |
| SFOC at MCR | ~170 g/kWh |
| SFOC at CSR | ~167 g/kWh |
| HFO consumption at CSR | ~38.4 t/day (main engine) |
| NOx compliance | IMO MARPOL Annex VI Tier II |
| Fuel injection | VIT cam-controlled (mechanical) |
| Turbocharger | MAN B&W TCA-series (single) |

### Endurance Cross-Check

```
22,000 n.miles ÷ 14.1 kn = ~1,560 hrs = ~65 days
38.4 t/day × 65 days = ~2,496 t HFO (main engine)
+ auxiliary (~3–4 t/day × 65) = ~195–260 t
Total ≈ 2,700–2,760 t  →  bunker capacity ~2,800–3,200 t ✓
```

---

## Bureau Veritas Classification Notation

Full notation: `BV +HULL, +MACH, Bulk carrier BC-A, GRAB(20), CSR,
Holds 2,4, and 6 may be empty, ESP, unrestricted navigation,
+AUT-UMS, VeriSTAR-HULL, INWATERSURVEY, MONSHAFT`

| Notation | Meaning |
|----------|---------|
| **+HULL** | BV hull class at superior (+) compliance level |
| **+MACH** | BV machinery class at superior level |
| **BC-A** | Most stringent bulk carrier structural category — designed for high-density cargo with specified holds empty at scantling draft |
| **GRAB(20)** | Holds/hatches rated for mechanical grab discharge up to 20 t grab weight |
| **CSR** | IACS Common Structural Rules for Bulk Carriers — harmonised min. scantlings |
| **Holds 2,4,6 empty** | BC-A operational condition: even-numbered holds may be empty at scantling draft (7-hold arrangement) |
| **ESP** | Enhanced Survey Programme — mandatory detailed structural surveys per IACS UR Z10 |
| **Unrestricted navigation** | Worldwide ocean trading, no geographic/weather restriction |
| **+AUT-UMS** | Automated unattended machinery spaces — engine room may be unmanned at sea |
| **VeriSTAR-HULL** | BV digital class record — structural data in VeriSTAR-Hull database, risk-based survey planning |
| **INWATERSURVEY** | Underwater hull surveys (divers/ROV) approved in lieu of dry-docking at defined intervals |
| **MONSHAFT** | Monitored tail shaft — continuous vibration/temperature/oil-analysis monitoring extends shaft survey interval up to 7.5 years |

---

## Cargo Hold Configuration

**7 holds / 7 hatches** (confirmed by BC-A notation: holds 2, 4, 6 of 7 may be empty)

| Hold | Grain capacity (m³) | Bale capacity (m³) |
|------|--------------------|--------------------|
| 1 (fwd) | ~10,500 | ~9,800 |
| 2 | ~14,500 | ~13,600 |
| 3 | ~15,000 | ~14,000 |
| 4 | ~15,200 | ~14,200 |
| 5 | ~15,200 | ~14,200 |
| 6 | ~14,500 | ~13,600 |
| 7 (aft) | ~13,500 | ~12,600 |
| **Total** | **~98,400** | **~92,000** |

Construction: double-bottom + double-side (wing) tanks + topside wing tanks + hopper tanks.
Cargo gear: **gearless** (shore cranes required).

---

## Hydrostatics

### Key Form Coefficients

| Parameter | Scantling (14.45 m) | Design (12.20 m) |
|-----------|--------------------|--------------------|
| Displacement | ~101,000–103,000 t | ~83,500–86,000 t |
| Lightweight | ~18,500–20,500 t | — |
| Block coefficient CB | ~0.82–0.84 | ~0.80–0.82 |
| Midship coeff CM | ~0.995–0.998 | — |
| Waterplane coeff CW | ~0.88–0.91 | — |
| Prismatic coeff CP | ~0.82–0.85 | — |
| Froude number (14.1 kn) | — | **~0.153** |
| L/B ratio | 6.99 | — |
| B/D ratio | 1.61 | — |

`Fn = V / √(g·L) = 14.1×0.5144 / √(9.81×225.5) = 0.153` (displacement regime)

### Stability (Typical)

| Condition | Draft | GM_T |
|-----------|-------|------|
| Full load (scantling) | 14.45 m | ~1.5–2.5 m |
| Operating (design) | 12.20 m | ~2.0–3.5 m |
| Heavy ballast | ~8.5 m | ~3.0–5.0 m |

### Structural Limits (CSR BC-A)

- Max SWBM hogging: ~2,000–3,000 MN·m
- Max SWBM sagging: ~1,500–2,500 MN·m
- Fatigue design life: 25 years minimum (CSR requirement)
- Double bottom height: ~2.6–2.8 m (CSR min = B/15 = 2.15 m)

---

## OrcaFlex / OrcaWave Modeling Parameters

### Mass & Inertia (per loading condition)

| Parameter | Loaded (14.45 m) | Ballast (~8.5 m) | Units |
|-----------|-----------------|------------------|-------|
| Displacement mass | ~101,000–103,000 | ~28,000–32,000 | t |
| KG | ~8.5–9.5 | ~10.5–12.0 | m |
| LCG from midship (fwd+) | ~0 to +2 | ~0 to +5 | m |
| k_xx (roll) | **~11.9** (≈ 0.37·B) | ~13.5–15.0 | m |
| k_yy (pitch) | **~56.4** (≈ 0.25·Lpp) | ~58–64 | m |
| k_zz (yaw) | **~57–59** | ~59–65 | m |

### Hydrostatic Properties (OrcaFlex Vessel Type)

| Parameter | Loaded | Ballast | Units |
|-----------|--------|---------|-------|
| Displaced volume | ~98,500–100,500 | ~27,200–31,200 | m³ |
| Waterplane area | ~5,700–6,200 | ~5,400–5,900 | m² |
| KB | ~7.8–8.5 | ~4.8–5.5 | m |
| BM transverse | ~6.5–8.0 | ~15–20 | m |
| KM transverse | ~14.5–16.5 | ~20–25 | m |

### Natural Periods

| Mode | Loaded | Ballast |
|------|--------|---------|
| Roll T_r | ~12–16 s | ~8–12 s |
| Pitch T_p | ~7–9 s | ~7–9 s |
| Heave T_h | ~8–11 s | ~6–8 s |

Roll period check: `T = 2π·k_xx / √(g·GM) = 2π·11.9 / √(9.81·2.0) ≈ 16.8 s` ✓

### Diffraction Analysis Setup

| Parameter | Recommendation |
|-----------|----------------|
| Panel mesh size | Lpp/50 – Lpp/80 ≈ 2.8–4.5 m at waterline |
| Frequency range | 0.05–2.0 rad/s (T ≈ 3–125 s) |
| Heading range | 0°–180° in 15° or 30° steps (port-starboard symmetry) |
| Irregular frequency removal | Recommended |
| Drafts to analyse | Loaded (14.45 m), ballast (~8.5 m), design (12.2 m) |
| Preferred solver | **BV Hydrostar** (consistent with BV classification + VeriSTAR-HULL) |
| Alternatives | AQWA, OrcaWave, WAMIT |

### Roll Damping Note

Potential damping from diffraction analysis significantly underestimates roll damping.
Add viscous roll damping in OrcaFlex:
- Typical linear roll damping: 5–10% critical
- Use "Additional Linear Damping" or "Additional Quadratic Damping" on the vessel type
- Critical for beam-sea operability assessments

### Wind & Current Drag Areas (Typical)

| Parameter | Loaded | Ballast |
|-----------|--------|---------|
| Wind area lateral (m²) | ~4,500–5,500 | ~5,500–6,500 |
| Wind area longitudinal (m²) | ~600–800 | ~700–900 |
| Cd wind lateral | ~0.8–1.2 | — |
| Cd current lateral | ~0.6–0.9 | — |

---

## OrcaFlex YAML Snippet (Vessel Type)

```yaml
VesselTypes:
  - Name: Kamsarmax_82k
    Length: 225.5           # Lpp (m)
    # Draught-specific data (add one entry per draft condition)
    Draughts:
      - Draught: 14.45      # scantling
        Mass: 102000.0      # tonnes — adjust to actual displacement
        CentreOfMass: [1.0, 0.0, 9.0]   # [Lpp fwd of midship, 0, KG] m
        MomentsOfInertia: [14450000, 1462000000, 1508000000]  # [Ixx, Iyy, Izz] t·m²
        # Ixx = m·k_xx² = 102000 × 11.9² ≈ 14.45e6 t·m²
        # Iyy = m·k_yy² = 102000 × 56.4² ≈ 324e6 t·m²  (adjust)
        HydrodynamicData:
          Source: Hydrostar   # or AQWA / OrcaWave
          File: data/kamsarmax_hydrostar_loaded.dat

      - Draught: 8.5        # heavy ballast
        Mass: 30000.0
        CentreOfMass: [3.0, 0.0, 11.0]
        HydrodynamicData:
          Source: Hydrostar
          File: data/kamsarmax_hydrostar_ballast.dat

Vessels:
  - Name: Kamsarmax
    VesselType: Kamsarmax_82k
    Draught: 14.45
    InitialPosition: [0.0, 0.0, 0.0]
    InitialHeading: 0.0
    Connection: Free
    Calculation:
      PrimaryMotion: 6 DOF calculated
      IncludeWaveLoad: Calculated from RAOs (first order)
      IncludeDriftLoad: Calculated from QTFs
      IncludeCurrentLoad: Yes
      IncludeWindLoad: Yes
```

---

## Sources

- Principal Particulars drawing (screenshot 2026-02-25) — bilingual EN/CN table
- MAN B&W S60MC-C8 Project Guide — engine layout data
- BV Rules NR 467 — classification notations
- IACS Common Structural Rules for Bulk Carriers (CSR-BC)
- Published Kamsarmax fleet data (Tsuneishi, Horizonship)
- OrcaFlex documentation — vessel type configuration
