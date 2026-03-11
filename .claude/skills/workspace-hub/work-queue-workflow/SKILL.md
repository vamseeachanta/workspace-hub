---
name: work-queue-workflow
description: >
  Explicit entrypoint skill for the WRK work-queue lifecycle workflow. Points to
  the canonical work-queue process and gatepass enforcement sequence.
version: 1.7.0
updated: 2026-03-08
category: workspace-hub
triggers:
  - work-queue workflow
  - wrk workflow
  - /work workflow
  - lifecycle workflow
related_skills:
  - coordination/workspace/work-queue
  - workspace-hub/workflow-gatepass
  - workspace-hub/workflow-html
  - workspace-hub/session-start
  - workspace-hub/session-end
capabilities:
  - workflow-entrypoint
  - lifecycle-routing
  - gatepass-handoff
requires:
  - .claude/work-queue/process.md
invoke: work-queue-workflow
tags: []
---
# Work-Queue Workflow

This skill is a clear entrypoint for users who ask for the "work-queue workflow".
It delegates to canonical `work-queue` and `workflow-gatepass` contracts.

Operating principle: **humans steer, agents execute**.
Every stage should explicitly track whether a human decision is required.

## Canonical Terminology

Use these definitions consistently across all skills, scripts, and artifacts:

| Term | Canonical meaning |
|------|------------------|
| **WRK session** | Single Claude conversation bounded by `/clear` or context reset |
| **WRK stage** | One of the 20 numbered lifecycle stages (Stage 1–20) |
| **Phase** | Sub-unit within a stage (e.g. Stage 6: Claude/Codex/Gemini phases; Stage 10: implementation phases) |
| **Step** | Numbered checklist action within a phase |
| **Checkpoint** | Snapshot artifact written at end of a WRK session (`checkpoint.yaml`) |
| **Resume** | Loading a checkpoint into a new WRK session via `/wrk-resume` before `/work run` |

Violations to avoid:
- Do NOT use "session" to mean "stage" (a stage spans many sessions; a session may touch many stages).
- Do NOT use "phase" as a synonym for "stage" (phases are sub-units inside a stage).
- Do NOT use "step" to mean "stage".

## Start-to-Finish Chain

