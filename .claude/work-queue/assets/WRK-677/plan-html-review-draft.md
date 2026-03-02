# WRK-677 Draft Plan HTML Review

> **Status:** DRAFT — awaiting human confirmation before multi-agent review
> **Date:** 2026-03-02
> **Orchestrator:** Claude

---

## Summary

WRK-677 hardens the claim gate by filling 5 missing metadata fields in `claim-evidence.yaml`
and adding an entirely absent claim gate check to `verify-gate-evidence.py`.

---

## Gap: 5 missing fields + no verifier check

| Field | Missing from | Fix |
|-------|-------------|-----|
| `session_owner` | template + `claim-item.sh` | Extract from frontmatter `provider` |
| `agent_fit` | template + `claim-item.sh` | Build from `route`/`computer`/`execution_workstations` |
| `quota_snapshot.timestamp` | template + `claim-item.sh` | `datetime.now(UTC).isoformat()` |
| `quota_snapshot.pct_remaining` | template + `claim-item.sh` | Parse `agent-quota-latest.json` |
| `blocking_state` | template + `claim-item.sh` | Extract from frontmatter `blocked_by` |
| Claim gate in verifier | `verify-gate-evidence.py` | New gate check (WARN for old items) |

---

## Three Deliverables

### 1. Template update (`claim-evidence-template.yaml`)
Add `session_owner`, `agent_fit`, `blocking_state`, and enriched `quota_snapshot` schema.
Add `claim_gate` subsection to `gate_evidence`.

### 2. Verifier claim gate (`verify-gate-evidence.py`)
New `claim_gate` check (~30 lines):
- Absent `claim-evidence.yaml` → WARN (backwards compat for old items)
- `session_owner` missing → FAIL
- `quota_snapshot.status` not `available` → FAIL
- `blocking_state.blocked == true` → FAIL

### 3. claim-item.sh enrichment
Python inline block extended (~20 lines) to emit all 5 new fields automatically.

---

## Backwards Compatibility

Items before WRK-677 with no `claim-evidence.yaml` get a WARN, not a hard failure.
`quota_snapshot.pct_remaining = null` for Claude is handled gracefully.

---

## Spec Reference
`specs/wrk/WRK-677/plan.md`

---

## Human Review Confirmation

☐ **Plan looks good — proceed to multi-agent review and implementation**
