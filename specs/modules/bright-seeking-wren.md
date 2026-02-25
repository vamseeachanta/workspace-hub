# Plan: WRK-607 — DNV RP F105 Free-Spanning Pipeline VIV Module

## Context

WRK-607 implements `digitalmodel.subsea.pipeline.free_span` — the DNV RP F105
free-spanning pipeline VIV assessment. This module is a prerequisite for WRK-045
Phase 4 (rigid jumper VIV screening) and unlocks ledger status `done` for WRK-528.

A `viv_analysis` module already exists at `subsea/viv_analysis/` covering general
tubular-member VIV (generic beam theory, lock-in screening). However it lacks:
- F105 stability parameter Ks and IL/CF onset criteria
- F105 effective-mass formula (Section 6.8) with correction factor Ce
- In-line vs cross-flow response amplitude curves (Section 6.4)
- Allowable free-span length (Section 4 Level 1 simplified)
- Integrated F105 fatigue via DNV-RP-C203 F-class (already in structural.fatigue)

## Existing Infrastructure to Reuse

| Reuse | Source path |
|-------|-------------|
| `BoundaryCondition`, `TubularMember`, `MaterialProperties`, `FluidProperties` | `subsea/viv_analysis/models.py` |
| `get_dnv_curve('F')`, `PowerLawSNCurve` | `structural/fatigue/sn_curves.py` |
| `LinearDamageAccumulation` | `structural/fatigue/damage_accumulation.py` |

## Module Location

**Source**: `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/`
(matches existing `subsea/pipeline/` layout — NOT `pipeline/free_span/` as WRK spec says)

**Tests**: `digitalmodel/tests/subsea/pipeline/test_free_span_f105.py`

## Files to Create

```
src/digitalmodel/subsea/pipeline/free_span/
├── __init__.py                    # public API + FreespanVIVFatigue facade
├── models.py                      # PipeSpanInput / SpanVIVResult dataclasses
├── span_natural_frequency.py      # F105 Sec 6.8: natural frequency (IL + CF)
├── span_onset_screening.py        # F105 Sec 4.3/4.4: IL/CF onset + Ks screening
├── span_viv_response.py           # F105 Sec 4.3/4.4: IL + CF amplitude model
├── span_fatigue_damage.py         # F105 Sec 7.3 + DNV-RP-C203: Miner damage
└── span_allowable_length.py       # F105 Sec 4.2 Level 1: max span length
```

**Class names** (meaningful, not generic):
- `SpanNaturalFrequency` — calculates fn_IL, fn_CF per F105 Sec 6.8
- `SpanOnsetScreening` — IL/CF screening criteria, Ks, `is_viv_susceptible()`
- `SpanVIVAmplitude` — piecewise response model, `il_amplitude_over_D()`, `cf_amplitude_over_D()`
- `SpanFatigueDamage` — Miner sum over current distribution, `damage_per_year()`, `fatigue_life_years()`
- `SpanAllowableLength` — Level 1 span length check, `max_span_m()`
- `FreespanVIVFatigue` — top-level orchestrator mirroring MATLAB tool structure

## Key Formulas (F105 per TwoHSpanVIV reference code)

Reference MATLAB implementation at:
`/mnt/remote/ace-linux-2/dde/Personal/FreeSpanVIVFatigue/` (13 files).
Port algorithm logic directly. Strip all proprietary identifiers — run
`scripts/legal/legal-sanity-scan.sh digitalmodel/` before any commit.