1. Run `session-start`.
2. Use `/work` to select/create the WRK item.
3. Ensure plan exists and user approval explicitly names WRK ID.
4. Run the canonical **20-stage lifecycle** (Capture -> Archive) from
   `workflow-gatepass`.
   See `workflow-html` SKILL for the single lifecycle HTML model — one file per WRK
   updated at every stage gate (not separate snapshots per stage).
   Update the lifecycle HTML and underlying stage docs after EACH stage completes.

   **STOP — Stage 5 is a BLOCKING interactive gate. Do NOT advance to cross-review
   (Stage 6), do NOT set `plan_reviewed: true`, and do NOT generate plan-final HTML
   until the user explicitly approves in this session. Silence is not approval.**

   ### Stage Gate Policy

   | Stage | Name | Gate Type | Exit Artifact |
   |-------|------|-----------|---------------|
   | 1 | Capture | **HARD** | `user-review-capture.yaml` |
   | 2 | Triage | auto | — (pause on conflict) |
   | 3 | Resource Intelligence | auto | — (pause on very-high-risk gap) |
   | 4 | Plan Draft | auto | — (pause on scope change) |
   | 5 | User Review Plan Draft | **HARD** | `user-review-plan-draft.yaml` |
   | 6 | Cross Review Plan | auto | — (pause on P1 finding) |
   | 7 | User Review Plan Final | **HARD** | `plan-final-review.yaml` |
   | 8–16 | Execution stages | auto | — |
   | 17 | User Review Close | **HARD** | `user-review-close.yaml` |
   | 18–20 | Archive stages | auto | — |

   **Hard gate rule (R-25):** Stages 1, 5, 7, 17 are hard gates. Agent must STOP and wait for
   explicit user approval. Silence is not approval. Do NOT advance until user responds.

   **Auto-proceed rule (R-26):** All other stages proceed automatically UNLESS a
   `conditional_pause_trigger` is met (see `scripts/work-queue/stage-gate-policy.yaml`).

   **Conditional pause rule (R-27):** If an auto-proceed stage encounters very-high-risk
   conditions (P1 finding, scope change, blocked dependency), the agent must pause, describe
   the risk to the user, and await direction before continuing.

   **Stage 1 contract:** After capturing a WRK item, write `assets/WRK-NNN/evidence/user-review-capture.yaml`
   (template at `specs/templates/user-review-capture.yaml`) with `scope_approved: true` and the
   user's explicit confirmation. Route A WRKs may set `n/a: true` with `n/a_reason` to bypass.
   Stage 2 entry is blocked until this artifact is present and valid.

   ### Stage 4 — Plan Draft Creation

   Produce the plan artifact (`specs/wrk/WRK-NNN/plan.md`) before Stage 5 review.

   **Pseudocode requirement** (for non-trivial logic — ≥3 steps or branching):
   Include function-level pseudocode blocks inside the plan for every significant
   algorithm, gate check, or decision workflow.
   Format:
   ```
   function_name(inputs) → output  # objective in one line
     1. step one
     2. step two (branch: if X then A, else B)
     3. return result
   ```
   N/A allowed with explicit reason: `n/a_reason: "pure-doc WRK — no logic"`

   **Tests/Evals requirement:**
   List ≥3 test or verification cases in the plan before Stage 5 review.
   Format: `test_name | scenario (happy/edge/error) | expected result`

   **Plan sections required** (Route B/C minimum):
   - Mission / What / Why
   - Phases with numbered steps
   - Pseudocode blocks for each phase with non-trivial logic
   - Tests and Evals list
   - Risks and Out of Scope

   ### Stage 5 — Plan Draft (Human-in-Loop Interactive)

   **Key Planning Skills — invoke before drafting:**
   - `brainstorming` → before any creative or design decision
   - `resource-intelligence` → before stating facts or dependencies
   - `superpowers:test-driven-development` → spec tests before pseudocode
   - `workflow-html` → update the single lifecycle HTML after Stage 5 completes

   **Route A (simple):** Section-by-section dialogue (not drop-and-approve). Agent challenges assumptions, surfaces tradeoffs. Human approves before `specs/wrk/WRK-NNN/plan.md` is saved. Stage 6 = single self-review.

   **Route B/C (medium/complex):** (1) Claude produces draft + opens in browser. (2) `bash scripts/work-queue/stage5-plan-dispatch.sh WRK-NNN` dispatches Codex+Gemini in parallel → `assets/WRK-NNN/plan_{claude,codex,gemini}.md`. (3) Synthesis: Claude presents diff table (topic|Claude|Codex|Gemini|recommended) section-by-section — user decides every conflict before final `plan.md` is written.

   **Pseudocode** (non-trivial logic ≥3 steps): `function_name(inputs) → output  # objective`; N/A+reason allowed for pure-doc WRKs.
   **Tests/Evals:** ≥3 entries (`what | happy/edge/error | expected`) before implementation; N/A+reason for pure-doc WRKs.

   **Stage 5 process:** Open lifecycle HTML (`xdg-open`) + push to origin BEFORE presenting any recommendation. Walk plan section-by-section. Write `evidence/user-review-plan-draft.yaml` with decision log.

   **Stage 5 exit checklist — ALL must be true before Stage 6:**
   - [ ] Plan HTML opened in browser (`xdg-open`) and pushed to origin
   - [ ] Lifecycle HTML updated with Stage 5 evidence and approval block
   - [ ] Interactive walk-through completed section-by-section with user
   - [ ] User has explicitly approved (not just "ok" — scope/criteria/risk decisions)
   - [ ] `user-review-plan-draft.yaml` written with decision log
   - [ ] Plan artifacts updated from user decisions
   - [ ] Pseudocode produced for all non-trivial logic (or N/A with reason)
   - [ ] Tests/Evals list written (≥3 entries or N/A with reason) and reviewed
   - [ ] (Route B/C only) All 3 agents completed interactive planning sessions;
         `plan_claude.md`, `plan_codex.md`, `plan_gemini.md` saved in assets/WRK-NNN/;
         synthesis merged into final `specs/wrk/WRK-NNN/plan.md`; conflicts resolved

   Stage 5→6 enforced by checker (WRK-1017):
   `uv run --no-project python scripts/work-queue/verify-gate-evidence.py --stage5-check WRK-NNN`

   ### Stage 6 — Cross-Review

   Each reviewer (Claude, Codex, Gemini) produces `cross-review-<provider>.md` in
   `assets/WRK-NNN/evidence/`. Route A: single self-review pass.

   **Pseudocode review checklist** (each cross-review artifact must include): pseudocode present (or N/A+reason); matches ACs; ≤10 sub-steps per step; explicit branching; edge/error paths covered.

   Output format: `## Verdict: APPROVE|MINOR|REQUEST_CHANGES` + `### Pseudocode Review` ([PASS|FAIL] per phase) + `### Findings` ([P1|P2|P3]).
   Dispatch (Route B/C): `bash scripts/review/cross-review.sh specs/wrk/WRK-NNN/plan.md all`

   ### Stage 10 — Work Execution

   **Context Budget**: Route A <40%, Route B <70%, Route C = plan multi-session.
   At 80%: call `bash scripts/hooks/context-monitor.sh --usage-pct 80` to auto-checkpoint.
   See `.claude/docs/session-chunking.md` for chunking patterns.

   Skills: `file-taxonomy` → `coding-style` → `superpowers:test-driven-development` → `superpowers:systematic-debugging`.
   Execution summary (in lifecycle HTML S10): what changed + why; key files (path/edit-type/purpose); key lines with excerpts.
   User-review checkpoints (5/7/17): open lifecycle HTML, review Gate-Pass section, push to origin before presenting to user.
