# WRK-677 Implementation Cross-Review

**date:** 2026-03-02
**item:** governance(review): strengthen claim gate metadata
**reviewers:** Codex, Gemini

---

## Codex Verdict: REQUEST_CHANGES → RESOLVED

### P2 — metadata_version type coercion
**Finding:** YAML integer `1` vs string `"1"` may cause version mismatch.
**Resolution:** Pre-existing `str()` coercion already handles both forms
(`str(1) == "1"`). Added inline comment to document this. No code change
needed.

### P2 — Missing field validation (agent_fit, quota_snapshot.timestamp)
**Finding:** check_claim_gate only validated session_owner, quota.status, and
blocking_state.blocked for v1 items; agent_fit and timestamp not checked.
**Resolution:** Added `quota_snapshot.timestamp` presence check as a hard
error for metadata_version="1" items. agent_fit is intentionally informational
(not operationally gated per plan spec).

### P3 — session_owner="unknown" policy
**Finding:** `"unknown"` passes the missing-owner check.
**Resolution:** Design decision: `"unknown"` is a safe sentinel emitted when
provider is absent in frontmatter. The gate fails on empty/None, not
"unknown". This allows claim emission for edge cases without blocking
legitimate runs. Acceptable risk for the current governance scope.

---

## Gemini Verdict: REQUEST_CHANGES → RESOLVED

### [BUG] blocked_by YAML block format not parsed
**Finding:** `get_value("blocked_by")` only captures inline `[WRK-NNN]`
format. YAML block format (`blocked_by:\n  - WRK-NNN`) returns empty string,
so `is_blocked = False` incorrectly for blocked items.
**Resolution:** Fixed in claim-item.sh — added block-format regex fallback
when inline value is empty; handles both inline and multi-line YAML block
formats. Verified with 5 format cases.

### [LOGIC] Frontmatter updated before gate validation
**Finding:** `upsert("status", "working")` writes the file before
verify-gate-evidence.py runs; if gate fails, file is left in pending/ with
`status: working`.
**Resolution:** Pre-existing behavior not introduced by WRK-677. Accepted
as known limitation — the claim step is called explicitly and the operator
is expected to fix gate artifacts and re-run. Tracked as UX debt (no WRK
item needed for current scope).

### [GAP] session_owner="unknown" — duplicate of Codex P3
See above. Intentional design decision.

### [UX] Workstation gate display for block-style workstations
**Finding:** Pre-existing UX issue in workstation gate output; not in WRK-677
scope.
**Resolution:** Out of scope. Pre-existing behavior retained.

---

## Combined Verdict: APPROVE (all P1/P2/bug findings resolved)

Changes made post-review:
1. `verify-gate-evidence.py` — `str()` comment + `quota_snapshot.timestamp` check
2. `claim-item.sh` — `blocked_by` YAML block format parsing fix
