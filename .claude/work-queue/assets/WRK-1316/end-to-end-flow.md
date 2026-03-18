# WRK Lifecycle: End-to-End Flow Trace

> Every LLM action, script call, hook fired, and human interaction from `/work run` to archive.
> This is what SHOULD happen. Deviations are enforcement failures.

---

## Pre-Entry: User types `/work run WRK-1323`

```
USER INPUT: /work run WRK-1323
```

### What fires:
1. **Skill tool** invokes `work` skill → reads command-interface SKILL.md
2. Skill detects "run" verb → routes to processing pipeline
3. **Bash**: `bash scripts/agents/work.sh --provider claude run`
   - work.sh reads `active-wrk` or sets it
   - work.sh prints **MANDATORY PREAMBLE** (WRK-1316 box)
   - work.sh prints routing recommendation
   - work.sh prints checkpoint if resuming

### LLM sees:
```
╔══════════════════════════════════════════════════════════════════╗
║  MANDATORY: Stage Machinery Required (WRK-1316)                 ║
║  For EVERY stage, you MUST call:                                 ║
║    1. start_stage.py WRK-1323 N                                  ║
║    2. Do the stage work                                          ║
║    3. exit_stage.py WRK-1323 N                                   ║
║  Human gates (1, 5, 7, 17): STOP and wait for "I approve stage N"║
╚══════════════════════════════════════════════════════════════════╝
```

### LLM decision:
→ "I need to start Stage 1. Call start_stage.py."

---

## Stage 1 — Capture

### 1a. Entry

```
LLM ACTION: Bash
COMMAND: uv run --no-project python scripts/work-queue/start_stage.py WRK-1323 1
```

**Hooks that fire (PreToolUse on Bash)**:
- `session-logger.sh pre` → logs tool use
- `propagate-ecosystem-check.sh` → link check
- `readiness.sh` → session readiness
- `enforce-no-bash-evidence.sh` → checks command (not evidence write → PASS)
- `enforce-stage-commit.sh` → checks command (not git commit → PASS)

**start_stage.py internals**:
1. `_stage_progression_guard()` → Stage 1 has no predecessor → PASS
2. `_run_pre_enter_hooks()` → reads stage-01-capture.yaml → no pre_enter_hooks → skip
3. Stage 1 special: writes `evidence/session-lock.yaml` (pid, hostname, timestamp)
4. `route_stage()` → prints stage banner + micro-skill content:
   ```
   Stage 1: Capture ── START
   --- Stage 1 Micro-Skill ---
   Stage 1 · Capture | human_interactive | light | single-thread
   Checklist:
   1. Ask human: WRK title, mission, category
   2. Write pending/WRK-NNN.md with valid frontmatter
   ...
   ```
5. `_surface_tools_activated()` → prints activated skills
6. `_update_stage_ev()` → writes `stage-evidence.yaml` with stage 1 = `in_progress`
7. `_log_gate_wait_start()` → calls `is-human-gate.sh 1` → exit 0 (IS gate)
   → writes `evidence/stage-timing-01.yaml` with `started_at`, `human_gate: true`
   → prints "GATE WAIT: Stage 1 — waiting for user approval."
8. `_regenerate_lifecycle_html()` → generates lifecycle + plan HTML
9. `_auto_open_html_for_human_gates()` → Stage 1 is in map → `xdg-open` both HTMLs

**LLM sees**: Stage banner, micro-skill checklist, "GATE WAIT" message, HTML opened

### 1b. Stage Work

```
LLM ACTION: Read pending/WRK-1323.md (already exists — was pre-created)
LLM ACTION: Bash — validate-wrk-frontmatter.sh WRK-1323
LLM OUTPUT: "Here is WRK-1323: [summary]. Do you approve the scope?"
```

**LLM STOPS HERE** — human gate. Does NOT proceed.

### 1c. Human Gate

```
USER INPUT: "I approve stage 1"
```

### 1d. Evidence Write

```
LLM ACTION: Write evidence/user-review-capture.yaml
```

**Hooks that fire (PreToolUse on Write)**:
- `gate_check.py` → checks gate 5/7/17 (stage 1 not checked here → PASS)
- `enforce-stage-machinery.sh` → path contains `evidence/` → checks stage-evidence.yaml
  → stage 1 is `in_progress` → PASS

