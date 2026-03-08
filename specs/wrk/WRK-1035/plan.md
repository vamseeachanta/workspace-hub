# WRK-1035 Plan — Work-Queue Lifecycle Hardening
> Route: C | Complexity: complex | Created: 2026-03-08

## Mission

Harden the work-queue lifecycle against retroactive approval fabrication, stage-skipping, Codex
bypass, and skill context-rot by enforcing machine-level gates, tightening skill contracts, pruning
verbose skills, and formalising the orchestrator team pattern across Stages 1–20.

---

## Phases

### Phase 1 — Stage Gate Policy Enforcement (Stage 1 Exit Gate + Policy Table)

**Goal:** Add a Stage 1 exit gate requiring user approval of captured scope before Stage 2 entry,
publish a machine-readable stage gate policy, and surface the policy table in the relevant skills.

**Files to change:**

- `specs/templates/user-review-capture.yaml` — new canonical template for Stage 1 exit artifact
  (fields: `stage: 1`, `reviewer`, `confirmed_at`, `scope_approved: true/false`, `notes`)
- `scripts/work-queue/stage-gate-policy.yaml` — new machine-readable gate classification
  (hard-gate stages: 1, 5, 7, 17; auto-proceed: 2–4, 6, 8–16, 18–20; conditional-pause rules
  from R-27 as a `trigger_conditions` list)
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — add §Stage Gate Policy table
  (hard/auto/conditional columns); add Stage 1 contract block with `user-review-capture.yaml`
  exit requirement (R-25); add R-26 (Stage 2 routing conflict pause) and R-27 (conditional pause
  trigger list for ALL auto-proceed stages)
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — add Stage 1 exit gate entry
  to stage-contract table; add conditional-pause rule (R-27) cross-reference; note this SKILL
  is a pruning candidate (985 lines — addressed in Phase 5)
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` — add `user-review-capture.yaml`
  to Evidence Locations list; add Stage 1 to Required Lifecycle Chain; add no-bypass rule for
  Stage 1 gate

**Rolling scope intake policy:**

- Scope additions and refinements are handled ad-hoc when prompted by the user — no formal
  process or artifact required. The agent may update the plan document in response to user
  direction without triggering a new Stage 4 plan-draft cycle.

**New scripts:**

- `scripts/work-queue/templates/user-review-capture.yaml` — template (duplicate entry-point so
  `claim-item.sh` can copy it on WRK creation)

**Tests:**

- `scripts/work-queue/tests/test_stage1_gate.py`
  - T1: Stage 2 entry blocked when `user-review-capture.yaml` absent
  - T2: Stage 2 entry passes when `scope_approved: true` and `confirmed_at` non-empty
  - T3: Stage 2 entry blocked when `scope_approved: false`
  - T4: Template file renders all required fields without placeholder gaps

**Acceptance criteria:**

- [ ] `user-review-capture.yaml` template exists at `specs/templates/`
- [ ] `stage-gate-policy.yaml` exists at `scripts/work-queue/` with hard/auto/conditional entries
  for all 20 stages
- [ ] `work-queue-workflow/SKILL.md` contains the stage gate policy table and Stage 1 contract
  block (R-25, R-26, R-27)
- [ ] `work-queue/SKILL.md` references Stage 1 gate in its stage-contract section
- [ ] `workflow-gatepass/SKILL.md` includes `user-review-capture.yaml` in Evidence Locations
- [ ] Gate verifier check for `user-review-capture.yaml` presence at Stage 2 entry added
  (addressed in Phase 3 — cross-phase dependency noted)
- [ ] T1–T4 pass

---

### Phase 2 — Retroactive Approval Prevention (R-01 through R-15, R-19, R-20)

**Goal:** Make retroactive timestamp fabrication detectable at the skill-language level AND
script-enforcement level for Stages 5, 7, and 17 — covering midnight UTC sentinel values,
browser-open to approval elapsed time, stage-tagged approvals, stale-artifact detection,
and scope-revision flow.

**Files to change:**

- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — update Stage 5 contract:
  - Add explicit prohibition: "Do NOT write `user-review-plan-draft.yaml` until the user has
    responded in this conversation. The `confirmed_at` timestamp must be taken from the moment
    of the user's response — not from plan creation time."
  - Add ≥300 second minimum between `plan_draft.opened_at` and `plan_final.opened_at` (R-15)
  - Add negative example (❌ pre-filled timestamp before user responds) and positive example
    (✅ user says "approve", agent writes artifact immediately after with `date -u` timestamp)
  - Add explicit WAIT protocol: "After `xdg-open`, emit a blocking terminal prompt. Do NOT
    proceed until the user responds with an explicit decision in this conversation."
  - Update Stage 7 contract with same prohibition and negative/positive examples for
    `plan-final-review.yaml` (`confirmed_by`, `confirmed_at`)
  - Update Stage 17 contract with same for `user-review-close.yaml` (`reviewer`,
    `confirmed_at`/`reviewed_at`) — minimum 300-second elapsed time after browser-open (R-03)
  - Add Stage 17 WAIT protocol: "For ALL work items, the agent must explicitly seek user
    confirmation before writing `user-review-close.yaml`. Emit a blocking prompt: 'Stage 17
    review required — please confirm you have reviewed the implementation and approve close.'
    Do NOT write the artifact until the user responds. User may respond 'No WAIT' to bypass
    the wait for the current session; if so, set a session-level flag `stage17_wait_bypassed:
    true` and proceed without blocking on future Stage 17 calls in the same session."
  - Add `stage:` field requirement to all three approval artifact templates (R-10)
  - Add stage-field cross-stage re-use prohibition: "An existing approval artifact with
    `stage: 5` MUST NOT be treated as satisfying Stage 7 or Stage 17"
  - Add stale-artifact detection rule (R-11 user thought): stage-start must log and ignore
    artifacts from prior runs found in future-stage directories; never treat stale artifact
    as satisfying current gate
  - Add scope-revision rule (R-20): if scope substitution accepted during plan review, agent
    must produce a new Stage 4 plan before requesting Stage 5 approval; prior plan is invalidated
  - Add ISO 8601 datetime requirement (R-19): all `reviewed_at` / `confirmed_at` fields must
    be full datetime with UTC offset (`2026-03-07T12:34:00Z`) — date-only is rejected

- `scripts/work-queue/templates/user-review-plan-draft-template.yaml` — add `stage: 5` field
- `scripts/work-queue/templates/user-review-plan-final-template.yaml` — add `stage: 7` field
- `scripts/work-queue/templates/user-review-close-template.yaml` — new canonical template for
  Stage 17 (fields: `stage: 17`, `reviewer`, `confirmed_at`, `reviewed_at`, `decision`,
  `scope_approved`, `notes`); replaces inline heredoc in `close-item.sh`
- `scripts/work-queue/close-item.sh` — add pre-check (R-04/R-08 gap #14):
  - Assert `execute.yaml` exists and `executed_at` is in the past before invoking verifier
  - Assert `user-review-close.yaml` exists, `confirmed_at` non-empty, `confirmed_at` strictly
    after `execute.executed_at` — exit 1 with diagnostic if any condition fails
  - Replace inline heredoc Stage 17 bootstrap with copy from canonical template

**Tests:**

- `scripts/work-queue/tests/test_retroactive_approval.py`
  - T5: `close-item.sh` exits 1 when `execute.yaml` absent
  - T6: `close-item.sh` exits 1 when `executed_at` is in the future
  - T7: `close-item.sh` exits 1 when `user-review-close.yaml` absent
  - T8: `close-item.sh` exits 1 when `confirmed_at` predates `executed_at`
  - T9: Approval artifact template includes `stage:` field for stages 5, 7, 17
  - T10: `user-review-close-template.yaml` renders all required fields correctly

**Acceptance criteria:**

- [ ] `work-queue-workflow/SKILL.md` Stage 5, 7, and 17 contracts each contain explicit
  prohibition, WAIT protocol, negative example, and positive example
- [ ] All three approval artifact templates include `stage:` field
- [ ] `user-review-close-template.yaml` exists at `scripts/work-queue/templates/`
- [ ] `close-item.sh` shell-blocks (exit 1) on absent/future `executed_at` and timestamp
  ordering violations before invoking the gate verifier
- [ ] T5–T10 pass

---

### Phase 3 — Gate Verifier Hardening (All 14 Audit Gaps)

**Goal:** Implement all 14 missing checks in `verify-gate-evidence.py`, partitioned by priority
(gaps 1–6 retroactive-approval detection first, gaps 7–14 structural/schema second), with a
test for each new check.

**Files to change:**

- `scripts/work-queue/verify-gate-evidence.py` — add the following new functions, in order
  of implementation priority:

  **Priority 1 (retroactive approval detection — gaps 1–6):**
  - `check_approval_ordering()` (gap 1): assert cross-artifact timestamp chain
    `plan-final-review.confirmed_at < claim.claimed_at < execute.executed_at <
    user-review-close.confirmed_at`; Stage 6 cross-review log `review_wrapper_complete`
    timestamp must postdate Stage 5 `reviewed_at`; any inversion → FAIL
  - Midnight UTC rejection (gap 2): FAIL on `reviewed_at` / `confirmed_at` with time
    component exactly `T00:00:00Z` in Stage 5/7/17 artifacts
  - Browser-open to approval elapsed time (gap 3): delta between `opened_at` (browser-open
    YAML) and `reviewed_at` (approval YAML) must be ≥ 300s for all human-gate stages
    (Stages 5, 7, and 17); all violations → FAIL (not WARN)
  - Codex keyword check (gap 4): FAIL when "codex" (case-insensitive) absent from
    `review.md` / `cross-review.yaml` / `cross-review-impl.md`
  - Sentinel value rejection (gap 5): FAIL when `activation.yaml` fields `session_id` or
    `orchestrator_agent` equal `"unknown"`; FAIL when `claim-evidence.yaml` `best_fit_provider`
    or `session_owner` equal `"unknown"` or `route` is empty; `quota_snapshot.pct_remaining`
    null when `status: available` → FAIL
  - Publish commit uniqueness (gap 6): WARN when plan_draft and plan_final share commit hash;
    FAIL when all three stage entries share commit hash

  **Priority 2 (structural/schema checks — gaps 7–14):**
  - stage-evidence path existence (gap 7): for each `evidence:` path in `stage-evidence.yaml`,
    verify file exists on disk; FAIL on first missing path
  - Done+pending-comment contradiction (gap 8): FAIL when stage has `status: done` and
    `comment` contains "pending", "not started", or "TBD" (case-insensitive)
  - Plan publish pre-dates approval (gap 9): FAIL when `user-review-publish.yaml`
    `plan_draft.published_at` < `user-review-plan-draft.yaml` `reviewed_at`
  - Workstation contract hard fail (gap 10): FAIL (not PASS-with-missing) when
    `plan_workstations` or `execution_workstations` absent or empty
  - Reclaim gate n/a (gap 11): emit `n/a` (not WARN) when Stage 18 stage-evidence is `n/a`
    and no reclaim log present; WARN only when reclaim log exists but `reclaim.yaml` absent
  - Claim artifact canonical path (gap 12): check `<assets_root>/claim-evidence.yaml`; retire
    legacy WARN exemption — all WRKs after WRK-285 produce PASS or FAIL on claim gate
  - ISO datetime with time component (gap 13): FAIL on date-only values (`2026-03-07`) in
    any approval artifact timestamp field; require full ISO 8601 with UTC offset
  - Stage 1 user-review-capture.yaml presence check (Phase 1 cross-dependency, gap 14-related):
    check `user-review-capture.yaml` exists before allowing Stage 2 entry; must be non-empty
    with `scope_approved: true` and ISO 8601 `confirmed_at`

  **Codex identity check (R-05 extension):**
  - Cross-review gate must check for "codex" in artifact text AND also verify the `reviewer`
    field in `cross-review.yaml` is not `"claude"` alone — self-review with no Codex is FAIL
    regardless of artifact keyword presence

  **Notes on backward compatibility:**
  - New timestamp ordering checks (gap 1) apply only to WRKs being closed or verified AFTER
    this WRK is deployed; archived WRKs are not retroactively re-verified
  - Sentinel value rejection (gap 5) will surface real claim failures on machines where
    `session-state.yaml` is absent; documented under Risks

- `scripts/work-queue/tests/test_gate_verifier_hardening.py` — new test file, one test class
  per gap:
  - T11: `check_approval_ordering()` FAIL on inverted claim/execute timestamps
  - T12: `check_approval_ordering()` PASS on correctly ordered chain
  - T13: midnight UTC rejection triggers FAIL on Stage 5 artifact
  - T14: midnight UTC rejection PASS on normal ISO timestamp
  - T15: browser-open to approval delta < 300s → FAIL (plan stage)
  - T16: browser-open to approval delta ≥ 300s → PASS
  - T17: browser-open to approval delta < 300s at Stage 17 → FAIL
  - T18: Codex keyword missing from review.md → FAIL
  - T19: Codex keyword present → PASS
  - T20: sentinel `"unknown"` in `session_id` → FAIL
  - T21: sentinel `""` in `route` → FAIL
  - T22: shared commit hash across all three publish stages → FAIL
  - T23: shared commit hash across two stages (plan_draft + plan_final) → WARN
  - T24: stage-evidence references nonexistent path → FAIL
  - T25: done+pending-comment contradiction → FAIL
  - T26: plan publish predates approval → FAIL
  - T27: workstation fields absent → FAIL (not PASS)
  - T28: Stage 18 n/a + no reclaim log → `n/a` (not WARN)
  - T29: claim artifact at legacy path → FAIL; at canonical path → PASS
  - T30: date-only timestamp value → FAIL

**Acceptance criteria:**

- [ ] All 14 gaps implemented in `verify-gate-evidence.py`
- [ ] Codex identity check rejects self-review-only cross-review artifacts
- [ ] Sentinel value `"unknown"` causes FAIL on activation and claim gates
- [ ] Workstation gate is hard FAIL (not PASS-with-missing)
- [ ] Reclaim gate emits `n/a` when Stage 18 is correctly marked `n/a`
- [ ] Claim artifact canonical path is `claim-evidence.yaml` at assets root
- [ ] T11–T30 pass (20 new tests)

---

### Phase 4 — Stage-Start/End Script Extension (R-28 + Stage Contract Enforcement)

**Goal:** Harden `start_stage.py` and `exit_stage.py` with new stage contract enforcement,
human-gate WAIT instructions, stale artifact detection, and Stage 17 field validation;
wire both into `work-queue-workflow/SKILL.md` as mandatory calls.

**Pre-work (required first step):** Review the current scope and implementation of
`start_stage.py` and `exit_stage.py` before writing any code. If the new requirements fit
naturally within their existing patterns and file structure, extend them in-place. Create new
helper scripts only if the current scope cannot accommodate the requirement without a
significant architectural change.

**Files to change:**

- `scripts/work-queue/start_stage.py` — extend (after scope review):
  - Print canonical stage name from stage YAML contract on every invocation (R-28)
  - Check that all required prior-stage exit artifacts exist before printing the stage
    prompt (prior-stage prerequisite check); emit diagnostic if any are missing
  - Print the active stage contract text (from `scripts/work-queue/stages/stage-NN-*.yaml`)
    to stdout so the agent does not rely on memory from session open (R-28)
  - For stages with human gate (1, 5, 7, 17): emit explicit WAIT instruction to stdout:
    "STOP — this is a human gate. Do NOT write approval artifact until user responds."
  - Scan for stale future-stage artifacts (any artifact in stages N+1..N+5 directories
    written in the current session); emit WARNING log entry for each found
  - Regenerate lifecycle HTML at stage entry (`generate-html-review.py --lifecycle WRK-NNN`)
    marking current stage as `in_progress`

- `scripts/work-queue/exit_stage.py` — extend:
  - Stage 17 exit: read `user-review-close.yaml`; BLOCK exit if `reviewer`, `reviewed_at`,
    or `confirmed_at` are empty or `decision` equals `"pending"` (R-13)
  - Stage-evidence incremental gate: enforce that `status: done` is only set after stage
    completion signal recorded; block done+pending-comment pattern (R-12)
  - Regenerate lifecycle HTML at stage exit marking stage as `done` with evidence links

- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — add to §Start-to-Finish Chain:
  - Mandatory call: `uv run --no-project python scripts/work-queue/start_stage.py WRK-NNN N`
    at the beginning of every stage
  - Mandatory call: `uv run --no-project python scripts/work-queue/exit_stage.py WRK-NNN N`
    at the end of every stage (before advancing to N+1)
  - Note: stage-start prints the stage contract; agent must not proceed without reading it

**Tests:**

- `scripts/work-queue/tests/test_stage_scripts.py`
  - T31: `start_stage.py` prints canonical stage name from contract YAML
  - T32: `start_stage.py` FAIL when prior-stage exit artifact missing
  - T33: `start_stage.py` emits WAIT instruction for human-gate stages (1, 5, 7, 17)
  - T34: `start_stage.py` emits no WAIT instruction for auto-proceed stages (e.g. Stage 3)
  - T35: `start_stage.py` detects and logs stale future-stage artifact
  - T36: `exit_stage.py` Stage 17 blocks on empty `confirmed_at`
  - T37: `exit_stage.py` Stage 17 blocks on `decision: pending`
  - T38: `exit_stage.py` Stage 17 passes when all required fields populated
  - T39: `exit_stage.py` blocks `status: done` when done+pending-comment contradiction found

**Acceptance criteria:**

- [ ] `start_stage.py` prints canonical stage name, prior-stage prerequisite check, stage
  contract text, and WAIT instruction for hard-gate stages on every invocation
- [ ] `start_stage.py` scans for and logs stale future-stage artifacts
- [ ] `start_stage.py` regenerates lifecycle HTML at stage entry
- [ ] `exit_stage.py` Stage 17 blocks exit when approval fields empty or `decision: pending`
- [ ] `exit_stage.py` blocks done+pending-comment contradictions in stage-evidence
- [ ] `exit_stage.py` regenerates lifecycle HTML at stage exit
- [ ] `work-queue-workflow/SKILL.md` mandates `start_stage.py` and `exit_stage.py` calls
- [ ] T31–T39 pass (9 new tests)

---

### Phase 5 — Skill Pruning (Work/Workflow Cluster)

**Goal:** Reduce the five oversize work/workflow skills to within the 400-line hard limit,
migrate verbose prose to scripts or reference files, and eliminate contract duplication
across skills using the skill-creator evaluation framework.

**Files to change:**

- `.claude/skills/coordination/workspace/work-queue/SKILL.md` (985 → ≤400 lines):
  - Sections to KEEP: stage contract table (condensed), routing rules, file placement map,
    cross-reference pointers to process.md and scripts
  - Sections to MIGRATE to `scripts/work-queue/references/work-queue-reference.md`:
    verbose per-stage procedural prose, extended routing decision trees, historical
    session design rationale
  - Sections superseded by scripts/gates (remove from SKILL): per-stage artifact checklists
    already enforced by `start_stage.py` / `exit_stage.py` / `verify-gate-evidence.py`
  - Add canonical nomenclature table (session / stage / phase / step / checkpoint / resume
    per thought 12 definitions) — this is new content that must be added, not migrated out
  - Add `stage-gate-policy.yaml` reference link (from Phase 1)

- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` (211 → thin index ≤150 lines):
  - After Phase 1 and Phase 2 additions the SKILL will have grown; prune in same pass
  - Migrate "Practical Lessons" prose to `scripts/work-queue/references/workflow-lessons.md`
  - Keep: §Stage Gate Policy table, §Stage 5/7/17 hard contracts with examples,
    §Start-to-Finish Chain (mandatory script calls added in Phase 4),
    §Orchestrator Team Mandate (Phase 6), §Source of Truth, §Version History
  - Target: 150–200 lines (this SKILL is the primary entrypoint — must stay readable)

- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` (205 → ≤200 lines):
  - Migrate redundant per-stage artifact checklists to reference doc
    (`scripts/work-queue/references/gatepass-artifact-map.md`)
  - Keep: Required Lifecycle Chain, no-bypass rules (updated Phase 1/3), Close Gate Minimum,
    Evidence Locations (updated with `user-review-capture.yaml`)
  - Remove: verbose prose duplicating what `verify-gate-evidence.py` already enforces

- `.claude/skills/workspace-hub/workflow-html/SKILL.md` (572 → ≤400 lines):
  - Migrate design-system CSS documentation block to
    `scripts/work-queue/references/workflow-html-css-reference.md`
  - Keep: Stage evidence sources table (updated with Stage 1 entry), Gate artifact format
    table (updated with `user-review-capture.yaml`), Mandatory usage table (updated with
    Stage 1 HTML trigger), §How to Invoke
  - Remove: inline CSS snippets and colour-palette reference (move to css reference file)

- `.claude/commands/workspace-hub/wrk-resume.md`:
  - Add `version:` field to frontmatter
  - Add step: read and surface `stage-evidence.yaml` on resume (stage status visible to agent)
  - Add step: check stage gate policy context on resume (agent resumes knowing current gate)
  - Add distinction: `/wrk-resume` = session-level context restore; `/work run` = execute
    next stage; both complement each other; resume is always a pre-step before `/work run`
    when resuming a broken session

**Skill pruning rules:**
  - Redundant content (duplicated verbatim in another authoritative location): delete outright
    — do NOT move to `references/`; references/ is for new reference material, not a dump for
    content that no longer needs to exist
  - Content converted to scripts (enforced procedurally by `start_stage.py`, `exit_stage.py`,
    `verify-gate-evidence.py`, etc.): add a single one-line note in `references/` pointing to
    the script path (e.g., `# See scripts/work-queue/start_stage.py — enforces this rule
    programmatically`); do not duplicate the prose

**Skill-creator evaluation per skill** (use `.claude/skills/_internal/builders/skill-creator/SKILL.md`):
  - Run eval/score for each of the 5 skills above
  - Output scorecard to `assets/WRK-1035/evidence/skill-pruning-scorecard.md`
  - Any skill scoring below 60/100 on utility is a retire/merge candidate; document in
    scorecard with recommendation

**Tests:**

- `scripts/work-queue/tests/test_skill_line_counts.py`
  - T40: `work-queue/SKILL.md` ≤ 400 lines
  - T41: `work-queue-workflow/SKILL.md` ≤ 200 lines
  - T42: `workflow-gatepass/SKILL.md` ≤ 200 lines
  - T43: `workflow-html/SKILL.md` ≤ 400 lines
  - T44: `wrk-resume.md` has `version:` field in frontmatter

**Acceptance criteria:**

- [ ] `work-queue/SKILL.md` ≤ 400 lines; includes nomenclature table (session/stage/phase/step)
- [ ] `work-queue-workflow/SKILL.md` ≤ 200 lines; includes Stage Gate Policy table, hard
  contracts for Stages 1/5/7/17, mandatory script calls, Orchestrator Team Mandate
- [ ] `workflow-gatepass/SKILL.md` ≤ 200 lines; no-bypass rules updated
- [ ] `workflow-html/SKILL.md` ≤ 400 lines; Stage 1 entries added to tables
- [ ] `wrk-resume.md` has `version:` field; reads stage-evidence on resume; clarifies
  session-resume vs stage-execute distinction
- [ ] Reference files created for migrated prose content
- [ ] Skill-creator scorecard written to `assets/WRK-1035/evidence/skill-pruning-scorecard.md`
- [ ] T40–T44 pass

---

### Phase 6 — Orchestrator Team Pattern

**Goal:** Document the on-demand TaskCreate pattern as the default for WRK execution, clarify
the scope-discovery-first and conditional-pause triggers, and accurately describe the
`spawn-team.sh` role without mandating it.

**Files to change:**

- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — add §Orchestrator Team Pattern
  section (inserted before §Source of Truth):
  - Hard architectural rule: "No WRK may be executed in a single Claude conversation from
    Stage 1 to Stage 20. Each stage or closely-related stage group must be a separate agent
    task to prevent context rot."
  - **Default pattern — on-demand TaskCreate**: orchestrator stays thin — reads checkpoints,
    makes decisions, delegates heavy work; any subtask requiring reading >3 files or writing
    >50 lines → delegate via TaskCreate. Orchestrator accumulates only summaries, diffs,
    pass/fail signals — never raw file content or full test output.
  - **TeamCreate/spawn-team.sh**: available for pre-planned multi-agent teams (e.g. parallel
    phase execution); NOT mandated. Use when the task set is fully known upfront and parallel
    spawning gives a clear throughput benefit. spawn-team.sh prints a recipe and pre-flight
    checklist — it is a convenience tool, not a required entrypoint.
  - Scope-discovery-first rule: "Discover N items, decide grouping, spawn all at once — do
    NOT incrementally spawn without knowing the full task set"
  - Conditional pause triggers for any auto-proceed stage (R-27 reference): routing
    conflict, scope conflict, risk spike, gate verifier failure, evidence contradiction,
    resource conflict, irreversible state risk
  - Minimum granularity guidance: one agent per stage is the default; sub-stage splits
    allowed when a single stage exceeds ~200 lines of output

- `scripts/work-queue/spawn-team.sh` — add Stage 1 exit gate pre-check:
  - Before printing team recipe, verify `user-review-capture.yaml` exists for the WRK and
    `scope_approved: true` — exit 1 with diagnostic if absent
  - This closes the earliest spawn vector for teams on WRKs that haven't been scope-approved

**Tests:**

- `scripts/work-queue/tests/test_spawn_team.py`
  - T45: `spawn-team.sh` exits 1 when `user-review-capture.yaml` absent
  - T46: `spawn-team.sh` exits 0 when `scope_approved: true` and `confirmed_at` non-empty
  - T47: `spawn-team.sh` exits 1 when `scope_approved: false`

**Acceptance criteria:**

- [ ] `work-queue-workflow/SKILL.md` §Orchestrator Team Pattern section present with
  on-demand TaskCreate as default, TaskCreate/TeamCreate distinction clarified,
  scope-discovery-first rule, and conditional pause triggers (R-27)
- [ ] `spawn-team.sh` validates Stage 1 exit gate before printing team recipe
- [ ] T45–T47 pass

---

## Implementation Sequence

```
Phase 1 (Stage 1 gate + policy table)
    → Phase 2 (retroactive approval prevention — skill contracts + close-item.sh)
        [can begin immediately after Phase 1 completes]
    → Phase 3 (gate verifier hardening — all 14 gaps)
        [Phase 1 must complete first — gap 14 depends on user-review-capture.yaml template]
        [gaps 1–6 (Priority 1) implemented first]
        [gaps 7–14 (Priority 2) implemented second, within same phase]
    → Phase 4 (start_stage.py / exit_stage.py extension)
        [can begin in parallel with Phase 3 Priority 2]
    → Phase 5 (skill pruning)
        [must run AFTER Phases 1, 2, 4 — skill edits consolidate in one pass]
        [do NOT edit SKILL.md piecemeal across phases; accumulate changes and apply together]
    → Phase 6 (orchestrator team mandate)
        [can be drafted in parallel with Phase 5; merge into SKILL.md in same editing pass]
