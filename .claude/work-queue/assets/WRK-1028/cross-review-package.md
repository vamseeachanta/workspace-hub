# WRK-1028 Cross-Review Package — Stage 6
## Plan: Stage-isolated WRK lifecycle

### Problem
The 20-stage WRK lifecycle runs as a single long conversation causing:
1. Context compaction — hard-stop instructions compressed away mid-session
2. Context rot — earlier stage noise pollutes later stages
3. Stage jumping — no mechanical barrier between stages
4. Quality drift — heavy stages treated same as light stages

### Architecture Decision
Stage-isolation model: each stage starts fresh from previous stage's exit artifacts.
- `task_agent` — autonomous stages spawn fresh Task agent (zero context rot)
- `human_session` — gate stages (1,5,7,17) run in current session (human IS new context)
- `chained_agent` — light stage groups in one Task agent (2+3+4, 8+9)

### Single Lifecycle HTML
One `WRK-NNN-lifecycle.html` per WRK. Updated at every stage exit.
Every stage has: reviewed_by, confirmed_by, decision, notes schema.
No separate plan-draft/implementation HTML files.

### Stage Classification
- Light (4KB budget): 1, 3, 8, 9, 18, 19, 20 — work-queue-workflow only
- Medium (8KB): 2, 4, 6, 11, 13, 14, 15, 16 — work-queue-workflow + domain skill
- Heavy (16KB): 5, 7, 10, 12, 17 — + brainstorming/TDD/systematic-debugging/workflow-html

### Human Gates (3)
- Gate 5→6: user-review-plan-draft.yaml must have decision: approved
- Gate 7→8: lifecycle HTML Stage 7 section must have confirmed_by: at line-start
- Gate 17→18: user-review-close.yaml must have decision: approved

### Key Design Decisions (all user-approved)
- Stage 5 Route C: 3 parallel terminals Claude/Codex/Gemini simultaneously; orchestrator synthesizes combined-plan.md
- Stage 6 + Stage 13: mandatory 3-provider review (Claude/Codex/Gemini) ALL routes; override only if user explicitly states quota unavailable AND explicitly instructs to continue
- Context hard-stop at 70% of context_budget_kb — mandatory /checkpoint + new session
- Gate enforcement: custom gate-check.py PreToolUse hook scoped to active-wrk (not hookify markdown)
- Checkpoint/resume auto-suggested at every stage exit; GATE PASSED banner at human gates

### 4-Phase Delivery
P1: gate-check.py (3 gates: 5→6, 7→8, 17→18)
P2: start-stage.sh + exit-stage.sh + stage-state.yaml
P3: 20 YAML contracts (≤15 lines each) + 20 micro-skills (≤20 lines each)
P4: Heavy-stage enforcement (TDD check, context budget 70% hard-stop) + generate-html-review.py --stage N --update

### start-stage.sh logic
1. Read scripts/work-queue/stages/stage-NN-slug.yaml contract
2. Measure entry_reads total size — if ≥70% of context_budget_kb: HARD STOP + checkpoint prompt
3. If invocation=task_agent: build prompt (contract + entry_reads + micro-skill) → spawn Task agent
4. If invocation=human_session: load entry_reads; emit micro-skill checklist; check for checkpoint.yaml → suggest /resume
5. Update .claude/state/stage-state.yaml

### exit-stage.sh logic
1. Read contract exit_artifacts[] — verify each exists
2. If human_gate=true: check gate field value (decision: approved / confirmed_by:)
3. If any check fails: exit 1 with specific message
4. Call generate-html-review.py WRK-NNN --stage N --update (lifecycle HTML)
5. Write stage log; update stage-state.yaml; git commit
6. If human_gate: print GATE PASSED banner + mandatory /checkpoint prompt
7. Else: print stage complete + /checkpoint tip

### gate-check.py PreToolUse hook
- Reads .claude/state/active-wrk to get WRK_ID
- Gate 5→6: blocks write to evidence/cross-review.yaml unless assets/{WRK_ID}/evidence/user-review-plan-draft.yaml contains "decision: approved"
- Gate 7→8: blocks write to evidence/claim-evidence.yaml|activation.yaml unless lifecycle HTML Stage 7 section contains "confirmed_by:" at line-start
- Gate 17→18: blocks write to evidence/reclaim.yaml unless assets/{WRK_ID}/evidence/user-review-close.yaml contains "decision: approved"

### 20 YAML Contract Schema (each ≤15 lines)
order, name, weight, invocation, human_gate, skills_required[], entry_reads[], exit_artifacts[], blocking_condition, log_action, context_budget_kb

### 20 Micro-Skill Schema (each ≤20 lines)
Stage N | invocation | weight
Entry: [artifacts]
Checklist: ≤8 items
Exit: [artifacts]

### 14 Acceptance Criteria
AC-01: 20 YAML contracts exist at scripts/work-queue/stages/stage-NN-slug.yaml
AC-02: Each contract has all 11 required fields
AC-03: start-stage.sh routes task_agent vs human_session correctly
AC-04: exit-stage.sh validates artifacts, checks human_gate, writes log, updates lifecycle HTML + stage-state.yaml
AC-05: stage-state.yaml at .claude/state/ (gitignored)
AC-06: 20 micro-skills at .claude/skills/workspace-hub/stages/, ≤20 lines each
AC-07: Lifecycle HTML updated at every stage exit; stage chip reflects status
AC-08: Stage 10 exit checks ≥1 test file; Stage 12 exit checks ≥3 test pass records
AC-09: gate-check.py Gate 5→6 blocks until user-review-plan-draft.yaml approved
AC-10: gate-check.py Gate 7→8 blocks until lifecycle HTML Stage 7 confirmed_by present
AC-11: gate-check.py Gate 17→18 blocks until user-review-close.yaml approved
AC-12: verify-gate-evidence.py reads stage-state.yaml as corroborating signal
AC-13: workflow-gatepass/SKILL.md + work-queue-workflow/SKILL.md reference start/exit-stage.sh
AC-14: ≥7 unit tests all pass

### 7 Unit Tests
1. test_start_stage_task_agent — Task agent prompt contains contract + entry_reads + micro-skill
2. test_start_stage_human_session — checklist emitted; lifecycle HTML chip flipped to in-progress
3. test_exit_stage_missing_artifact — SystemExit(1); no log; lifecycle HTML not updated
4. test_exit_stage_happy_advance — log written; lifecycle HTML updated; stage-state.yaml updated; exit 0
5. test_exit_stage_human_gate_stop — SystemExit(1) when decision field missing/not approved
6. test_hookify_gate5_blocked — gate-check blocks write when user-review-plan-draft.yaml missing
7. test_hookify_gate5_allowed — gate-check allows write when decision: approved present

### Constraints
- workspace-hub only (no submodule changes)
- scripts use uv run --no-project python for any Python
- gate-check.py must not false-positive on non-WRK writes
- stage-state.yaml is .claude/state/ (gitignored runtime state)
- micro-skills ≤20 lines; contracts ≤15 lines (context budget discipline)