**File written**: `scope_approved: true`, `reviewer: vamsee`, `approval_text: "I approve stage 1"`

### 1e. Exit

```
LLM ACTION: Bash
COMMAND: uv run --no-project python scripts/work-queue/exit_stage.py WRK-1323 1
```

**exit_stage.py internals**:
1. Loads stage-01-capture.yaml
2. Checks exit_artifacts: `pending/WRK-1323.md` exists? YES. `lifecycle.html` exists? YES.
3. `_deterministic_stage_check()` → D-item checks for stage 1
4. `_heavy_stage_check()` → stage 1 not heavy → skip
5. Human gate check → `gate_file: user-review-capture.yaml`, `gate_value: scope_approved: true` → PASS
6. **verify_checklist()** → reads stage-01 checklist (4 items)
   → checks `evidence/checklist-01.yaml` → MUST EXIST with all items completed
   → If missing → BLOCKED (exit 1)
7. **run_hooks()** → loads pre_exit_hooks + pre_checks → stage 1 has none → skip
8. `_log_stage_completed()` → appends `completed_at` + `duration_s` to `stage-timing-01.yaml`
9. `_update_stage_ev()` → marks stage 1 = `done`
10. `_regenerate_lifecycle_html()` → HTML updated (auto-refresh picks it up)
11. Writes checkpoint.yaml
12. Prints "Stage 1 exit validated."

**LLM sees**: "Stage 1 exit validated. All artifacts present."

### 1f. LLM Decision
→ "Stage 1 done. Moving to Stage 2. Call start_stage.py WRK-1323 2."

---

## Stage 2 — Resource Intelligence

### 2a. Entry

```
LLM ACTION: Bash
COMMAND: uv run --no-project python scripts/work-queue/start_stage.py WRK-1323 2
```

**start_stage.py internals**:
1. `_stage_progression_guard()` → checks stage-evidence.yaml → stage 1 = `done` → PASS
2. `_run_pre_enter_hooks()` → stage-02 has no pre_enter_hooks → skip
3. `route_stage()` → prints banner + micro-skill:
   ```
   Stage 2: Resource Intelligence ── START
   Checklist:
   1. Search codebase
   2. Query knowledge base
   3. Online research (WebSearch)
   4. Save documents to docu-intel
   5. Assess complexity
   ...
   ```
4. `_surface_tools_activated()` → prints: resource-intelligence, document-index-pipeline, WebSearch, WebFetch
5. `_update_stage_ev()` → stage 2 = `in_progress`
6. `_log_gate_wait_start()` → `is-human-gate.sh 2` → exit 1 (NOT gate) → writes timing, no GATE WAIT message
7. HTML regenerated (not opened — auto-refresh)

### 2b. Stage Work

```
LLM ACTION: Grep/Glob — search codebase for existing code
LLM ACTION: Bash — query-knowledge.sh --category tooling
LLM ACTION: WebSearch — "verify_checklist CLI dry-run patterns"
LLM ACTION: Write evidence/resource-intelligence.yaml
```

**Hook on Write**: `enforce-stage-machinery.sh` → stage 2 `in_progress` → PASS

### 2c. Exit

```
LLM ACTION: Bash
COMMAND: uv run --no-project python scripts/work-queue/exit_stage.py WRK-1323 2
```

**exit_stage.py**: checks artifacts → checklist → hooks → timing → HTML → checkpoint
→ "Stage 2 exit validated."

### 2d. LLM Decision
→ "Stage 2 done. Auto-proceed to Stage 3."

---

## Stages 3-4 (Auto-proceed, same pattern)

```
For each stage N in [3, 4]:
  LLM: Bash → start_stage.py WRK-1323 N
  LLM: [stage work — reads, writes, etc.]
  LLM: Bash → exit_stage.py WRK-1323 N
```

Stage 3: Triage → set route A, workstations, orchestrator
Stage 4: Plan Draft → EnterPlanMode → write ACs, pseudocode, test plan → generate plan.html

---

## Stage 5 — User Review: Plan Draft (HARD GATE)

### 5a. Entry

```
LLM ACTION: Bash
COMMAND: uv run --no-project python scripts/work-queue/start_stage.py WRK-1323 5
```

