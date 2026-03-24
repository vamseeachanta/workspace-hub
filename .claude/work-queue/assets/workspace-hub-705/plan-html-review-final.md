# WRK-675 Final Plan HTML Review

> **Status:** FINAL — post cross-review, ready for implementation
> **Date:** 2026-03-01
> **Cross-review verdicts:** Codex REQUEST_CHANGES (P1/P2 addressed) | Gemini REQUEST_CHANGES (P1/P2 addressed)

---

## Changes from Draft

### Codex findings resolved
- **P1 (Critical):** Stage count corrected — canonical flow is 9 stages:
  `Capture → Resource Intelligence → Triage → Plan → Claim → Execute → **Review** → Close → Archive`
- **P2 (paths):** `orchestrator-flow.md` moved from `.claude/work-queue/assets/WRK-656/` to
  `assets/WRK-656/` (repo root, same directory as comparison HTML). Accessible to all agents.
- **P2 (scripts):** Script suite table now shows all three internal submit scripts with their
  specific handling (watchdog/PGID for Claude, 300s timeout + INVALID_OUTPUT for Codex,
  standard + INVALID_OUTPUT for Gemini).
- **P2 (dependencies):** WRK-673 and WRK-1000 explicitly marked as informational/non-blocking.

### Gemini findings resolved
- **P1 (Target ID):** Clarification added — WRK-656 paths are intentional (parent governance
  item). WRK-675 assets live in `.claude/work-queue/assets/WRK-675/`.
- **P2 (agent-neutral path):** `orchestrator-flow.md` now at `assets/WRK-656/` (root), not
  under `.claude/` hidden directory.
- **P3 (Phase 1 sources):** Input sources now explicitly listed (logs + review-input.md +
  variation-test-results.md + summary HTMLs).

---

## Final Plan Summary

**Deliverables:**
1. `assets/WRK-656/orchestrator-flow.md` — canonical 9-stage flow, 6-script suite (+3 internal), 4-deviation table
2. `assets/WRK-656/wrk-656-orchestrator-comparison.html` — updated with Canonical Flow, Script Alignment, Deviation Notes sections

**Central alignment finding:**
`cross-review.sh all` is the single canonical cross-review entry point for ALL orchestrators.
Direct per-agent script calls from orchestration code = drift.

**Deviation table (4 entries):**
1. `submit-to-claude.sh` direct call in WRK-669 → Drift → use `cross-review.sh all`
2. Gemini ISO+INFO log format → Drift → normalise to YAML key-value
3. Codex INVALID_OUTPUT in impl review → Drift → WRK-1000
4. Resource Intelligence skipped → tracked → WRK-673

---

## Spec Reference
`specs/wrk/WRK-675/plan.md`

---

## Implementation Approved ✓
