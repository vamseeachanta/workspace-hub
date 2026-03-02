# WRK-675 Draft Plan HTML Review

> **Status:** DRAFT — awaiting human confirmation before multi-agent review
> **Date:** 2026-03-01
> **Orchestrator:** Claude

---

## Summary

WRK-675 codifies the canonical orchestrator flow and reference script suite for Claude, Codex,
and Gemini running `/work run`. Evidence base: WRK-669 (Claude), WRK-670 (Codex), WRK-671/672
(Gemini). Two deliverables:

1. `.claude/work-queue/assets/WRK-656/orchestrator-flow.md` — canonical flow doc
2. Updated `assets/WRK-656/wrk-656-orchestrator-comparison.html` — adds Script Alignment section

---

## Planned Phases

### Phase 1 — Inventory
Parse logs and assets from WRK-669/670/671. Build a matrix: orchestrator × script × usage.
Note discrepancies (log format, `submit-to-claude.sh`, Codex INVALID_OUTPUT).

### Phase 2 — Analysis
Classify each deviation as agent-specific (OK) or drift (fix needed). Define canonical 7-script
suite. Define canonical log format (YAML key-value).

### Phase 3 — Documentation
Author `orchestrator-flow.md` with 9-stage flow, script suite, deviation table, and
improvement candidates. Update comparison HTML with canonical flow and script alignment sections.

---

## Canonical Script Suite (7 scripts)

| # | Script | Required By |
|---|--------|------------|
| 1 | `scripts/agents/session.sh init` | All |
| 2 | `scripts/agents/work.sh run` | All |
| 3 | `scripts/agents/plan.sh` | All |
| 4 | `scripts/review/cross-review.sh` | All |
| 5 | `scripts/work-queue/verify-gate-evidence.py` | All |
| 6 | `scripts/work-queue/log-gate-event.sh` | All |
| 7 | `scripts/review/submit-to-gemini.sh` | When Gemini is reviewer |

Agent-specific (not drift): `submit-to-claude.sh` (Claude only, watchdog+PGID).

---

## Key Discrepancies Identified

| # | Discrepancy | Classification |
|---|-------------|---------------|
| 1 | Gemini logs use ISO+INFO format vs YAML key-value | Drift — normalise |
| 2 | `submit-to-claude.sh` only in Claude run | Agent-specific — acceptable |
| 3 | Codex INVALID_OUTPUT in implementation review | Drift — WRK-1000 follow-on |
| 4 | Resource Intelligence skipped by all three | Acceptable (sandbox baseline) |

---

## Spec Reference
`specs/wrk/WRK-675/plan.md`

---

## Human Review Confirmation

☐ **Plan looks good — proceed to multi-agent review**