```

**Parallelisation notes:**
- Phases 3 Priority 2 and Phase 4 may proceed in parallel (separate files, no conflicts)
- Phases 5 and 6 SKILL.md edits MUST be applied in a single editing pass to avoid
  merge conflicts and double-counting line budgets
- Test files for each phase can be written in parallel; all tests run together at end

---

## Risks

- **Timestamp ordering enforcement (gap 1) will fail retroactive verification of archived WRKs**
  if `verify-gate-evidence.py` is run against them. Mitigation: add a `--since-wrk` flag that
  limits new checks to WRKs closed after WRK-1035 deployment; archived items are exempt.

- **Codex keyword enforcement (gap 4) combined with Codex unavailability blocking (R-06) may
  deadlock WRKs on ace-linux-1** where Codex interactive terminal is unavailable. Mitigation:
  document the ace-linux-1 Codex constraint in the gate verifier; WRK-1021 (scheduled jobs)
  is the upstream fix for non-interactive Codex availability. WRK-1035 adds the check and
  documents the constraint; it does not solve the underlying machine constraint.

- **Sentinel value rejection (gap 5) will surface real claim failures** on machines where
  `session-state.yaml` is absent and `claim-item.sh` falls back to `"unknown"`. Mitigation:
  Phase 2 must also update `claim-item.sh` to read `$CLAUDE_SESSION_ID` env variable as
  primary source; block claim with diagnostic if env var also absent rather than writing
  sentinel. This is a scope addition to Phase 2 (low risk — shell-level only).

- **`work-queue/SKILL.md` at 985 lines is the most-referenced skill in the cluster.** Any
  content removed must be preserved in reference files with explicit cross-links. A broken
  cross-reference is worse than an oversize file. Mitigation: run `grep -r "work-queue/SKILL.md"`
  across all skills and commands before pruning; update every caller to use the new reference
  path.

- **Stage 1 gate addition changes WRK creation flow for all future WRKs.** Existing WRKs in
  `pending/` do not have `user-review-capture.yaml`. Mitigation: add a migration exemption in
  the gate verifier (same pattern as `stage5-migration-exemption-template.yaml`) covering WRKs
  created before WRK-1035 deployment. Exemption list: all WRKs with `created_at` before
  `2026-03-09T00:00:00Z`.

- **14 gate verifier gaps are all in one 1208-line file.** Adding all 14 checks risks pushing
  the file further past readable size. Mitigation: refactor `verify-gate-evidence.py` into
  sub-modules (`checks/timestamp.py`, `checks/identity.py`, `checks/structure.py`) as part
  of Phase 3; keep the main file as a dispatcher ≤ 150 lines.

- **Phase 5 SKILL pruning risks removing content that agents still need.** Mitigation: before
  any line is deleted from a SKILL, confirm it is either: (a) already enforced by a script
  (and the script is referenced in the SKILL), or (b) duplicated verbatim in the target
  reference file.

---

## Open Questions for User Review (Stage 5) — ALL RESOLVED

1. **Codex unavailability on ace-linux-1** — **RESOLVED**: Hard FAIL with a documented
   ace-linux-1 exemption in the gate verifier. Exemption is removed when WRK-1021 closes and
   provides non-interactive Codex access.

2. **`claim-item.sh` sentinel fix scope** — **RESOLVED**: Include in Phase 2 scope. Low risk
   (pure shell-level) and directly enables gap 5 sentinel rejection.

3. **`verify-gate-evidence.py` modularisation** — **RESOLVED**: Refactor into sub-modules in
   Phase 3 (`checks/timestamp.py`, `checks/identity.py`, `checks/structure.py`). Avoids the
   file crossing 1600 lines with 14 new checks inline.

4. **`/plan` at session start** — **RESOLVED**: Out of scope for WRK-1035. Captured as
   WRK-1042 follow-up (session-start skill is not in the work/workflow cluster this WRK
   targets).

5. **Nomenclature section placement** — **RESOLVED**: Cross-reference only. The canonical
   session/stage/phase/step table lives in `work-queue/SKILL.md`; `work-queue-workflow/SKILL.md`
   carries a one-line cross-reference. Duplication defeats the pruning goal.

6. **`workflow-html/SKILL.md` CSS reference split** — **RESOLVED**: Migrate CSS documentation
   to a reference file. Agents building HTML invoke `workflow-html` skill and follow the
   reference link for CSS specifics.

7. **Migration exemption cutoff** — **RESOLVED**: WRK-ID-based exemption (≤ WRK-1035).
   More stable than time-based; avoids timezone ambiguity.

---

## Tests and Evals

### Unit tests (new test files, all under `scripts/work-queue/tests/`)

| ID | File | What | Scenario | Expected |
|----|------|------|----------|----------|
| T1 | test_stage1_gate.py | Stage 2 entry gate | `user-review-capture.yaml` absent | FAIL |
| T2 | test_stage1_gate.py | Stage 2 entry gate | `scope_approved: true`, `confirmed_at` set | PASS |
| T3 | test_stage1_gate.py | Stage 2 entry gate | `scope_approved: false` | FAIL |
| T4 | test_stage1_gate.py | Template render | All required fields present | PASS |
| T5 | test_retroactive_approval.py | close-item pre-check | `execute.yaml` absent | exit 1 |
| T6 | test_retroactive_approval.py | close-item pre-check | `executed_at` in future | exit 1 |
| T7 | test_retroactive_approval.py | close-item pre-check | `user-review-close.yaml` absent | exit 1 |
| T8 | test_retroactive_approval.py | close-item pre-check | `confirmed_at` < `executed_at` | exit 1 |
| T9 | test_retroactive_approval.py | Approval template | `stage:` field present | PASS |
| T10 | test_retroactive_approval.py | Close template | All fields render | PASS |
| T11 | test_gate_verifier_hardening.py | `check_approval_ordering` | Inverted claim/execute | FAIL |
| T12 | test_gate_verifier_hardening.py | `check_approval_ordering` | Correct order | PASS |
| T13 | test_gate_verifier_hardening.py | Midnight UTC rejection | `T00:00:00Z` in Stage 5 | FAIL |
| T14 | test_gate_verifier_hardening.py | Midnight UTC rejection | Normal ISO timestamp | PASS |
| T15 | test_gate_verifier_hardening.py | Elapsed time check | Delta < 300s, plan stage | FAIL |
| T16 | test_gate_verifier_hardening.py | Elapsed time check | Delta ≥ 300s | PASS |
| T17 | test_gate_verifier_hardening.py | Elapsed time check | Delta < 300s, Stage 17 | FAIL |
| T18 | test_gate_verifier_hardening.py | Codex keyword | "codex" absent | FAIL |
| T19 | test_gate_verifier_hardening.py | Codex keyword | "Codex" present (case) | PASS |
| T20 | test_gate_verifier_hardening.py | Sentinel rejection | `session_id: "unknown"` | FAIL |
| T21 | test_gate_verifier_hardening.py | Sentinel rejection | `route: ""` | FAIL |
| T22 | test_gate_verifier_hardening.py | Commit uniqueness | All 3 stages same hash | FAIL |
| T23 | test_gate_verifier_hardening.py | Commit uniqueness | 2 stages same hash | WARN |
| T24 | test_gate_verifier_hardening.py | Evidence path existence | Nonexistent path | FAIL |
| T25 | test_gate_verifier_hardening.py | Done+pending comment | `status: done` + "pending" comment | FAIL |
| T26 | test_gate_verifier_hardening.py | Publish pre-dates approval | `published_at` < `reviewed_at` | FAIL |
| T27 | test_gate_verifier_hardening.py | Workstation hard fail | Fields absent | FAIL |
| T28 | test_gate_verifier_hardening.py | Reclaim n/a | Stage 18 n/a, no reclaim log | `n/a` |
| T29 | test_gate_verifier_hardening.py | Claim path | Canonical path | PASS; legacy → FAIL |
| T30 | test_gate_verifier_hardening.py | ISO datetime | Date-only value | FAIL |
| T31 | test_stage_scripts.py | `start_stage.py` | Prints stage name | PASS |
| T32 | test_stage_scripts.py | `start_stage.py` | Prior-stage artifact missing | FAIL |
| T33 | test_stage_scripts.py | `start_stage.py` | Human gate stage → WAIT | WAIT printed |
| T34 | test_stage_scripts.py | `start_stage.py` | Auto-proceed stage → no WAIT | No WAIT |
| T35 | test_stage_scripts.py | `start_stage.py` | Stale future artifact | WARNING logged |
| T36 | test_stage_scripts.py | `exit_stage.py` Stage 17 | Empty `confirmed_at` | exit 1 |
| T37 | test_stage_scripts.py | `exit_stage.py` Stage 17 | `decision: pending` | exit 1 |
| T38 | test_stage_scripts.py | `exit_stage.py` Stage 17 | All fields populated | PASS |
| T39 | test_stage_scripts.py | `exit_stage.py` | Done+pending-comment | FAIL |
| T40 | test_skill_line_counts.py | `work-queue/SKILL.md` | Line count | ≤ 400 |
| T41 | test_skill_line_counts.py | `work-queue-workflow/SKILL.md` | Line count | ≤ 200 |
| T42 | test_skill_line_counts.py | `workflow-gatepass/SKILL.md` | Line count | ≤ 200 |
| T43 | test_skill_line_counts.py | `workflow-html/SKILL.md` | Line count | ≤ 400 |
| T44 | test_skill_line_counts.py | `wrk-resume.md` | Has `version:` field | PASS |
| T45 | test_spawn_team.py | `spawn-team.sh` | `user-review-capture.yaml` absent | exit 1 |
| T46 | test_spawn_team.py | `spawn-team.sh` | `scope_approved: true` | exit 0 |
| T47 | test_spawn_team.py | `spawn-team.sh` | `scope_approved: false` | exit 1 |

**Total: 47 new tests across 5 test files.**

### Integration eval (post-implementation, human-run)

- Run `verify-gate-evidence.py WRK-1035` after implementation — all new checks must PASS
  (WRK-1035 itself serves as the first live test of all new gates)
- Open `WRK-1035-lifecycle.html` and confirm Stage 1 entry shows `user-review-capture.yaml`
  as present and `scope_approved: true`
- Run `start_stage.py WRK-1035 17` against a test fixture and confirm WAIT instruction appears
- Run `exit_stage.py WRK-1035 17` against a fixture with `decision: pending` and confirm exit 1
- Confirm `work-queue/SKILL.md` is ≤ 400 lines after pruning with no broken cross-references

---

## Out of Scope

The following items were identified during WRK-1035 planning but are explicitly deferred to
follow-up WRKs:

- **WRK-1039** — Gate verifier hardening Phase 2 (if 14 gaps from Phase 3 are too large for
  one WRK, the overflow items are deferred here; current plan includes all 14 in Phase 3)
- **WRK-1040** — Nomenclature canonicalisation full audit and rename: auditing ALL script field
  names (not just SKILL prose), renaming mismatched env vars, updating stage YAML contracts.
  Phase 5 adds the nomenclature TABLE to `work-queue/SKILL.md`; the full rename/audit is
  WRK-1040 scope. **Note: WRK-1040 nomenclature canonicalisation audit is being completed in
  parallel by a subagent; findings will be integrated into WRK-1035 on return.**
- **WRK-1041** — Lifecycle HTML auto-refresh and on-demand `/work html WRK-NNN` command;
  `<meta http-equiv="refresh">` or file-watch approach. Phase 4 in this WRK regenerates HTML
  at stage-start/end; on-demand and auto-refresh are WRK-1041 scope.
- **WRK-1042 (to capture)** — `/plan` at session start as mandatory step in session-start skill
  when a plan file exists (thought 8)
- **WRK-1043 (to capture)** — Statusline second segment showing active WRK + current stage
  (thought 14): `[WRK:WRK-1035 · Stage 4 Plan Draft]` from `active-wrk` + `checkpoint.yaml`
- **WRK-1044 (to capture)** — Human_SESSION detection logic: block agent from seeking user
  review when not in a Human_SESSION context (thought 2, missing detection rule)
- **Codex non-interactive availability on ace-linux-1** — upstream fix deferred to WRK-1021
  (scheduled jobs); WRK-1035 adds the Codex keyword check and documents the ace-linux-1
  constraint; does not resolve the machine-level terminal requirement
- **`/checkpoint` naming collision resolution** (thought 6): deciding whether interactive-session
  checkpoint and stage checkpoint are the same or different commands; deferred to WRK-1040
  (nomenclature audit)
- **Broad skill inventory pruning across all skills** — handled by nightly curation job
  (WRK-1009 / `skill-curation-nightly.sh`); Phase 5 targets only the work/workflow cluster
- **`wrk-lifecycle-testpack/SKILL.md` test suite contract update** — adding Stage 1 gate tests
  and gap-specific test templates; noted as a pruning candidate in resource-intelligence.yaml
  but deferred to avoid scope creep; capture as WRK-1045
- **WRK-1036 findings integration** — WRK-1036 is in progress (stale team agents cleanup);
  any findings that affect WRK-1035 scope will be assessed at Stage 7 plan-final review
