---
name: orcawave-aqwa-benchmark-convention-differences
description: 'Sub-skill of orcawave-aqwa-benchmark: Convention Differences (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Convention Differences (+3)

## Convention Differences


- **AQWA**: ISO 6954 (phase lead) — `A * cos(wt + phi)`
- **OrcaWave**: Orcina (phase lag) — `A * cos(wt - phi)`
- **Conversion**: `phi_Orcina = -phi_ISO` (negate AQWA phases)

## Implementation


Normalize at extraction time, not at comparison time. Use Orcina (phase lag) as the canonical convention:
```python
# In AQWA extraction, after building each RAOComponent:
component.phase = -component.phase  # ISO 6954 → Orcina lag
results.phase_convention = "orcina_lag"
```

Track convention metadata on `DiffractionResults`:
```python
phase_convention: str = "unknown"  # "orcina_lag" or "iso_lead"
unit_system: str = "SI"            # "SI" (kg,m,s) or "orcaflex" (te,m,s)
```

## M24/M42 Sway-Roll Coupling Sign Fix


AQWA sway-roll coupling terms (M24/M42) have opposite sign to OrcaWave. Empirically determined from barge geometry; needs AQWA Theory Manual Section 4.3 confirmation.

```python
# Negate Sway-Roll coupling in AQWA extraction
# Added mass AND damping matrices
matrix[1, 3] = -matrix[1, 3]  # M24
matrix[3, 1] = -matrix[3, 1]  # M42
```

**Scope**: Only M24/M42 — other roll-coupling terms (M14, M34, M46) are near-zero for typical barge geometries and cannot be verified.

## Unit System


- AQWA: SI (kg, m, s)
- OrcaWave: OrcaFlex (te, m, s) — factor ~1000x
- Pearson correlation is scale-invariant, so units don't affect correlation-based comparison
- Track in metadata for absolute value comparisons
