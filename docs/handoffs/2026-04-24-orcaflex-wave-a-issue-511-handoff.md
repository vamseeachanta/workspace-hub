# Execution Handoff — OrcaFlex Wave A continuation (#511)

> **Prior session:** 2026-04-24 closed #510 plan-scope complete; recommended Path 2 (fresh session for #511) due to T1→T2 complexity jump.
> **Prior handoff (full Wave A+B+C):** `docs/handoffs/2026-04-24-orcaflex-orcawave-batch-execution-handoff.md`
> **Session-to-session state:** #510 closed + 3 follow-ups filed (#529/#530/#531). Branch `issue-510-fix-test-drift` pushed to digitalmodel origin at `190555410` but NOT yet merged to `main` — pending user PR merge.

---

## Handoff Prompt (copy-paste into a fresh session)

```
You are the execution-phase operator for OrcaFlex Wave A issue #511 from the 2026-04-24 overnight batch.

CURRENT STATE:
- #510 (T1 test-drift) completed in the prior session. Branch `issue-510-fix-test-drift` pushed to digitalmodel origin at `190555410`, NOT YET MERGED to main — pending user PR merge. Base your #511 work on `origin/main` regardless; #510's test-side fixes do not collide with #511's src-side work.
- 3 follow-up issues filed for #510's remaining failures: #529 (convert_batch parallel stats bug), #530 (fixture-scoping refactor), #531 (out-of-scope umbrella for 9 pre-existing failures). Ignore these for #511 — they are tracked separately and NOT in scope.
- Workspace-hub main HEAD is `0e29f923d` (includes plan-index entry for #510).
- #511 is currently `status:plan-approved` and OPEN in vamseeachanta/digitalmodel.

CONTEXT TO READ FIRST (in order):
1. docs/plans/2026-04-24-issue-511-orcaflex-campaign-spec-generation.md — full plan (T2, extends CampaignMatrix)
2. scripts/review/results/2026-04-24-plan-511-adversarial.md — adversarial review findings (defect checklist)
3. scripts/review/results/2026-04-24-plan-511-disagreement.md — cross-reviewer disagreement summary
4. scripts/review/results/2026-04-24-plan-511-{claude,codex,gemini}.md — per-provider reviews
5. digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py — primary extension target (CampaignMatrix, CampaignSpec, CampaignGenerator, _apply_overrides all live here)
6. digitalmodel/src/digitalmodel/solvers/parametric_spec_generator.py — OrcaWave sibling (source of `_set_nested` pattern to port, re-implemented as Pydantic-aware setter per the plan)
7. digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/cli.py:293-358 — `cmd_campaign` CLI to extend with `--spec-only` flag

AGENT TEAM STRATEGY (5 phases):

Phase 1 — Parallel exploration (spawn 3 agents in ONE message with parallel Agent tool calls):
- Agent A (feature-dev:code-explorer): Deep-dive on digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/schema/campaign.py. Map CampaignMatrix, CampaignSpec, CampaignGenerator, _apply_overrides signatures + execution paths. Return structured findings listing exact extension points (line numbers, method boundaries, Pydantic model hooks) where new `ParameterSweep`, generic dotted-path applier, and `spec_only` mode must integrate.
- Agent B (feature-dev:code-explorer): Analyze digitalmodel/src/digitalmodel/solvers/parametric_spec_generator.py. Understand the OrcaWave `_set_nested` helper, dataclass-based sweeps (FrequencySweep/HeadingSweep/HullParameterSweep), and the dotted-path UX. Document what logic is reusable as-is vs. what needs re-implementation as Pydantic-aware (re-validating through ProjectInputSpec, not raw dict mutation).
- Agent C (Explore, thorough): Enumerate existing tests around campaign.py and parametric spec generators: digitalmodel/tests/solvers/orcaflex/modular_generator/schema/test_campaign.py, digitalmodel/tests/solvers/orcaflex/modular_generator/test_campaign_generator.py, digitalmodel/tests/solver/test_parametric_spec_generator.py. Report current test coverage, naming conventions, fixture patterns, and which test classes are the natural expansion surface for new `ParameterSweep` + `spec_only` tests.

Phase 2 — Design synthesis (single agent, after Phase 1 completes):
- feature-dev:code-architect: Synthesize Phase 1 findings into an architecture blueprint covering:
  (a) `ParameterSweep` Pydantic model shape (`parameter: str`, `values: list[Any]`, optional `alias: str`)
  (b) Generic dotted-path applier — Pydantic-aware (re-validates through ProjectInputSpec, not raw dict mutation)
  (c) `spec_only: bool=False` path on CampaignGenerator — emits `run_XXX/spec.yml` per combination, no `master.yml`/`includes/`
  (d) Sweep-parameter resolver + combinatorial-explosion preflight (warn/error on large combination products)
  (e) LHS + OAAT combination modes — DECIDE dep choice (see Key Decisions below)
  Output: step-by-step implementation sequence with files-to-touch, order of feature slices, test-first ordering.

Phase 3 — TDD implementation (main session, no subagents for this phase):
- Invoke skill superpowers:test-driven-development BEFORE writing implementation code.
- RED: write failing tests for each new feature (one slice at a time).
- GREEN: minimum implementation per slice.
- Refactor as needed per plan.
- One feature slice per commit (atomic). Commit messages reference #511 and the slice (e.g., `feat(#511): add ParameterSweep Pydantic model`).

Phase 4 — Verification (parallel):
- Foreground: run full `uv run pytest digitalmodel/tests/solvers/orcaflex/ -q` — confirm no regression vs. the #510-post-fix baseline (10 failed, 966 passed, 154 skipped, 3 errors). NEW failures indicate #511 regressions; investigate before push.
- Spawn `pr-review-toolkit:code-reviewer` agent against the diff before pushing — independent read.
- Spawn `pr-review-toolkit:pr-test-analyzer` if test coverage on new features needs a second read.

Phase 5 — Close:
- Push branch `issue-511-campaign-spec-generation` to digitalmodel origin.
- Post implementation-complete evidence comment on #511 (never self-label `status:done` per feedback_never_offer_to_self_label_plan_approved — leave at `status:working`, surface evidence, await user sign-off).
- Update workspace-hub docs/plans/README.md with the #511 row (separate commit on workspace-hub main, same-session or hand off).

PROTOCOLS:
1. TDD MANDATORY: failing tests first, then implementation. Follow digitalmodel/tests/ conventions and `uv run pytest` for validation.
2. Read r2-adversarial review before implementing — it documents any r2-introduced defects to avoid.
3. Atomic commits referencing issue number per feature slice.
4. Label transition `status:plan-approved → status:working` at kickoff. NEVER to `status:done` without user sign-off.
5. If implementation reveals the plan is wrong (new defect found during coding), STOP — create `status:plan-review` transition for user re-approval. Do not silently re-plan.
6. Create clean branch from `origin/main` of digitalmodel (NOT from #510's branch).

KEY DECISIONS TO CONFIRM WITH USER AT KICKOFF:
Post both of these in the kickoff comment and wait for user sign-off before implementing (do not decide unilaterally):

- LHS dep choice: `scipy.stats.qmc` (already in dep tree, low risk, stdlib-flavored) vs `pyDOE2` (new dep, richer DOE primitives but adds a dependency). Plan defers to implementer. Surface explicitly.
- Dotted-path `sweeps:` validation strategy: full Pydantic re-validation per combination (strict correctness, slower — plan's prescription) vs. pre-flight validation + raw dict mutation (faster, matches OrcaWave sibling pattern). Plan prescribes Pydantic-aware; confirm this is still the direction given performance implications for large sweeps (plan's own example yields 60 combos; real campaigns could be 680+).

KNOWN ENVIRONMENTAL HAZARDS (from prior session):
- Auto-sync can silently push commits after `[rejected]` push errors — verify with `git rev-parse HEAD origin/main` before retrying (per feedback_autosync_silent_pusher).
- Multi-session git-lock contention on this workstation; single-session work is the safe default.
- digitalmodel full-suite `tests/solvers/orcaflex/` takes ~11-14 min. Budget at least 2 full runs.
- `uv run` recompiles bytecode (~1:40s) when env switches; first pytest of session adds this overhead.
- Baseline `tests/solvers/orcaflex/` after #510 edits: `10 failed, 966 passed, 154 skipped, 3 errors`. Any NEW failures from #511 work are regressions. The 10 existing failures are tracked in #529/#530/#531 — do NOT fix them under #511.
- Prior session's workspace-hub had uncommitted edits (scripts/analysis/provider_session_ecosystem_audit.py and untracked plan files #2480/#2481/#2482). Respect those — they belong to another session. When committing the #511 plan-index row, use `git checkout origin/main -- docs/plans/README.md` first to isolate from prior-session contamination, then re-apply your edit.

YOUR FIRST ACTION:
1. Confirm you have read the plan + adversarial review + the 7 context files above.
2. Post kickoff comment on #511 transitioning `status:plan-approved → status:working`, citing the 2 Key Decisions for user confirmation.
3. Spawn Phase 1 exploration agents IN PARALLEL (single message, 3 Agent tool calls).
4. Synthesize Phase 1 findings + user-confirmed decisions before invoking Phase 2 architect.
5. Do NOT start Phase 3 TDD until user has signed off on both Key Decisions.

ARTIFACTS (canonical paths):
- Plan: workspace-hub/docs/plans/2026-04-24-issue-511-orcaflex-campaign-spec-generation.md
- Review artifacts (5): workspace-hub/scripts/review/results/2026-04-24-plan-511-{claude,codex,gemini,adversarial,disagreement}.md
- Prior session handoff (batch parent): workspace-hub/docs/handoffs/2026-04-24-orcaflex-orcawave-batch-execution-handoff.md
- Prior session state handoff (this doc): workspace-hub/docs/handoffs/2026-04-24-orcaflex-wave-a-issue-511-handoff.md
- #510 completion evidence: vamseeachanta/digitalmodel#510 (closed, user-verified `status:done`)
- #510 follow-ups: #529, #530, #531 (out of scope for #511)
```

---

## Notes for the handoff operator (metadata — do NOT paste into prompt)

### Why Path 2 (fresh session, not continuation)

The prior session executed #510 end-to-end and ran into meaningful-but-bounded context spend:
- 2 full pytest suites on `tests/solvers/orcaflex/` (~25 min wall-clock total)
- 4 separate git push+verify cycles across 2 repos
- 5 GitHub comments posted (kickoff, completion-evidence, close-summary, follow-ups cross-ref)
- 3 follow-up issues filed
- 1 plan-index row added, cleaned from prior-session contamination, committed, pushed

A T2 feature with src/ touches and 5 new components (ParameterSweep model, dotted-path applier, spec_only mode, preflight, LHS/OAAT modes) requires its own fresh exploration → design → TDD cycle. Starting it with a fatigued context would risk either incomplete exploration (missing the real extension points in campaign.py) or TDD corners cut during implementation.

### Why agent-team phases (not single-agent implementation)

Phase 1's parallel exploration is genuinely independent work — three agents reading three different surfaces (target file, sibling-pattern file, test landscape) in parallel is strictly faster and keeps the main session's context clean for the architect-phase synthesis. Phase 2's single-architect call produces a traceable blueprint that anchors Phase 3's TDD. Phase 4's code-review + test-analysis agents serve as the "second read" before push.

This pattern fits `superpowers:dispatching-parallel-agents` ("2+ independent tasks that can be worked on without shared state or sequential dependencies"). Phase 3 TDD intentionally stays in the main session — TDD requires tight hand-eye coupling between failing test, implementation, and verification.

### Session-to-session durable feedbacks applied in the handoff prompt

- `feedback_never_offer_to_self_label_plan_approved` — never self-approve or pre-authorize the `status:done` transition; user gate is load-bearing across session boundaries.
- `feedback_gh_issue_close_silent_comment_drop` — post close/summary comments BEFORE closing an issue.
- `feedback_autosync_silent_pusher` — `[rejected]` pushes may be silently resolved by auto-sync; verify reflog + `git rev-parse` before retrying.
- `feedback_check_parallel_work` — scan in-flight sessions at start.
- `feedback_plan_past_tense_artifact_claims` — future tense for proposed work; present/past for confirmed state only.
- `feedback_reflog_as_ground_truth` — use reflog + `git status` to verify state, not just `[rejected]` messages.

### Wave A remaining after #511

- **#504** — OrcaFlex buoys builder refactor (T2, isolated file, use `BuoysOrchestrator` approach B per original batch handoff). This is a separate fresh session after #511 completes.

### Review artifact health at time of handoff write

- `plan-511-claude.md` — APPROVE or MINOR (confirm at session start)
- `plan-511-codex.md` — verdict unverified (prior session noted Codex/Gemini fanout script issues in the original batch handoff — the adversarial review file is the authoritative cross-review artifact for #511)
- `plan-511-gemini.md` — same caveat
- `plan-511-adversarial.md` — authoritative defect checklist; READ FIRST alongside the plan
- `plan-511-disagreement.md` — verdict-split summary; skim for any load-bearing dissent

### Batch-parent linkage

#511 is 1 of 10 issues in the 2026-04-24 OrcaFlex/OrcaWave overnight batch:
- Wave A: #510 (done), **#511 (this handoff)**, #504 (next fresh session)
- Wave B: #515, #500, #501
- Wave C: #282, #279, #486, #503

The original batch handoff at `docs/handoffs/2026-04-24-orcaflex-orcawave-batch-execution-handoff.md` covers all 10; this handoff narrows scope to #511 for a single fresh session.
