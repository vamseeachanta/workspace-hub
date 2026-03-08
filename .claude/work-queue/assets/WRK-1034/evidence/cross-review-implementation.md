# WRK-1034 Implementation Cross-Review

**Stage**: 13 — Agent Cross-Review (Implementation)
**Date**: 2026-03-08
**Reviewer**: Codex (via feature-dev:code-reviewer agent)
**Verdict**: APPROVE (round 2)

## Round 1 — REJECT

Reviewed: `verify-gate-evidence.py` (new Stage 7/17 gate functions), `stage7-gate-config.yaml`,
`stage17-gate-config.yaml`, `claim-item.sh` guard block, `close-item.sh` guard block,
`tests/unit/test_verify_gate_evidence.py` (T1–T17).

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| P1-01 | P1 | Fail-open allowlist guard — `if human_allowlist` evaluates to False when allowlist is empty, allowing any identity to pass the human check. Affects `check_stage7_evidence_gate`, `check_stage17_evidence_gate`, and `_validate_exemption`. |
| P2-01 | P2 | `emergency_bypass_*` fields declared in both gate configs but never implemented in Python logic; misleading schema that suggests an unimplemented escape hatch. |
| P2-03 | P2 | T14/T15/T16 call predicate functions directly; `_run_stage7_check`/`_run_stage17_check` exit-code mapping (True→0, False→1, None→2) was untested. |
| P3-01 | P3 | `exemption_ref` field not validated against real WRK archive. |
| P3-02 | P3 | `confirmed_at` not validated as ISO-8601; `0` or `false` would pass the non-empty check. |

## Round 2 — APPROVE

### Fixes Applied

**P1-01**: Inverted `if human_allowlist and x not in human_allowlist` to fail-closed in all 3 locations:
- `_validate_exemption`: returns `(None, "...empty — gate cannot validate...")` when allowlist is empty
- `check_stage7_evidence_gate`: returns `(False, "...empty...")` before identity check
- `check_stage17_evidence_gate`: returns `(False, "...empty...")` before identity check

**P2-01**: Removed `emergency_bypass_until`, `emergency_bypass_reason`, `emergency_bypass_approved_by`
from both `stage7-gate-config.yaml` and `stage17-gate-config.yaml`.

**P2-03**: Added T18 (`test_run_stage7_check_exit_code_mapping`) and T19 (`test_run_stage17_check_exit_code_mapping`) — each tests all 3 exit-code branches using `unittest.mock.patch.object` on the gate function and `pathlib.Path.is_dir`.

### Test Results After Fixes

```
55 passed in 0.59s
```

### Remaining Minor Items (P3 — accepted, not blocking)

- **P3-01**: `exemption_ref` validation deferred (added to future-work fw-03 scope)
- **P3-02**: Timestamp format validation deferred (human-authored files; low practical risk)