5. Verify close gate evidence and integrated/repo tests (3-5 pass records).
6. Close and archive using queue scripts.

Do not use shortened lifecycle variants for execution governance. This entrypoint
must always resolve to the canonical 20-stage chain.

## Plan-Mode Gates

Invoke the `workspace-hub/plan-mode` skill at the start of these deliberative stages,
before writing any artifact. `plan_mode: required` is recorded in each stage contract YAML.

| Stage | Name | Trigger |
|-------|------|---------|
| Stage 4 | Plan Draft | Before first lifecycle HTML write |
| Stage 6 | Cross-Review | Before synthesizing 3-provider verdicts |
| Stage 10 | Work Execution | Before implementation file writes |
| Stage 13 | Agent Cross-Review | Before recording implementation verdict |

Pattern: `EnterPlanMode` → think → `ExitPlanMode` → write evidence via Write tool.

## Orchestrator Team Pattern

**Hard rule:** No WRK may be fully executed in a single Claude conversation (Stage 1→20).
Each stage (or closely-related stage group) must be a separate agent task to prevent context rot.

**Default — on-demand TaskCreate:**
- Orchestrator reads checkpoints, makes decisions, delegates heavy work via TaskCreate
- Any subtask requiring >3 file reads or >50 lines of output → delegate via TaskCreate
- Orchestrator accumulates summaries, pass/fail signals — never raw file content
- Minimum granularity: one agent per stage; sub-stage splits allowed when stage exceeds ~200 output lines

**TeamCreate / spawn-team.sh:**
- Available for pre-planned parallel-phase execution when the full task set is known upfront
- NOT mandated — use when parallel spawning gives clear throughput benefit
- `spawn-team.sh WRK-NNN <slug>` prints a recipe and pre-flight checklist; it is a convenience
  tool, not a required entrypoint
- Requires Stage 1 exit gate (`user-review-capture.yaml` with `scope_approved: true`) before
  team recipe is printed

**Scope-discovery-first rule (R-28):**
Find N items FIRST, decide grouping, then spawn all agents at once.
Do NOT incrementally spawn additional agents without first knowing the full scope.