```
# natural_frequency.py — F105 Section 6.8
C1 = {pinned-pinned: 9.87, fixed-fixed: 22.4, fixed-pinned: 15.42}
m_e = m_pipe + m_content + m_added    # effective mass/unit length
f_n = C1 / (L² * sqrt(m_e / EI)) * sqrt(1 + Ce * (delta/D)²)
  Ce ≈ 0.4 (pinned-pinned), 0.2 (fixed-fixed), delta = sag (typically 0)
m_added = Ca * rho_w * pi/4 * D²     # added mass, Ca=1.0 (circular)

# onset_criteria.py — F105 Sec 4.3.5 (IL) and Sec 4.4.6 (CF)
Ks = inlineStabilityFactor / gamma_k  # stability parameter (given or computed)
  where inlineStabilityFactor = 4*pi*m_e*zeta_T / (rho_w * D²)

# IL onset: piecewise (Sec 4.3.5, Fig 4-2)
Ur_onset_IL = 0.6 + Ks               (when 0.4 ≤ Ks ≤ 1.6)
            = 1.0                     (when Ks < 0.4)
            = 2.2                     (when Ks > 1.6)
Apply safety: Ur_effective = Ur_onset_IL / gamma_on_IL

# CF onset: seabed proximity correction (Sec 4.4.6)
psi_prox = 0.2 * (4 + 1.25 * e/D)    (when e/D < 0.8, e = gap to seabed)
         = 1.0                        (when e/D ≥ 0.8)
Ur_onset_CF = 3.0 * psi_prox / gamma_on_CF

Ur = (Uc + Uw) / (f_n * D)           # reduced velocity with wave contribution
il_viv_onset = Ur >= Ur_onset_IL
cf_viv_onset = Ur >= Ur_onset_CF

# viv_response.py — IL amplitude model (F105 Sec 4.3.4, Fig 4-2)
A2_IL = 0.13 * (1 - Ks/1.8)         # lower plateau
A1_IL = max(0.18 * (1 - Ks/1.2), A2_IL)  # peak amplitude
Vr1 = Ur_onset_IL + 10 * A1_IL
Vr2 = (3.7 if Ks ≥ 1 else 4.5 - 0.8*Ks) - 2*A2_IL
Vr_end = 3.7 if Ks ≥ 1 else 4.5 - 0.8*Ks
# Piecewise linear interpolation over [Ur_onset, Vr1, Vr2, Vr_end]

# CF amplitude model (F105 Sec 4.4.4)
Rk = max(1 - 0.15*Ks, 0)             # CF damping reduction (Ks ≤ 4)
# For current-dominated (alpha > 0.8):
A1_CF = 0.9   (f_CF2/f_CF1 < 1.5) | 1.3 (>2.3) | interpolated between
# Wave-dominated (alpha ≤ 0.8):
A1_CF = 0.7 (KC<10) | 0.9 (KC>30) | 0.7 + 0.01*(KC-10) (10-30)
# CF amplitude curve: [Vr=2 → Vr_onset → Vr1 → Vr2 → Vr_end=16]
#                     [0    → 0.15    → A1  → A2  → 0]

# Stress from amplitude (from ANSYS modal stress at keypoints)
# For simplified span (beam), stress = A/D * CorrectionFactor * mode_stress_normalized
# CorrectionFactor = 2 * gamma_s * D

# fatigue.py — Palmgren-Miner (F105 Sec 7.3 + DNV-RP-C203)
# Two-slope S-N: N = C1 * S^(-m1) for S ≥ S_trans
#                N = C2 * S^(-m2) for S < S_trans
# D_per_year = f_n * 3.16e7 / N(S) * P(Uc)    (weighted by current probability)
# Use structural.fatigue.sn_curves.get_dnv_curve('F') for C1/m1 parameters

# span_length.py — Level 1 static simplified (F105 Sec 4.2)
# L_max ≤ D * (delta_allow/D * EI / W_sub)^0.25  (beam deflection limit)
# delta_allow = 0.0225 * D (static deflection limit per DNV)
```

## Implementation Order (TDD)

1. **Write tests first** (`test_free_span_f105.py`) — failing tests for all 5 modules
2. **`models.py`** — `FreespanInput`, `FreespanResult` dataclasses
3. **`span_natural_frequency.py`** — `SpanNaturalFrequency` class, `fn_IL()` / `fn_CF()`
4. **`span_onset_screening.py`** — `SpanOnsetScreening` class, `stability_parameter()`, `il_onset_velocity()`, `screening_flags()`
5. **`span_viv_response.py`** — `SpanVIVAmplitude` class, `il_amplitude_over_D()`, `cf_amplitude_over_D()`
6. **`span_fatigue_damage.py`** — `SpanFatigueDamage` class, `damage_per_year()`, `fatigue_life_years()`
7. **`span_allowable_length.py`** — `SpanAllowableLength` class, `max_span_m()`
8. **`__init__.py`** — `FreespanVIVFatigue` facade + `assess()` returning `FreespanResult`

## Test Coverage

Tests assert:
- `natural_frequency`: fn_IL ≈ 0.42 Hz, fn_CF ≈ 0.38 Hz for reference case (±10%)
- `onset_criteria`: Ks > 0, Ur_onset_IL = 1.0 + 0.4/Ks, onset flag for reference case
- `viv_response`: amplitude = 0 when below onset; amplitude > 0 when above
- `fatigue`: fatigue life > 0 years; infinite life when stress below S-N limit
- `span_length`: allowable span < 50 m for 10" pipe at 100 m depth
- `F105FreespanAssessment.assess()`: round-trip with WRK-607 example inputs

## Files Modified (existing)

None — new module only. The `subsea/pipeline/__init__.py` will NOT be touched
(free_span is a new sub-package; it does not break existing exports).

## Legal / Compliance

All formulas taken from DNV RP F105 (industry standard — public).
No client identifiers. Run `scripts/legal/legal-sanity-scan.sh digitalmodel/` after implementation.

## Verification

```bash
cd digitalmodel
PYTHONPATH=src python3 -m pytest tests/subsea/pipeline/test_free_span_f105.py -v
```

Expected: all tests green, no import errors.
