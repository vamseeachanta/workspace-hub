---
name: work-queue-workflow
description: >
  Explicit entrypoint skill for the WRK work-queue lifecycle workflow. Points to
  the canonical work-queue process and gatepass enforcement sequence.
version: 1.2.0
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

   **Route A (simple):** Human-in-loop interactive only. Agent drafts, human reviews
   inline. No scripts during Stage 5. Human must explicitly approve before markdown is
   saved. Cross-review (Stage 6) is a single self-review pass only.

   **Route B/C (medium/complex):** Same human-in-loop interactive as Route A for
   Stage 5 itself. After the user finishes and plan markdown is saved, ALL THREE agents
   (Claude, Codex, Gemini) independently draft their own plan version. Synthesis of all
   three outputs is produced and saved before proceeding to Stage 6 cross-review.

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
   - [ ] (Route B/C only) All 3 agents independently drafted plan; synthesis saved

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
