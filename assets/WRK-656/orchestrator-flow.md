# Canonical Orchestrator Flow & Script Suite

**Source:** WRK-675 (governance review)
**Date:** 2026-03-01
**Status:** Approved — based on WRK-669 (Claude), WRK-670 (Codex), WRK-671/672 (Gemini)

---

## Overview

This document defines the canonical `/work run` orchestrator flow and reference script suite that
Claude, Codex, and Gemini must all follow. It was derived by inventorying and comparing the three
orchestrator gate runs (WRK-669, WRK-670, WRK-671) and identifying the best-performing patterns.

See `wrk-656-orchestrator-comparison.html` for the full per-agent compliance table.

---

## Canonical 9-Stage Flow

```
Capture
  └→ Resource Intelligence   [WRK-673: evidence enforcement]
       └→ Triage
            └→ Plan           [plan gate: draft HTML → cross-review → final HTML → user approval]
                 └→ Claim
                      └→ Execute
                           └→ Review    [cross-review: Claude + Codex + Gemini via cross-review.sh]
                                └→ Close  [verify-gate-evidence.py → exit 0]
                                     └→ Archive
```

All nine stages must be traversed in order. Skipped stages require an explicit waiver with
justification recorded in the claim-evidence.yaml.

---

## Reference Script Suite

### Canonical scripts — ALL orchestrators must call these

| # | Script | Stage | Purpose |
|---|--------|-------|---------|
| 1 | `scripts/agents/session.sh init --provider <agent>` | Session start | Orchestrator lock (once per session) |
| 2 | `scripts/agents/work.sh --provider <agent> run` | Work handoff | Work orchestration handoff |
| 3 | `scripts/agents/plan.sh --provider <agent> WRK-NNN` | Plan | Plan gate (draft → cross-review → final) |
| 4 | `scripts/review/cross-review.sh <file> all` | Review | Unified cross-review entry point |
| 5 | `scripts/work-queue/verify-gate-evidence.py WRK-NNN` | Close | Gate evidence validator |
| 6 | `scripts/work-queue/log-gate-event.sh` | All | Stage event logging (YAML format) |

### Internal scripts — called BY cross-review.sh, NOT directly by orchestrators

| Script | Agent | Special handling inside cross-review.sh |
|--------|-------|-----------------------------------------|
| `scripts/review/submit-to-claude.sh` | Claude (as reviewer) | `setsid` watchdog, PGID cleanup, exit 124 = watchdog timeout |
| `scripts/review/submit-to-codex.sh` | Codex (as reviewer) | 300s timeout, INVALID_OUTPUT detection, empty-response NO_OUTPUT |
| `scripts/review/submit-to-gemini.sh` | Gemini (as reviewer) | Standard submission + INVALID_OUTPUT detection |

**Rule:** Orchestrators call `cross-review.sh <file> all`. The per-agent submit scripts are an
implementation detail of `cross-review.sh`. Calling them directly from orchestration code bypasses:
- Unified timestamped result file naming
- INVALID_OUTPUT normalisation and raw file preservation
- 2-of-3 fallback consensus when Codex returns NO_OUTPUT
- Codex HARD GATE enforcement

---

## Cross-Review Policy

`cross-review.sh all` submits to all three agents and applies these rules:

| Codex result | Fallback |
|-------------|---------|
| VALID (APPROVE / MINOR) | CODEX_PASSED=true — cross-review succeeds |
| NO_OUTPUT (empty / timeout) | 2-of-3 consensus: if Claude+Gemini both ≤MINOR → CONDITIONAL_PASS |
| INVALID_OUTPUT | Treated as NO_OUTPUT; HARD GATE warning issued |
| Explicit REJECT / MAJOR | No fallback — HARD GATE fails; must resolve before proceeding |

Codex is always the **hard gate**. The 2-of-3 consensus covers NO_OUTPUT only (typically caused by
Codex not being installed or a large-diff timeout), never an explicit rejection.

---

## Log Format Standard

All stage events must use YAML key-value format. Example:

```yaml
timestamp: 2026-03-01T14:30:00Z
wrk_id: WRK-NNN
stage: cross-review
action: finish
provider: claude
verdict: MINOR
notes: 1 MINOR finding resolved inline
```

**Non-canonical (drift):** ISO+INFO marker format observed in WRK-671 Gemini logs:
```
2026-03-02T14:30:00Z INFO Phase 2: Cross-Review Gate.
```
Future Gemini orchestrator sessions should emit YAML key-value via `log-gate-event.sh`.

---

## Deviation Table

| # | Deviation | Observed In | Classification | Resolution |
|---|-----------|-------------|---------------|-----------|
| 1 | Direct `submit-to-claude.sh` call in orchestration loop | WRK-669 (Claude) | **Drift** | Always use `cross-review.sh all` |
| 2 | Gemini ISO+INFO log format instead of YAML key-value | WRK-671 (Gemini) | **Drift** | Normalise via `log-gate-event.sh` in future Gemini runs |
| 3 | Codex `INVALID_OUTPUT` in implementation review | WRK-670 (Codex) | **Drift** | WRK-1000: Codex /work skill compatibility fix |
| 4 | Resource Intelligence stage skipped (all three runs) | WRK-669/670/671 | **Tracked** | WRK-673: RI evidence enforcement checkpoint |

---

## Follow-On Improvement Candidates

| Priority | Item | WRK | Agent | Status |
|----------|------|-----|-------|--------|
| P1 | Enforce Resource Intelligence before any orchestrator rerun | WRK-673 | Claude | Done |
| P1 | Fix Codex /work skill to avoid INVALID_OUTPUT on large diffs | WRK-1000 | Codex | Pending |
| P1 | After 10 additional runs per Claude/Codex, revisit orchestrator-flow.md to confirm canonical flow holds and update comparison HTML with extended evidence | WRK-675 (next iteration) | Claude | Pending |
| P2 | Add `log-gate-event.sh` call to Gemini orchestrator session init to normalise log format | — | Gemini | Pending |
| P2 | Document watchdog/PGID pattern in `submit-to-claude.sh` inline comments | — | Claude | Pending |
| P3 | Automate cross-review consistency check in nightly CI (compare result file format across runs) | — | — | Pending |

---

## Inventory Matrix

Scripts used by each orchestrator during WRK-669/670/671:

| Script | Claude (WRK-669) | Codex (WRK-670) | Gemini (WRK-671) | Canonical? |
|--------|:---:|:---:|:---:|:---:|
| `/work run WRK-NNN` | ✓ | ✓ | ✓ | ✓ |
| `session.sh init` | noted | noted | noted | ✓ |
| `cross-review.sh all` | partial (used for Gemini; direct call for Claude) | ✓ | ✓ | ✓ |
| `submit-to-claude.sh` (direct) | ✓ (drift) | ✗ | ✗ | ✗ internal only |
| `verify-gate-evidence.py` | ✓ (exit 0) | ✓ (exit 0) | ✓ (exit 0) | ✓ |
| `log-gate-event.sh` (YAML) | ✓ | ✓ | ✗ (ISO+INFO drift) | ✓ |
| `submit-to-gemini.sh` (via cross-review) | ✓ | ✓ | ✓ | internal |

---

*Last updated: 2026-03-01 | WRK-675 | See `wrk-656-orchestrator-comparison.html` for stage compliance detail.*
