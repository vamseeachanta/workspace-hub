---
name: work-queue-workflow
description: >
  Explicit entrypoint skill for the WRK work-queue lifecycle workflow. Points to
  the canonical work-queue process and gatepass enforcement sequence.
version: 1.5.0
updated: 2026-03-07
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
---
# Work-Queue Workflow

This skill is a clear entrypoint for users who ask for the "work-queue workflow".
It delegates to canonical `work-queue` and `workflow-gatepass` contracts.

Operating principle: **humans steer, agents execute**.
Every stage should explicitly track whether a human decision is required.

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

   ### Stage 5 — Plan Draft (Human-in-Loop Interactive)

   **Key Planning Skills — invoke before drafting:**
   - `brainstorming` → before any creative or design decision
   - `resource-intelligence` → before stating facts or dependencies
   - `superpowers:test-driven-development` → spec tests before pseudocode
   - `workflow-html` → update the single lifecycle HTML after Stage 5 completes

   **Route A (simple) — Single-Agent Interactive Planning:**
   Agent and human walk the plan section-by-section in a live dialogue — this is NOT
   a drop-and-approve. Agent drafts, challenges its own assumptions, asks clarifying
   questions, surfaces tradeoffs. Human responds and guides. No scripts during Stage 5.
   Human must explicitly approve before plan markdown is saved.
   Output: single `specs/wrk/WRK-NNN/plan.md`.
   Cross-review (Stage 6) is a single self-review pass only.

   **Route B/C (medium/complex) — Multi-Agent Interactive Planning:**

   1. **Shared draft first**: Claude produces the initial plan draft (`specs/wrk/WRK-NNN/plan.md`)
      and opens it in the browser for user review.
   2. **3-agent interactive planning**: User sends the same draft plan to all three agents
      (Claude, Codex, Gemini) in separate interactive planning sessions. Each agent walks
      the plan section-by-section, surfaces gaps, and produces its own refined version.
      Each agent saves its output as:
      - `plan_claude.md` → `.claude/work-queue/assets/WRK-NNN/plan_claude.md`
      - `plan_codex.md` → `.claude/work-queue/assets/WRK-NNN/plan_codex.md`
      - `plan_gemini.md` → `.claude/work-queue/assets/WRK-NNN/plan_gemini.md`
   3. **Synthesize interactively with user**: Claude reads all three plans and presents
      differences and conflicts section-by-section to the user. User decides on each
      conflict. Claude does NOT auto-merge — every non-trivial difference is surfaced.
      Synthesis prompt structure:
      - Read plan_claude.md, plan_codex.md, plan_gemini.md
      - Present a diff table: topic | Claude | Codex | Gemini | recommended
      - For each conflict: ask user to decide before writing the merged section
      - After user approves all sections: write final `specs/wrk/WRK-NNN/plan.md`
      - Ask for explicit final approval before Stage 6

   **Parallel dispatch** (Route B/C — after Claude draft is ready):
   ```bash
   bash scripts/work-queue/stage5-plan-dispatch.sh WRK-NNN
   ```
   Dispatches Codex and Gemini in parallel (background processes); waits for both.
   Outputs: `assets/WRK-NNN/plan_codex.md`, `assets/WRK-NNN/plan_gemini.md`.
   After both land, trigger synthesis session with Claude (interactive with user).

   **Pseudocode requirement** (for non-trivial logic — ≥3 steps or branching):
   Produce function-level pseudocode before user review.
   Format: `function_name(inputs) → output  # objective in one line`
   N/A allowed with explicit reason: `n/a_reason: "pure-doc skill edit — no logic"`

   **Tests/Evals requirement:**
   List ≥3 test or verification cases before implementation begins.
   Format: `what | scenario (happy/edge/error) | expected result`
   N/A allowed with reason for pure-doc WRKs (skill/rule edits).

   **Stage 5 process:**
   - Open the plan-draft HTML in default browser (`xdg-open`) AND push to origin
     BEFORE presenting any recommendation. Update lifecycle HTML for Stage 5.
   - Walk the draft plan section-by-section — this is a dialogue, not a drop.
   - Ask tough clarifying questions; challenge weak assumptions; surface tradeoffs.
   - Write `assets/WRK-<id>/evidence/user-review-plan-draft.yaml` with full
     decision log (scope in/out, AC changes, risks, approve-as-is vs revise).

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

   ### Stage 10 — Work Execution

   **Key Execution Skills — invoke before writing code:**
   - `file-taxonomy` → understand file placement rules before touching any file
   - `coding-style` → verify naming, size, and style rules before writing
   - `superpowers:test-driven-development` → red → green → refactor cycle
   - `superpowers:systematic-debugging` → invoke on test failure before guessing fixes

   **Execution summary — produce after implementation:**
   Document in the lifecycle HTML Stage 10 section:
   - Functionality added or updated (what changed and why)
   - Key files changed: path, edit type (new/edit/delete), purpose
   - Key lines or sections edited: include script/code excerpts showing the change

   User-review checkpoints (stages 5/7/17): open lifecycle HTML in default browser,
   review the Gate-Pass Stage Status section, push to origin before presenting to user.
