# WRK-675 Plan: governance(review) — align orchestrator flow & scripts

**Source WRK:** WRK-675
**Route:** C (complex)
**Created:** 2026-03-01
**Status:** final (post-cross-review)

---

## Objective

Codify the canonical `/work run` orchestrator flow and reference script suite that Claude, Codex,
and Gemini must all follow, based on evidence from WRK-669 (Claude), WRK-670 (Codex), and
WRK-671/672 (Gemini). Produce two deliverables under `assets/WRK-656/` (the parent governance
item).

Note: Resource Intelligence evidence is tracked in WRK-673 (informational, non-blocking).
Codex /work skill fix is tracked in WRK-1000 (informational, non-blocking).

---

## Clarification — WRK-656 vs WRK-675 paths

`WRK-656` is the **parent governance item** for the orchestrator comparison. Its asset directory
(`assets/WRK-656/`) already contains `wrk-656-orchestrator-comparison.html`. Both deliverables for
WRK-675 are contributions TO that parent item's asset set — they live in `assets/WRK-656/`, not
in `assets/WRK-675/`. WRK-675 assets (`plan.md`, gate evidence) live in the normal WRK-675 asset
locations. This is intentional, not a confusion.

---

## Phase 1 — Inventory (data-collection)

**Input sources:**
- `WRK-669-*.log`, `WRK-670-*.log`, `WRK-671-*.log`
- `assets/WRK-669/review-input.md`, `assets/WRK-670/review-input.md`
- `assets/WRK-669/variation-test-results.md`, `assets/WRK-671/variation-test-results.md`
- Summary HTML files for each orchestrator run

**Tasks:**
- Build matrix: orchestrator × script × usage (present/absent/variant).
- Note log format divergence: Claude/Codex YAML key-value vs Gemini ISO+INFO markers.
- Note direct `submit-to-claude.sh` invocation in WRK-669 vs `cross-review.sh all` in WRK-670/671.
- Note Codex INVALID_OUTPUT in WRK-670 implementation review (follow-on: WRK-1000).
- Note Resource Intelligence skipped by all three — WRK-673.

**Acceptance:** Inventory matrix table complete; all 4 deviations enumerated.

---

## Phase 2 — Analysis

**Key finding — cross-review script:**
`cross-review.sh all` is the canonical cross-review entry point for ALL orchestrators. It calls
the per-agent submit scripts internally:

| Internal call | Handles |
|---------------|---------|
| `submit-to-claude.sh` | setsid watchdog, PGID cleanup, watchdog timeout exit 124 |
| `submit-to-codex.sh` | 300s timeout, INVALID_OUTPUT detection, NO_OUTPUT fallback |
| `submit-to-gemini.sh` | standard submission, INVALID_OUTPUT detection |

Fallback: 2-of-3 consensus when Codex returns NO_OUTPUT (Claude+Gemini both APPROVE or MINOR).
Codex remains HARD GATE — fallback only on NO_OUTPUT, never on explicit REJECT/MAJOR.

**Drift:** WRK-669 called `submit-to-claude.sh` directly in the orchestration loop instead of
routing through `cross-review.sh all`. This bypassed the unified result file naming, INVALID_OUTPUT
normalisation, and 2-of-3 fallback logic. All orchestrators must use `cross-review.sh all`.

**Log format standard:** YAML key-value (`timestamp/wrk_id/stage/action/provider/notes`).
Gemini ISO+INFO style is drift — normalise in future Gemini orchestrator sessions.

**WRK-673 / WRK-1000:** informational, non-blocking for WRK-675 completion.

**Acceptance:** Deviation table complete, canonical flow text drafted.

---

## Phase 3 — Documentation

**Deliverable 1:** `assets/WRK-656/orchestrator-flow.md`
- Canonical 9-stage flow: Capture → Resource Intelligence → Triage → Plan → Claim → Execute →
  Review → Close → Archive.
