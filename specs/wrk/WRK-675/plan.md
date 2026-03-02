# WRK-675 Plan: governance(review) — align orchestrator flow & scripts

**Source WRK:** WRK-675
**Route:** C (complex)
**Created:** 2026-03-01
**Status:** draft

---

## Objective

Codify the canonical `/work run` orchestrator flow and reference script suite that Claude, Codex,
and Gemini must all follow, based on evidence from WRK-669 (Claude), WRK-670 (Codex), and
WRK-671/672 (Gemini). Produce two deliverables: `orchestrator-flow.md` (canonical doc) and an
updated comparison HTML.

---

## Phase 1 — Inventory (data-collection)

**Input:** Logs and asset files from WRK-669, WRK-670, WRK-671.

**Tasks:**
- Parse `WRK-669-*.log`, `WRK-670-*.log`, `WRK-671-*.log` for stage events and script names.
- Extract script calls from `review-input.md`, `variation-test-results.md`, summary HTML files.
- Build a matrix: orchestrator × script × usage (present/absent/variant).
- Note log format divergence: Claude/Codex use YAML key-value; Gemini uses ISO+INFO markers.
- Note `submit-to-claude.sh`: used only by Claude orchestrator; Codex/Gemini use `cross-review.sh`.
- Note Codex `INVALID_OUTPUT` in one implementation review (follow-on: WRK-1000).

**Acceptance:** Inventory table complete; discrepancies enumerated.

---

## Phase 2 — Analysis

**Tasks:**
- Identify deviations that are agent-specific (acceptable) vs. drift (fix needed).
- Determine canonical reference script suite (7 scripts; see §4 below).
- Define canonical log format: YAML key-value `timestamp/wrk_id/stage/action/provider/notes`.
- Record `submit-to-claude.sh` as a Claude-specific deviation (watchdog/PGID cleanup) — not
  required for Codex/Gemini but recommended when Claude is the reviewed party.
- Record Gemini ISO+INFO log style as a non-canonical deviation needing normalisation.

**Acceptance:** Canonical flow + deviation table drafted.

---

## Phase 3 — Documentation

**Deliverable 1:** `.claude/work-queue/assets/WRK-656/orchestrator-flow.md`
- Canonical 9-stage flow (Capture → Resource Intelligence → Triage → Plan → Claim → Execute →
  Close → Archive).
- Reference script suite table.
- Deviation table: agent-specific vs. drift.
- Follow-on improvement candidates.

**Deliverable 2:** `assets/WRK-656/wrk-656-orchestrator-comparison.html`
- Add "Canonical Flow" section linking to `orchestrator-flow.md`.
- Add "Script Alignment" table showing per-agent script usage vs. canonical.
- Add "Deviation Notes" highlighting normalisation targets.

**Acceptance:** Both files exist, cross-reference each other, validator passes on WRK-675.

---

## Canonical Reference Script Suite

| # | Script | Purpose | Required |
|---|--------|---------|---------|
| 1 | `scripts/agents/session.sh init` | Orchestrator lock (once/session) | All |
| 2 | `scripts/agents/work.sh run` | Work orchestration handoff | All |
| 3 | `scripts/agents/plan.sh` | Plan gate | All |
| 4 | `scripts/review/cross-review.sh` | Multi-agent cross-review | All |
| 5 | `scripts/work-queue/verify-gate-evidence.py` | Gate validator | All |
| 6 | `scripts/work-queue/log-gate-event.sh` | Stage log events (YAML format) | All |
| 7 | `scripts/review/submit-to-gemini.sh` | Gemini review submission | When Gemini is reviewer |

Agent-specific additions (not drift):
- `scripts/review/submit-to-claude.sh` — Claude orchestrator only (watchdog + PGID cleanup).

---

## Files Changed

| File | Action |
|------|--------|
| `.claude/work-queue/assets/WRK-656/orchestrator-flow.md` | CREATE |
| `assets/WRK-656/wrk-656-orchestrator-comparison.html` | EDIT (add Canonical Flow + Script Alignment sections) |
| `specs/wrk/WRK-675/plan.md` | CREATE (this file) |
| `.claude/work-queue/pending/WRK-675.md` | UPDATE frontmatter (spec_ref, status) |

---

## Test Strategy

- Verifier smoke tests: `verify-gate-evidence.py WRK-675` → exit 0.
- Manual check: `orchestrator-flow.md` exists and cross-links comparison HTML.
- Manual check: comparison HTML `<a href>` resolves to `orchestrator-flow.md`.

---

## Risks / Notes

1. Codex is not installed on ace-linux-1 → cross-review Codex will be NO_OUTPUT (per policy).
2. This is a documentation-only WRK; TDD gate satisfied by verifier smoke tests.
3. Phase 1 "10 additional runs" was aspirational in the original WRK text; existing three runs
   (WRK-669/670/671) are sufficient for the canonical flow definition.
