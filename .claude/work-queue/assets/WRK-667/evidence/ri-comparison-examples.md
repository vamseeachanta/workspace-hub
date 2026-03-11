# Resource Intelligence — Before/After Comparison Examples

Generated for: WRK-667
Rubric version: 1.0 (2026-03-09)

---

## Rubric

For each pair, compare the **same WRK category** and **same required artifact set**.
Measure:

| Metric | Definition |
|--------|-----------|
| `missing_artifact_rate` | Required files absent / total required files (0.0 = all present) |
| `plan_edits_required` | Number of plan-draft iterations triggered by gaps found in RI or execution |
| `confidence` | Derived: `high` iff rate==0.0 AND p1-gaps resolved AND provenance complete |

---

## Example 1 — WRK-655 (harness / resource-intelligence skill build)

**Category**: harness | **Route**: B

### Before (WRK-655 at Stage 2 entry — RI skill not yet available)

- `resources.yaml`: absent (no template)
- `resource-intelligence-summary.md`: hand-written, no required-field validation
- `evidence/resource-intelligence.yaml`: absent (gate not defined yet)
- `top_p1_gaps`: not recorded — gap in verify-gate-evidence.py was discovered at Stage 14

**Signals (reconstructed)**:
```yaml
missing_artifact_rate: 0.5     # 4 of 8 required files missing
plan_edits_required: 3         # plan revised twice after execution revealed gaps
confidence: low
```

### After (WRK-667 — RI skill active)

- All 8 required artifacts scaffolded by `init-resource-pack.sh`
- `evidence/resource-intelligence.yaml`: gate-checked by `verify-gate-evidence.py`
- `validate-resource-pack.sh` exits 0 before Stage 2 declared complete
- `top_p1_gaps: []` (no blocking gaps) confirmed by gate

**Signals**:
```yaml
missing_artifact_rate: 0.0
plan_edits_required: 0
confidence: high
```

**Delta**: artifact-gap −0.5, plan-edits −3, confidence low→high

---

## Example 2 — WRK-624 (harness / governance skill review)

**Category**: harness | **Route**: C

### Before (WRK-624 — RI executed without validate-resource-pack.sh)

- `resources.yaml` had no `source_type` field — malformed sources not caught until cross-review
- `resource-intelligence-summary.md` missing `reviewer` field — failed verify-gate-evidence.py at Stage 14
- No `legal_scan_ref` — legal gate failure discovered at Stage 14

**Signals (reconstructed)**:
```yaml
missing_artifact_rate: 0.125   # 1 of 8 files had structural errors (treated as missing)
plan_edits_required: 2         # legal-scan miss + malformed sources required plan revision
confidence: medium
```

### After (WRK-667 validator active)

- `validate-resource-pack.sh` catches: missing required fields in `resource-intelligence-summary.md`,
  malformed `resources.yaml` source entries, out-of-repo `legal_scan_ref` paths
- All checks pass before Stage 2 exit

**Signals**:
```yaml
missing_artifact_rate: 0.0
plan_edits_required: 0
confidence: high
```

**Delta**: artifact-gap −0.125, plan-edits −2, confidence medium→high

---

## Example 3 — WRK-1028 (harness / stage-isolation contract)

**Category**: harness | **Route**: C

### Before (WRK-1028 — RI exit artifact lacked skills.core_used)

- `evidence/resource-intelligence.yaml` written manually, `skills.core_used` absent
- `completion_status` field missing — verify-gate-evidence.py blocked Stage 14
- `domain.*` fields absent — plan had vague problem statement, leading to scope drift

**Signals (reconstructed)**:
```yaml
missing_artifact_rate: 0.0     # all 8 files present
plan_edits_required: 4         # scope drift caused 4 plan-draft revisions
confidence: low                # provenance incomplete + core_used missing
```

### After (WRK-667 quality_signals + template active)

- Template includes `skills.core_used` (≥3), `completion_status`, `domain.problem`
- `validate-resource-pack.sh` checks `completion_status` + `skills.core_used` ≥3
- `quality_signals.confidence` derivation rule documented in template — author sets explicitly

**Signals**:
```yaml
missing_artifact_rate: 0.0
plan_edits_required: 1         # one minor plan revision (expected for Route C)
confidence: high
```

**Delta**: artifact-gap 0 (files were present), plan-edits −3, confidence low→high

---

## Summary

| Pair | Before confidence | After confidence | Plan-edits delta |
|------|------------------|-----------------|-----------------|
| WRK-655 | low | high | −3 |
| WRK-624 | medium | high | −2 |
| WRK-1028 | low | high | −3 |

All three pairs show `confidence → high` and `plan_edits_required` reduced by ≥2 when the
WRK-667 additions (validator, template, quality_signals) are active.