**start_stage.py**:
- Stage progression guard → stage 4 = `done` → PASS
- Timing written with `human_gate: true`
- Prints "GATE WAIT: Stage 5 — waiting for user approval."
- HTML regenerated (NOT opened — already open from Stage 1)

### 5b. Stage Work

```
LLM OUTPUT: "Here is the plan for WRK-1323:
  ACs: [list]
  Pseudocode: [blocks]
  Test plan: [entries]

  Please review each section."
```

**LLM walks through each section, waits for feedback after each.**

### 5c. Human Gate

**LLM STOPS.** Prints: "Waiting for: I approve stage 5"

```
USER INPUT: "I approve stage 5"
```

### 5d. Evidence + Exit

```
LLM ACTION: Write evidence/user-review-plan-draft.yaml
  → decision: approved, approval_text: "I approve stage 5"
LLM ACTION: Bash → exit_stage.py WRK-1323 5
```

**exit_stage.py**: checklist (5 items, 4 requires_human) → all complete with approved_by → PASS

---

## Stage 6 — Cross-Review (Auto-proceed)

```
LLM: Bash → start_stage.py WRK-1323 6
LLM: Bash → cross-review.sh <plan-file> all
  → Claude, Codex (or Opus fallback), Gemini review plan
LLM: Write evidence/cross-review.yaml (3 reviewers, P1/P2 findings)
LLM: Bash → exit_stage.py WRK-1323 6
```

---

## Stage 7 — User Review: Plan Final (HARD GATE)

### 7a. Entry + Work

```
LLM: Bash → start_stage.py WRK-1323 7
LLM OUTPUT: "Cross-review findings: [P1/P2 list]. All P1s resolved."
LLM: STOPS — "Waiting for: I approve stage 7"
```

### 7b. Human Gate

```
USER INPUT: "I approve stage 7"
```

### 7c. Exit

```
LLM: Write evidence/plan-final-review.yaml
LLM: Bash → exit_stage.py WRK-1323 7
```

**exit_stage.py**: checklist (4 items, 2 requires_human) → hooks (check-p1-resolved.sh) → PASS
→ Prints "GATE PASSED — Stage 8 unlocked."

**POST-GATE: R-26 active. Stages 8-16 auto-proceed without asking.**

---

## Stages 8-16 (Auto-proceed chain)

```
For each stage N in [8, 9, 10, 11, 12, 13, 14, 15, 16]:

  LLM: Bash → start_stage.py WRK-1323 N

  Stage 8:  claim-item.sh → move to working/, write activation.yaml
  Stage 9:  Load skills, write routing.yaml
  Stage 10: TDD — write tests, implement, refactor, write execute.yaml, git commit+push
  Stage 11: generate-html-review.py --lifecycle, verify 20 sections
  Stage 12: Run full test suite, build AC-test matrix, write ac-test-matrix.md
  Stage 13: cross-review.sh on implementation, write review.md
  Stage 14: verify-gate-evidence.py → all gates PASS, write gate-evidence-summary.yaml
  Stage 15: Review for future work items, /work add if needed, write future-work.yaml
  Stage 16: Capture ≥3 lessons learned, write resource-intelligence-update.yaml

  LLM: Bash → exit_stage.py WRK-1323 N
```

**Each exit_stage.py call**: validates artifacts → checklist → hooks → timing → HTML → checkpoint

**Stage 10 special**: pre_enter_hooks fire (verify-log-presence.sh), TDD skill activated
**Stage 14 special**: pre_exit_hooks fire (verify-gate-evidence.py must exit 0)
**Stage 17 special**: pre_exit_hooks fire (check-acs-pass.sh must exit 0)

---

## Stage 17 — User Review: Implementation (HARD GATE)

### 17a. Entry

```
LLM: Bash → start_stage.py WRK-1323 17
```

Timing with `human_gate: true`. "GATE WAIT" printed.

### 17b. Stage Work

```
LLM OUTPUT: "Implementation complete. Here's the summary:
  - Stage 10: [what was implemented]
  - Stage 12: [test results — X pass, 0 fail]
  - Stage 13: [cross-review — APPROVE, findings resolved]
  - Stage 14: [all gates PASS]

  Questions?"
```

**LLM answers questions, applies fixes if requested.**

### 17c. Human Gate

**LLM STOPS.** "Waiting for: I approve stage 17"

```
USER INPUT: "I approve stage 17"
```

### 17d. Exit

