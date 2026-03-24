# WRK-675 Draft Plan HTML Review

> **Status:** DRAFT — awaiting human confirmation before multi-agent review
> **Date:** 2026-03-01
> **Orchestrator:** Claude

---

## Summary

WRK-675 codifies the canonical orchestrator flow and reference script suite for Claude, Codex,
and Gemini running `/work run`. Evidence base: WRK-669 (Claude), WRK-670 (Codex), WRK-671/672
(Gemini). Resource Intelligence stage improvement tracked separately in WRK-673.

Two deliverables:
1. `.claude/work-queue/assets/WRK-656/orchestrator-flow.md` — canonical flow doc
2. Updated `assets/WRK-656/wrk-656-orchestrator-comparison.html` — adds Canonical Flow,
   Script Alignment, and Deviation Notes sections

---

## Planned Phases

### Phase 1 — Inventory
Parse logs and assets from WRK-669/670/671. Build matrix: orchestrator × script × usage.
Note discrepancies (log format, direct `submit-to-claude.sh` call, Codex INVALID_OUTPUT,
Resource Intelligence skipped — WRK-673).

### Phase 2 — Analysis
Classify each deviation as agent-specific (OK) or drift (fix needed).
**Key finding:** `cross-review.sh all` is the canonical entry point for ALL orchestrators.
Per-agent submit scripts are internal to `cross-review.sh` — orchestrators must not call
them directly.

### Phase 3 — Documentation
Author `orchestrator-flow.md` with 9-stage flow, canonical 7-script suite, and deviation table.
Update comparison HTML with Canonical Flow + Script Alignment + Deviation Notes.

---

## Cross-Review Script — Key Alignment Point

`cross-review.sh all` handles:
- Claude: `submit-to-claude.sh` with setsid watchdog + PGID cleanup
- Codex: `submit-to-codex.sh` with timeout + INVALID_OUTPUT detection
- Gemini: `submit-to-gemini.sh`
- Fallback: 2-of-3 consensus when Codex returns NO_OUTPUT

**All orchestrators should call `cross-review.sh all`, not individual submit scripts.**
This is the central consistency fix WRK-675 establishes.

---

## Canonical Script Suite (7 entries)

| # | Script | Required By |
|---|--------|------------|
| 1 | `scripts/agents/session.sh init` | All |
| 2 | `scripts/agents/work.sh run` | All |
| 3 | `scripts/agents/plan.sh` | All |
| 4 | `scripts/review/cross-review.sh all` | All (unified entry point) |
| 5 | `scripts/work-queue/verify-gate-evidence.py` | All |
| 6 | `scripts/work-queue/log-gate-event.sh` | All (YAML format) |
| 7 | `scripts/review/submit-to-gemini.sh` | Internal to cross-review.sh |

---

## Deviation Table

| # | Deviation | In | Class | Fix |
|---|-----------|-----|-------|-----|
| 1 | Direct `submit-to-claude.sh` in orchestration | WRK-669 | Drift | Use `cross-review.sh all` |
| 2 | Gemini ISO+INFO log format | WRK-671 | Drift | Normalise to YAML key-value |
| 3 | Codex INVALID_OUTPUT in impl review | WRK-670 | Drift | WRK-1000 follow-on |
| 4 | Resource Intelligence skipped | All | Tracked | WRK-673 |

---

## Spec Reference
`specs/wrk/WRK-675/plan.md`

---

## Human Review Confirmation

☐ **Plan looks good — proceed to multi-agent review and implementation**
