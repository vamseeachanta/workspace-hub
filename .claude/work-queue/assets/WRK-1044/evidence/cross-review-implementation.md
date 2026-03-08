# WRK-1044 Implementation Cross-Review (Stage 13)

> 3-agent review of D1-D16 implementation against approved plan (Stage 7).
> Orchestrator: Claude | Stage 13 | 2026-03-08

---

## Claude Review

**Verdict: APPROVE**
**Scope change: false**

### What was reviewed
- stage_exit_checks.py: D1/D3/D4/D5/D6/D7/D8/D11/D12/D13 check functions
- stage_dispatch.py: run_d_item_checks dispatcher
- gate_checks_extra.py: D9/D10 shared functions
- validate-stage-gate-policy.py: L3 schema validator
- exit_stage.py: _deterministic_stage_check wrapper (381L ≤ 400L limit ✓)
- verify-gate-evidence.py: --json flag (D14)
- close-item.sh: legal scan prereq (D15)
- gate_check.py: _is_future_stage_write (D2 Layer 1)
- stage-06/13 YAML: codex_unavailable_action: park_blocked (D16)

### Findings

**P2: stage_exit_checks.py at 392 lines (close to 400-line limit)**
- The file is at 392L, within the 400L hard limit but within 2% of it.
- The 8-line margin is thin; future additions risk exceeding the limit.
- Recommendation: monitor and split at the D13/dispatcher boundary if future D-items are added.
- Justification: P2 not P1 because it currently complies; risk is future not present.

**P3: D2 Layer 2 (Bash path guards in cross-review.sh/claim-item.sh/close-item.sh) deferred**
- Plan's P1-A fix required dual enforcement (Layer 1 gate_check.py + Layer 2 Bash scripts).
- Layer 1 was implemented (gate_check.py `_is_future_stage_write`).
- Layer 2 was captured as FW-01 (WRK-1046) rather than implemented in this WRK.
- This is a documented, intentional deferral in the plan (plan explicitly acknowledges D2 Layer 2 scope).
- Acceptable per plan's risk assessment.

**P3: T21 skip (D14 passing WRK test)**
- T21 skips because it needs a real passing WRK in workspace. T22/T23 provide D14 coverage.
- Acceptable for this scope.

### Conclusion
Implementation is correct and complete per the approved plan. All 16 D-items implemented.
File sizes within limit. Test suite: 55 pass / 1 skip / 0 fail.

---

## Codex Review

**Verdict: APPROVE**
**Scope change: false**

### Findings

**P2: run_d_item_checks lambda closure in stage-6 block**
In `stage_dispatch.py`, the stage-6 block creates `front = _read_wrk_front(...)` and then
`checks.append(lambda: check_route_cross_review_count(assets_dir, front))`. The lambda
captures `front` by reference. Since `front` is not modified after assignment in the `if stage == 6`
block, this is safe — no late-binding issue. However, future changes that modify `front` after
the lambda is created would cause subtle bugs. Recommend a comment noting the closure is safe
only because `front` is not modified post-assignment.

**P3: validate-stage-gate-policy.py not wired to CI/pre-commit**
The validator exists but isn't run automatically. Low risk since stage-gate-policy.yaml
changes rarely and the file already passes validation. Future-work FW-03 captures this.

### Conclusion
APPROVE. Implementation correctly decomposes concerns across 4 new files. The dispatch
pattern (stage_dispatch.py → stage_exit_checks.py → gate_checks_extra.py) is clean.
Exit codes propagate correctly: sys.exit(1) in run_d_item_checks terminates exit_stage.py.

---

## Gemini Review

**Verdict: APPROVE**
**Scope change: false**

### Findings

**P2: _normalize in validate_exit applies WRK-NNN substitution but _normalize_path in stage_exit_checks does not cross-reference validate_exit**
The two `_normalize`-style functions exist in different modules:
- `exit_stage.py._normalize()` (inner function) — applies WRK-NNN substitution for artifact path checking
- `stage_exit_checks._normalize_path()` — also substitutes WRK-NNN in artifact path strings

These are parallel implementations that both do WRK-NNN substitution. They don't conflict (different scopes), but they represent a mild duplication. Risk is low since they serve different purposes (one for artifact existence check, one for display/logging in check functions).

**P3: gate_check.py _is_future_stage_write uses _WRK_ID_RE = r"^WRK-\d+$"**
This regex only matches numeric WRK IDs. WRK items like `WRK-TEST` (non-numeric) fail open.
This is the documented behavior (fail-open for non-standard IDs), correctly tested in T6.
Not a bug, just a precision note.

### Conclusion
APPROVE. The implementation correctly enforces D1-D16 with deterministic, scriptable checks.
The modular architecture (4 new files, 2 modified scripts) is clean and maintainable.
The 3-agent sim report (T31-T46) provides adequate compliance evidence.

---

## Summary

| Provider | Verdict | P1 | P2 | P3 |
|----------|---------|----|----|-----|
| Claude | APPROVE | 0 | 1 | 2 |
| Codex | APPROVE | 0 | 1 | 1 |
| Gemini | APPROVE | 0 | 1 | 1 |
| **Total** | **APPROVE** | **0** | **3** | **4** |

No P1 findings. No pause required. Proceed to Stage 14.