5. Verify close gate evidence and integrated/repo tests (3-5 pass records).
6. Close and archive using queue scripts.

Do not use shortened lifecycle variants for execution governance. This entrypoint
must always resolve to the canonical 20-stage chain.

## Source of Truth

- Process contract: `.claude/work-queue/process.md`
- Execution workflow: `coordination/workspace/work-queue/SKILL.md`
- Gate enforcement: `workspace-hub/workflow-gatepass/SKILL.md`
- Stage orchestration: `scripts/work-queue/start_stage.py` / `scripts/work-queue/exit_stage.py`
- Stage contracts (20): `scripts/work-queue/stages/stage-NN-*.yaml`
- Stage micro-skills (20): `.claude/skills/workspace-hub/stages/stage-NN-*.md`
- Gate hook: `scripts/work-queue/gate_check.py` (Write PreToolUse, supplemental)

## Version History

- **1.5.0** (2026-03-07): Stage 5 dispatch uses batch script — required in skill/contract (WRK-1020)
  - `scripts/work-queue/stage5-plan-dispatch.sh WRK-NNN` runs Codex+Gemini in parallel
  - Mirrors cross-review.sh pattern; background processes + wait; outputs to assets/WRK-NNN/
  - Referenced in SKILL.md, stage-05 micro-skill; dispatch is now a documented requirement
- **1.4.0** (2026-03-07): Stage 5 synthesis is interactive with user (WRK-1020)
  - Route B/C synthesis: Claude presents diff table section-by-section; user decides conflicts
  - No auto-merge — every non-trivial difference surfaced before writing final plan.md
  - Synthesis prompt structure: diff table (topic|Claude|Codex|Gemini|recommended) per section
- **1.3.0** (2026-03-07): Stage 5 interactive planning clarified for all routes (WRK-1020)
  - Route A: single-agent interactive planning (section-by-section dialogue, not drop-and-approve)
  - Route B/C: 3-step — shared draft → 3 interactive planning sessions → combine
  - Named artifacts: `plan_claude.md`, `plan_codex.md`, `plan_gemini.md` in assets/WRK-NNN/
  - Exit checklist updated with artifact naming and merge requirement
- **1.1.0** (2026-03-07): Stage 5 route-split, pseudocode/tests-evals, key-skills blocks, single-HTML model (WRK-1026)
  - Route A: human-in-loop inline only; Route B/C: 3-agent independent planning after markdown saved
  - Pseudocode requirement: function-level, N/A+reason allowed
  - Tests/Evals requirement: ≥3 entries, N/A+reason for pure-doc WRKs
  - Stage 5 exit checklist expanded to 9 items; hard stop before cross-review enforced
  - Stage 10: Key Execution Skills block + execution summary requirement (files, lines, excerpts)
  - Single lifecycle HTML model: one file per WRK, updated after each stage (workflow-html)
  - Doc-after-each-stage rule: lifecycle HTML and docs updated immediately, not deferred
- **1.0.4** (2026-03-07): Contract alignment — link Stage 5 policy to canonical checker (WRK-1017)
  - Added executable gate reference: `verify-gate-evidence.py --stage5-check`
  - All four official Stage 6 entrypoints now listed as callers
- **1.0.3** (2026-03-05): Stage 5 enforced as hard blocking gate (WRK-1017)
  - Added STOP — BLOCK marker and explicit blocking language for Stage 5
  - Added Stage 5 checklist (6 items, all required before Stage 6)
  - Documented `user-review-plan-draft.yaml` as required gate-verification artifact
- **1.0.2** (2026-03-05): Initial captured version

## Practical Lessons (WRK-690)

- Always run the workflow through shared scripts (`session.sh`, `work.sh`,
  `plan.sh`, `execute.sh`, `review.sh`, close/archive scripts) so signal logs are
  consistent across orchestrators.
- Refresh weekly gate-analysis before presenting coverage conclusions:
  1) `build-session-gate-analysis.py` 2) `audit-session-signal-coverage.py`.
- Treat per-agent coverage gaps as workflow defects even if aggregate metrics pass.
- In multi-agent parallel execution, keep WRK boundaries strict: unrelated changes
  from other active agents are non-blocking and must be documented (not reverted)
  in the current WRK as out-of-scope side effects.
- Keep AGENTS concise and map-like; use repo-local docs as system-of-record.
- Favor mechanical enforcement (scripts/linters/tests) over prose-only rules.
- Throughput policy: fast merges are acceptable only with bounded-risk controls
  (rollback path, follow-up WRK capture, recurring cleanup/refactor runs).