- Reference script suite table (full, including internal submit scripts).
- Deviation table (4 entries).
- Follow-on improvement candidates.
- Note: placed in `assets/WRK-656/` (root, not `.claude/`) so it is accessible to all agents
  (Claude, Codex, Gemini) without agent-specific path resolution.
- Cross-reference WRK-673 for Resource Intelligence stage evidence.

**Deliverable 2:** `assets/WRK-656/wrk-656-orchestrator-comparison.html`
- Add "Canonical Flow" section with link to `orchestrator-flow.md`.
- Add "Script Alignment" table (per-agent vs canonical).
- Add "Deviation Notes" section: log-format normalisation; RI tracking via WRK-673.
- Add "Cross-Review Consistency" note: `cross-review.sh all` mandate.

**Acceptance:** Both files exist, cross-reference each other, validator passes on WRK-675.

---

## Canonical Reference Script Suite

| # | Script | Required By | Notes |
|---|--------|------------|-------|
| 1 | `scripts/agents/session.sh init` | All | Once per session |
| 2 | `scripts/agents/work.sh run` | All | Work handoff |
| 3 | `scripts/agents/plan.sh` | All | Plan gate |
| 4 | `scripts/review/cross-review.sh all` | All | Unified cross-review entry |
| 5 | `scripts/work-queue/verify-gate-evidence.py` | All | Gate validator |
| 6 | `scripts/work-queue/log-gate-event.sh` | All | YAML stage logs |

Internal to cross-review.sh (not called directly by orchestrators):

| Script | Agent | Special handling |
|--------|-------|-----------------|
| `scripts/review/submit-to-claude.sh` | Claude reviewer | setsid watchdog, PGID, exit 124 |
| `scripts/review/submit-to-codex.sh` | Codex reviewer | 300s timeout, INVALID_OUTPUT |
| `scripts/review/submit-to-gemini.sh` | Gemini reviewer | standard + INVALID_OUTPUT |

---

## Deviation Table

| # | Deviation | Observed In | Classification | Resolution |
|---|-----------|-------------|---------------|-----------|
| 1 | Direct `submit-to-claude.sh` in orchestration loop | WRK-669 | Drift | Always use `cross-review.sh all` |
| 2 | Gemini ISO+INFO log format | WRK-671 | Drift | Normalise to YAML key-value |
| 3 | Codex INVALID_OUTPUT in impl review | WRK-670 | Drift | WRK-1000 (non-blocking) |
| 4 | Resource Intelligence skipped | All three | Tracked separately | WRK-673 (non-blocking) |

---

## Files Changed

| File | Action | Location |
|------|--------|---------|
| `assets/WRK-656/orchestrator-flow.md` | CREATE | Repo root assets (accessible to all agents) |
| `assets/WRK-656/wrk-656-orchestrator-comparison.html` | EDIT | Repo root assets |
| `specs/wrk/WRK-675/plan.md` | CREATE | This file |
| `.claude/work-queue/assets/WRK-675/` | GATE ARTIFACTS | plan HTML, review, TDD, legal, claim |
| `.claude/work-queue/working/WRK-675.md` | UPDATE | status, spec_ref, plan_reviewed |

---

## 9-Stage Flow

Capture → Resource Intelligence → Triage → Plan → Claim → Execute → Review → Close → Archive

(8 stages were listed in the draft — Review stage was missing between Execute and Close.)

---

## Test Strategy

- `verify-gate-evidence.py WRK-675` → exit 0.
- `assets/WRK-656/orchestrator-flow.md` exists and contains cross-link to comparison HTML.
- Comparison HTML `<a href="orchestrator-flow.md">` resolves correctly (same directory).
- Deviation table has 4 rows.
- Script suite table lists 6 canonical + 3 internal scripts.

---

## Risks / Notes

1. Codex not installed on ace-linux-1 → plan cross-review Codex is NO_OUTPUT (per policy).
2. Documentation-only WRK; TDD gate satisfied by verifier smoke tests.
3. Resource Intelligence (WRK-673) and Codex skill (WRK-1000) are informational follow-ons —
   WRK-675 can close independently.