**Conditional pause triggers (R-27) for any auto-proceed stage:**
routing conflict, scope conflict, risk spike, gate verifier failure,
evidence contradiction, resource conflict, irreversible state risk.
When triggered: pause, describe the risk, await direction before continuing.

**Stage 17 rolling scope cap:**
During live validation, only HIGH-severity violations caused by WRK-NNN's own gates are
absorbed. Pre-existing patterns → capture as new WRK items in
`assets/WRK-NNN/evidence/deferred-findings.yaml` (`disposition: new-wrk`).

## Source of Truth

- Process contract: `.claude/work-queue/process.md`
- Execution workflow: `coordination/workspace/work-queue/SKILL.md`
- Gate enforcement: `workspace-hub/workflow-gatepass/SKILL.md`
- Stage orchestration: `scripts/work-queue/start_stage.py` / `scripts/work-queue/exit_stage.py`
- Stage contracts (20): `scripts/work-queue/stages/stage-NN-*.yaml`
- Stage micro-skills (20): `.claude/skills/workspace-hub/stages/stage-NN-*.md`
- Gate hook: `scripts/work-queue/gate_check.py` (Write PreToolUse, supplemental)

## Version History

- **1.8.0** (2026-03-08): Deliverables section in lifecycle HTML at close; stage-evidence path update rule on close; D/N classification → WRK-1044 (WRK-1035)
- **1.7.0** (2026-03-08): Stage 4 pseudocode req + Stage 6 cross-review pseudocode checklist; browser-open-before-approve rule (WRK-1035)
- **1.6.0** (2026-03-08): Canonical terminology table: WRK session/stage/phase/step/checkpoint/resume (WRK-1040)
- **1.5.0** (2026-03-07): Stage 5 dispatch via `stage5-plan-dispatch.sh`; Codex+Gemini parallel (WRK-1020)
- **1.4.0** (2026-03-07): Stage 5 synthesis interactive with user — diff table, no auto-merge (WRK-1020)
- **1.3.0** (2026-03-07): Stage 5 route-split; named plan artifacts; exit checklist expanded to 9 items (WRK-1020)

## Practical Lessons (WRK-690)

- Stages 8, 19, 20 (Claim/Close/Archive) are **autonomous** — run scripts without asking permission.
- Use shared scripts (`session.sh`, `work.sh`, `plan.sh`, `execute.sh`, `review.sh`) for consistent signal logs.
- Per-agent coverage gaps are workflow defects even if aggregate metrics pass.
- Multi-agent: keep WRK scope strict; out-of-scope side effects are non-blocking — document, don't revert.
- Favor mechanical enforcement (scripts/linters/tests) over prose-only rules.

## Lifecycle HTML — Deliverables Section (WRK-1035)

At Stage 17/18 (Close), regenerate lifecycle HTML with a **Deliverables** section appended at the end:

```
## Deliverables
| Artifact | Type | Path |
|----------|------|------|
| <file> | <script|skill|test|yaml|...> | <relative path> |
```

Source: `exit_artifacts` fields across all completed stage contracts + the WRK body's `## What` section.
Purpose: makes the HTML a self-contained record of what the WRK produced; reviewers see outcomes without reading evidence files.
Implementation target: `generate-html-review.py --lifecycle` → append deliverables table from `future-work.yaml` + stage-evidence exit_artifacts. (WRK-1041 scope)

## Stage-Evidence Path After Close (WRK-1035)

`stage-evidence.yaml` stage[1/2/9] evidence paths reference `working/WRK-NNN.md`.
After `close-item.sh` moves the WRK to `done/`, those paths become stale and fail `archive-item.sh`.

**Rule**: When `close-item.sh` moves a WRK from `working/` to `done/`, update any `stage-evidence.yaml` entries whose `evidence:` field references `working/WRK-NNN.md` → `done/WRK-NNN.md`. Add this as a step in `close-item.sh` after the `mv` command. (WRK-1044 D-scope)
