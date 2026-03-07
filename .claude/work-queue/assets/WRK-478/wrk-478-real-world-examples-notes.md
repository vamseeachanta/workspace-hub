# WRK-478 Real-World Validation Examples — Research Notes
# Generated: 2026-03-07 | Status: in-progress (updating implementation-review.html)

## Task
Replace generic test/eval table in `implementation-review.html` with 3 real-world examples:
1. BSEE GOM jacket (internet source)
2. FST Hull (doc-intel: calc-010)
3. Deepwater RBS (doc-intel: calc-004)

---

## Example 1 — BSEE GOM Shallow-Water Jacket (Internet Source)
**Source**: BSEE public offshore structure data (bsee.gov/stats-facts) + BOEM field data
**Structure**: Typical 4-pile fixed steel jacket, Gulf of Mexico, ~70m water depth
**Standard**: DNV-RP-B401-2021

### Inputs
- Seawater temperature: 25°C (Gulf of Mexico, tropical) → band: >17°C
- Seawater resistivity: 0.20 Ω·m (warm Gulf water, ~35 ppt)
- Submerged area: 5 000 m² (combined jacket legs, braces, conductors)
- Splash zone: 300 m²; Atmospheric: 200 m²
- Coating: Cat I (high-quality epoxy, ≥300 µm)
- Design life: 25 yr
- Anode: Al-Zn-In stand-off, L=1.0m, r=0.05m, m_a=200 kg, u=0.85

### Hand-Calculated Expected Results (B401-2021)
Current densities (Table 3-1, >17°C, coated):
- Submerged: i_mean = 0.070 A/m²
- Splash: i_mean = 0.100 A/m² (temp-independent, coated)
- Atmospheric: i_mean = 0.010 A/m² (temp-independent, coated)

Coating breakdown (Cat I, 25yr):
- f_ci = 0.05, k = 0.020
- f_cm = 0.05 + 0.020 × 12.5 = 0.30
- f_cf = 0.05 + 0.020 × 25.0 = 0.55

Current demand:
- Submerged I_mean = 5000 × 0.070 × 0.30 = 105.0 A
- Splash I_mean    =  300 × 0.100 × 0.30 =   9.0 A
- Atmospheric I_mean = 200 × 0.010 × 0.30 = 0.6 A
- TOTAL I_mean = 114.6 A

- Submerged I_final = 5000 × 0.070 × 0.55 = 192.5 A
- Splash I_final    =  300 × 0.100 × 0.55 =  16.5 A
- Atmospheric I_final = 200 × 0.010 × 0.55 = 1.1 A
- TOTAL I_final = 210.1 A

Anode mass (Al, ε=2000 Ah/kg, u=0.85, T=25yr):
- M = 114.6 × 25 × 8760 / (2000 × 0.85)
- M = 25,093,800 / 1700 = 14,761 kg
- N_mass = ceil(14761 / 200) = 74 anodes

Anode resistance (stand-off, Dwight, rho=0.20, L=1.0, r=0.05):
- R = (0.20 / 2π×1.0) × (ln(4×1.0/0.05) − 1)
- R = 0.03183 × (ln(80) − 1) = 0.03183 × (4.382 − 1) = 0.03183 × 3.382 = 0.1077 Ω

Current output per anode (Al: E_drive = −0.80 − (−1.05) = 0.25 V):
- I_per_anode = 0.25 / 0.1077 = 2.32 A

Adequacy check:
- I_total = 74 × 2.32 = 171.7 A vs I_final = 210.1 A → NOT adequate (mass count)
- N_current = ceil(210.1 / 2.32) = ceil(90.6) = 91 anodes
- Recommended = max(74, 91) = 91 anodes ← dual-criterion governs current
- Verify: 91 × 2.32 = 211.1 A > 210.1 A ✓

**Summary**: 91 stand-off anodes, ~18,200 kg net mass, ~21,400 kg gross mass (91×235/0.85 ≈)
Note: current output governs over mass criterion (typical for warm-water platforms)

---

## Example 2 — FST Hull Coastal LNG (Document Intelligence: calc-010)
**Source**: `digitalmodel/docs/domains/cathodic_protection/examples/calc-010-dnv-b401-2021-fst-design-philosophy.md`
**Structure**: Floating Storage Terminal hull, coastal LNG, brackish water
**Standard**: DNV-RP-B401-2021 + ABS GN Ships 2017

