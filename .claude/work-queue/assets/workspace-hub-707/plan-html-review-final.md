# WRK-677 Final Plan HTML Review

> **Status:** FINAL — post cross-review, ready for implementation
> **Cross-review:** Codex REQUEST_CHANGES (P1/P2 resolved) | Gemini APPROVE (P2 suggestions incorporated)

---

## Changes from Draft

### Codex P1 resolved — backwards-compat rule
`metadata_version: "1"` is the single discriminator:
- Present + `"1"` → hard fail on missing required fields
- Absent or other value → WARN (legacy item, no date logic needed)

### Codex P2 resolved — template path
Documented that `.claude/work-queue/assets/WRK-656/claim-evidence-template.yaml` is the
canonical path (WRK-656 is the active governance parent item).

### Codex P2 resolved — claim-item.sh hardening
Provider defaults to `"unknown"`, blocked_by coerced to list, quota absent → `status: "unknown"`,
all fields emit deterministic placeholders.

### Gemini P2 resolved — ISO8601
Pin to `strftime("%Y-%m-%dT%H:%M:%SZ")` everywhere.

### Gemini P2 incorporated — quota unknown
`status: "unknown"` when source absent → WARN not FAIL. Only `rate-limited` / `quota-exceeded`
are hard failures.

---

## Final Deliverables

1. **`claim-evidence-template.yaml`** — 5 new fields + `claim_gate` subsection + `metadata_version`
2. **`verify-gate-evidence.py`** — `check_claim_gate()` function (~35 lines); WARN for legacy items
3. **`claim-item.sh`** — Python inline extended with session_owner, agent_fit, blocking_state, quota enrichment

## Implementation Approved ✓

confirmed_by: user
confirmed_at: 2026-03-02T10:18:00Z
decision: passed