```
LLM: Write evidence/user-review-close.yaml
LLM: Bash → exit_stage.py WRK-1323 17
```

**exit_stage.py**: checklist (4 items, 3 requires_human) → hooks (check-acs-pass.sh) → PASS

---

## Stages 18-20 (Auto-proceed, close + archive)

```
Stage 18 — Reclaim:
  LLM: Bash → start_stage.py WRK-1323 18
  LLM: Write evidence/reclaim.yaml (status: n/a — no checkpoint break)
  LLM: Bash → exit_stage.py WRK-1323 18

Stage 19 — Close:
  LLM: Bash → start_stage.py WRK-1323 19
  LLM: Bash → verify-gate-evidence.py WRK-1323 → exit 0
  LLM: Bash → close-item.sh WRK-1323
    → legal scan, final gate check, move working/ → done/
  LLM: Bash → exit_stage.py WRK-1323 19

Stage 20 — Archive:
  LLM: Bash → start_stage.py WRK-1323 20
  LLM: Bash → archive-item.sh WRK-1323
    → move done/ → archive/2026-03/
  LLM: Bash → clear-active-wrk.sh
  LLM: Bash → git commit + push (lifecycle HTML final state)
  LLM: Bash → exit_stage.py WRK-1323 20
```

### Hook on git commit (enforce-stage-commit.sh):
→ active WRK has stage-timing-*.yaml files → PASS

---

## Summary: What Fires Per Stage

| Step | Script/Hook | Purpose |
|------|-------------|---------|
| **Entry** | `start_stage.py WRK N` | Progression guard, pre_enter hooks, micro-skill, tool activation, timing, HTML |
| ↳ Hook | `enforce-no-bash-evidence.sh` | Block Bash evidence writes |
| ↳ Hook | `enforce-stage-commit.sh` | Block commit without timing |
| **Work** | LLM uses tools (Read, Write, Bash, etc.) | Actual stage work |
| ↳ Hook | `enforce-stage-machinery.sh` | Block Write to evidence/ without in_progress stage |
| ↳ Hook | `gate_check.py` | Block Write past gates 5→6, 7→8, 17→18 |
| **Exit** | `exit_stage.py WRK N` | Artifact check, checklist, pre_exit hooks, timing, HTML, checkpoint |

## Human Interaction Points

| Stage | Gate | What User Sees | What User Types |
|-------|------|----------------|-----------------|
| 1 | Capture | WRK summary, scope question | "I approve stage 1" |
| 5 | Plan Draft | Plan sections walked through | "I approve stage 5" |
| 7 | Plan Final | Cross-review findings, P1 resolution | "I approve stage 7" |
| 17 | Implementation | Stages 10-16 summary, test results | "I approve stage 17" |

## Evidence Files Created (per WRK)

```
assets/WRK-1323/evidence/
├── session-lock.yaml           ← Stage 1 entry
├── user-review-capture.yaml    ← Stage 1 exit
├── resource-intelligence.yaml  ← Stage 2 exit
├── user-review-plan-draft.yaml ← Stage 5 exit
├── cross-review.yaml           ← Stage 6 exit
├── plan-final-review.yaml      ← Stage 7 exit
├── claim-evidence.yaml         ← Stage 8 exit
├── activation.yaml             ← Stage 8 exit
├── execute.yaml                ← Stage 10 exit
├── ac-test-matrix.md           ← Stage 12 exit
├── review.md                   ← Stage 13 exit
├── gate-evidence-summary.yaml  ← Stage 14 exit
├── future-work.yaml            ← Stage 15 exit
├── resource-intelligence-update.yaml ← Stage 16 exit
├── user-review-close.yaml      ← Stage 17 exit
├── reclaim.yaml                ← Stage 18 exit
├── stage-evidence.yaml         ← Updated by start/exit at every stage
├── stage-timing-01.yaml        ← One per stage (started_at, completed_at, duration_s)
├── stage-timing-02.yaml
├── ...
├── stage-timing-20.yaml
├── checklist-01.yaml           ← Checklist completion state per stage
├── checklist-02.yaml
├── ...
├── hooks-pre_exit-07.yaml      ← Hook execution evidence (stages with hooks)
├── hooks-pre_exit-14.yaml
├── hooks-pre_exit-17.yaml
└── hooks-pre_exit-19.yaml
```