### Key Parameters
- Hull surface area: 13,446 m² (15m draft, conservative)
- Seawater temp: 10°C
- Seawater resistivity: 0.5875 Ω·m (10 ppt salinity, design case)
- Design life: 40 yr (primary); 25 yr (secondary)
- Coating: Glass flake reinforced epoxy; fci=0.02, k=0.005/yr
- Anode: Al alloy A3 flush-mounted, L=1.4m, w=0.15m, u=0.85, m_a=27.5 kg (net)
- Anode potential: -1.09 V (vs -1.05 for standard Al; higher-purity alloy)

### Source Results (40yr, 0.5875 Ω·m)
- f_cm = 0.12 (12%), f_cf = 0.22 (22%)
- I_initial = 53.784 A; I_mean = 322.705 A; I_final = 591.626 A
- Required anode mass: 66,515 kg (mean governs)
- N_anodes = 2,419 (mass governs)
- R_anode initial = 0.379 Ω (Lloyd's formula, initial geometry)
- I_per_anode initial = 0.77 A; total initial = 1,850.6 A > 53.784 A ✓
- R_anode final = 0.45 Ω (depleted geometry); I_per_anode = 0.65 A
- Total final output = 2419 × 0.65 = 1,570.3 A > 591.626 A ✓
- Total gross mass = 73,174.8 kg (73.17 MT)

### Sensitivity (1 ppt brackish water, ρ=5.076 Ω·m)
- 40yr: 7,875 anodes, 238,219 kg gross → impractical → ICCP selected

### Module Applicability Note
The B401-2021 module (platform-focused Table 3-1) uses different current densities than
this FST hull example (which uses ABS GN Ships 200 mA/m² bare steel). The coating
breakdown linear formula is consistent; anode mass formula is identical. The FST hull
zone geometry (single "hull" zone) maps to the "submerged" zone concept in B401 platform
module. Direct numerical comparison requires awareness of which current density source is used.

---

## Example 3 — Deepwater Subsea RBS 1710–1900m (Document Intelligence: calc-004)
**Source**: `digitalmodel/docs/domains/cathodic_protection/examples/calc-004-dnvgl-b401-subsea-riser-base.md`
**Structure**: 4 production Riser Base Structures, deepwater, multi-anode-type design
**Standard**: DNVGL-RP-B401:2017

### Key Parameters
- Water depth: 1710–1900 m
- Design life: 27 yr (25 operational + 2 wet storage)
- Seawater resistivity: 0.31 Ω·m
- Zones: Cat III paint (main structure + yoke), 5LPP insulation (piping, jumpers), bare (connector ends)
- 10% surface area contingency on structural surfaces

### Anode Types Used
| Type | Geometry | Net Mass | Ra_init | Ra_final | Ia_init | Ia_final |
|------|----------|----------|---------|---------|---------|---------|
| SO-90 stand-off | 1080×189×180mm | 91.44 kg | 0.119 Ω | 0.175 Ω | 2.100 A | 1.430 A |
| FM-65 flush | 950×186×136mm | 64.04 kg | 0.273 Ω | 0.339 Ω | 0.916 A | 0.740 A |
| FM-15 short flush | yoke frame | ~15 kg (nom) | — | — | — | — |

### Results (4-RBS group)
- Total design current: 9.290 A
- Total net anode mass required: 679.65 kg
- Anode count: 16 SO-90 + 24 FM-65 + 6 FM-15 = 46 total (4-RBS group)
- Per RBS: ~4 SO-90 + 6 FM-65 + 1-2 FM-15 ≈ 11-12 anodes

### Module Applicability
Current densities in calc-004 use DNVGL-RP-B401:2017 Table 6-3 (not 2021 Table 3-1).
The 2017 table uses initial/mean/final (0.220/0.110/0.170 A/m²) for >300m structures,
vs 2021 which uses a single mean density with coating breakdown factors.
The anode mass formula (M = I×T×8760/εu) and resistance formula (Dwight) are the same.
The SO-90 resistance (R=0.119Ω) is consistent with Dwight: rho=0.31, L=1.08, r≈0.05 →
R ≈ (0.31/2π×1.08) × (ln(4×1.08/0.05)−1) = 0.0457 × (3.46) ≈ 0.158 Ω — close to 0.119
(difference due to actual vs equivalent cylindrical radius of 189×180mm cross-section).

---

## HTML Update Plan
File: `.claude/work-queue/assets/WRK-478/implementation-review.html`
Section to replace: "Test / Eval Coverage (WRK-1026 Format)" table
New structure:
1. Brief test count summary (keep stat row)
2. Real-World Validation Cases table (3 examples with source attribution)
3. Compact functional test coverage table (condensed from 15 rows → 8 rows)

## Status
- [x] Research gathered
- [x] Hand-calculations verified
- [ ] HTML Tests section updated
