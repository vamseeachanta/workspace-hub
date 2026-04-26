# Plan for #2409: feat(release-readiness): fixture-backed golden-task corpus for model-release comparisons

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2409
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2409-claude.md | scripts/review/results/2026-04-26-plan-2409-codex.md | scripts/review/results/2026-04-26-plan-2409-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `tests/fixtures/` already exists at the workspace-hub root with sub-directories `readiness/`, `embeddings/`, `test_vectors/`. `tests/fixtures/model_release_battery/` does **not** yet exist (verified via `ls -la` on 2026-04-26).
- Found: `tests/fixtures/readiness/` carries five YAML fixtures (`linux-valid.yaml`, `windows-valid.yaml`, `invalid-access-mode.yaml`, `invalid-timestamp.yaml`, `missing-required-field.yaml`) demonstrating an existing valid/invalid YAML fixture pattern this corpus will replicate for golden-task expected outcomes.
- Found: `tests/ecosystem-sync/golden/` contains `empty.md` and `with_signals.md` — prior precedent in the repo for committing "golden" reference outputs alongside tests.
- Found: `scripts/review/plan-review-fanout.sh`, `scripts/review/plan-review-prompt.md`, `scripts/review/results/` — the adversarial-review surface this corpus will need to mirror when fixturing the "adversarial review" workflow class.
- Found: `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` (issue #2408, version 1.0.0) defines the five readiness dimensions — Context-Budget Awareness, Truncation-Safe Artifact Design, Machine-Readable vs Prose, Prompt-Pack Portability, Discoverability. The corpus MUST honor dimensions 1 (Context-Budget) and 2 (Truncation-Safe) per #2409 acceptance criteria.
- Found: `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` defines provider-owned vs repo-owned drift split — relevant because expected-output drift (from model improvement) MUST be classified the same way to prevent silent baseline-staleness rot.
- Gap: no fixture format, no scoring/normalization spec, no CI hook, and no per-workflow-class baseline directory tree exists today.

### Standards
| Standard | Status | Source |
|---|---|---|
| Model-release readiness contract (workspace-hub scope) | done | `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` (#2408) |
| Model-release upgrade playbook | done | `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` (#2408) |
| Smoke-battery runner contract | not yet built — sibling | issue #2410 (see "Documents consulted") |
| Intelligence retrieval contract | done | issue #2208 (CLOSED) — applied to this plan's evidence section |
| Coding-style: path handling + harness-file size | done | `.claude/rules/coding-style.md` |
| Patterns: enforcement gradient (prose → script → hook) | done | `.claude/rules/patterns.md` — fixture validation will target Tier-2 (script) per the gradient |

### LLM Wiki pages consulted
- No relevant wiki pages. This is harness/control-plane work; wiki coverage is reserved for engineering-domain knowledge per `docs/plans/README.md` issue-class table.

### Documents consulted
- Issue #2409 body — explicit deliverables (`tests/fixtures/model_release_battery/`, expected-output baselines, scoring/normalization), explicit acceptance criteria (5 workflow classes, baseline shape, scoring reproducible, context-budget aware, truncation-safe).
- Parent issue #2399 — defines the broader readiness program; lists the 5 workflow classes (planning, adversarial review, repo navigation, code modification discipline, session handoff integrity) that this corpus must cover. Body states "fixture-backed golden-task corpus" was the evaluation-corpus slice split out into #2409.
- Sibling issue #2410 — defines the runner/schema contract. The corpus produced here MUST be consumable by the schema #2410 will define, so the file layout and YAML keys must be runner-agnostic and minimally opinionated to avoid pre-empting #2410's design space.
- Sibling issue #2408 (`status:plan-approved`) — the workspace-hub-only readiness contract and playbook. Approved 2026-04-23. Establishes the dimension vocabulary the corpus's "context-budget aware + truncation-safe" criteria reference.
- Prior plan `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md` — names `tests/fixtures/model_release_battery/` as the corpus location; this plan inherits that path decision.
- Prior plan `docs/plans/2026-04-20-issue-2408-workspace-hub-model-release-readiness-contract-and-upgrade-playbook.md` — already-landed approval; corpus must not contradict its scope-stop line.
- Issues #1466–#1470 (CLOSED, harness-evals thread) — historical evaluation pattern: each tool was scored against existing GSD/Superpowers, with explicit "decision" outputs (CHERRY-PICK / EXTRACT / SKIP). The corpus will reuse the explicit-decision pattern for adversarial-review workflow-class baselines (verdict ∈ {APPROVE, MINOR, MAJOR}). #1470 contributed the daily-update cron pattern relevant to baseline-refresh cadence.
- Memory note `project_ai_harness_evaluations` — points to #1466–#1470 as the canonical eval pattern.
- Memory note `data_format_guidelines` — YAML default for agent-facing structured data; JSON only for machine-consumed tool output. Drives the format choice below.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26 via `gh issue view`):
- `#2409` — OPEN — feat(release-readiness): fixture-backed golden-task corpus for model-release comparisons
- `#2399` — OPEN — feat(ai-orchestration): define next-model-release readiness contract for repo ecosystem
- `#2408` — OPEN — feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook (status:plan-approved)
- `#2410` — OPEN — feat(release-readiness): smoke-battery schema and runner contract (no runner implementation)
- `#2411` — OPEN — feat(release-readiness): tier-1 provider entrypoint and parity surface inventory
- `#2412` — OPEN — feat(release-readiness): deterministic follow-up issue creation and dedup policy
- `#2208` — CLOSED — feat(workflow): require intelligence retrieval contract in GitHub issue planning/execution/review
- `#1466`–`#1470` — CLOSED — AI harness evaluation thread (GStack/Hermes/Paperclip/Superpowers/harness-update-cron)

**File existence** (`ls -la` 2026-04-26):
- EXISTS: `/mnt/local-analysis/workspace-hub/tests/fixtures/` (empty `.gitkeep` + sub-dirs)
- EXISTS: `/mnt/local-analysis/workspace-hub/tests/fixtures/readiness/` (5 YAML files, valid/invalid pattern reference)
- EXISTS: `/mnt/local-analysis/workspace-hub/tests/ecosystem-sync/golden/` (precedent for "golden" output naming)
- EXISTS: `/mnt/local-analysis/workspace-hub/docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md`
- EXISTS: `/mnt/local-analysis/workspace-hub/docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md`
- EXISTS: `/mnt/local-analysis/workspace-hub/scripts/review/plan-review-prompt.md` (reference adversarial stance contract)
- MISSING (this plan creates): `/mnt/local-analysis/workspace-hub/tests/fixtures/model_release_battery/`
- MISSING (this plan creates): `/mnt/local-analysis/workspace-hub/scripts/release_readiness/score_battery.py`
- MISSING (sibling — created by #2410): `/mnt/local-analysis/workspace-hub/docs/standards/MODEL_RELEASE_SMOKE_RUNNER_CONTRACT.md`
- MISSING (sibling — created by #2410): `/mnt/local-analysis/workspace-hub/config/ai/model-release-smoke-battery.yaml`

**Line excerpts** — readiness contract dimensions 1 & 2 (lines 45–60 of `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md`):
```
### 1. Context-Budget Awareness
Every readiness standard or playbook introduced under this contract MUST state
its intended read budget (in lines, tokens, or fractions of the consumer's
context window) and MUST fit within it.
### 2. Truncation-Safe Artifact Design
Artifacts MUST assume the reader may receive only the first N kilobytes.
- Identity (title, version, scope, cross-references) MUST appear in the first
  500 bytes.
- Normative requirements inside a section MUST precede explanatory or
  motivational prose for that same section.
```
These two clauses bind the corpus design — every fixture file MUST open with an identity block in the first 500 bytes and MUST declare its read budget.

**Gap proofs**:
- `ls /mnt/local-analysis/workspace-hub/tests/fixtures/model_release_battery 2>&1` → "No such file or directory" → confirms the corpus does not yet exist.
- `find /mnt/local-analysis/workspace-hub -maxdepth 5 -name '*battery*' 2>/dev/null` → returns nothing under `tests/` → confirms no prior battery corpus exists.
- `ls /mnt/local-analysis/workspace-hub/scripts/release_readiness 2>&1` → "No such file or directory" → confirms no scoring script directory exists.

Distinct sources cited above: 9 (issue body #2409 + parent #2399 + siblings #2408/#2410 + harness-eval thread #1466–#1470 + retrieval-contract #2208 + readiness contract standard + upgrade playbook standard + memory `data_format_guidelines` + memory `project_ai_harness_evaluations`). Minimum 3 satisfied.

### Gaps identified
- No fixture directory exists at `tests/fixtures/model_release_battery/`.
- No baseline file format is defined for any of the 5 workflow classes.
- No scoring/normalization rubric is documented or executable.
- No CI integration story exists — fixture validation will not run on PRs without one.
- No baseline-drift policy: how does the corpus distinguish "model regressed" from "expected output is now stale because the model genuinely improved"?
- No truncation-safety guarantee on fixture inputs themselves — large inputs could blow context budgets when fed to a real provider.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-26-issue-2409-fixture-backed-golden-task-corpus.md` |
| Corpus root README | `tests/fixtures/model_release_battery/README.md` |
| Corpus schema doc (in-tree, runner-agnostic) | `tests/fixtures/model_release_battery/SCHEMA.md` |
| Workflow-class fixtures | `tests/fixtures/model_release_battery/<class>/<task-id>/` (5 classes × ≥3 tasks each) |
| Scoring rubric (per class) | `tests/fixtures/model_release_battery/<class>/RUBRIC.yaml` |
| Battery-wide normalization rules | `tests/fixtures/model_release_battery/NORMALIZATION.yaml` |
| Baseline-drift policy | `tests/fixtures/model_release_battery/DRIFT_POLICY.md` |
| Validation script | `scripts/release_readiness/validate_battery_fixtures.py` |
| Scoring script (offline) | `scripts/release_readiness/score_battery.py` |
| Test suite | `tests/release_readiness/test_battery_fixtures.py` |
| CI hook | `.github/workflows/validate-battery-fixtures.yml` |
| Plan review — Claude | `scripts/review/results/2026-04-26-plan-2409-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-26-plan-2409-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-26-plan-2409-gemini.md` |
| Docs index update | `docs/plans/README.md` |

---

## Deliverable

A committed `tests/fixtures/model_release_battery/` corpus carrying ≥3 fixtures per workflow class across the 5 required classes, each with input + expected-output baseline + per-class rubric, plus a validation/scoring script and CI hook that fail-close on schema violations, so any future model-release comparison run produces a reproducible delta against committed expected outcomes rather than against agent-narrated prose.

---

## Pseudocode

```
# Fixture directory layout (one per workflow class)
tests/fixtures/model_release_battery/
  README.md               # identity block + read budget + class index
  SCHEMA.md               # runner-agnostic fixture schema (referenced by #2410)
  NORMALIZATION.yaml      # whitespace/casing/path-rewrite rules applied before scoring
  DRIFT_POLICY.md         # how to refresh baselines without silent rot
  issue_planning/
    RUBRIC.yaml           # weights + partial-credit definitions for this class
    task-001-trivial-typo-fix/
      input.yaml          # issue body, repo state hints, complexity hint
      expected.yaml       # baseline plan structure (sections, evidence-source count)
      meta.yaml           # context-budget cap, truncation cutoffs, last-validated-against
    task-002-standard-feature/
    task-003-cross-provider-review-routing/
  adversarial_review/
    RUBRIC.yaml
    task-001-approve-with-evidence/
    task-002-major-on-missing-tests/
    task-003-minor-on-prose-only-evidence/
  repo_navigation/
    RUBRIC.yaml
    task-001-locate-existing-module/
    task-002-find-non-existent-feature/  # negative case: must say "not found"
    task-003-disambiguate-similarly-named-modules/
  code_modification_discipline/
    RUBRIC.yaml
    task-001-edit-without-deleting-imports/
    task-002-respect-path-handling-rule/
    task-003-respect-harness-file-size-cap/
  session_handoff_integrity/
    RUBRIC.yaml
    task-001-handoff-preserves-todos/
    task-002-handoff-includes-blocker-state/
    task-003-handoff-flags-stale-marker-drift/

# Each input.yaml carries (truncation-safe identity block first):
#   schema_version: "1.0"
#   class: <one of 5>
#   task_id: <stable string>
#   read_budget_tokens: <integer>
#   prompt: |
#     <truncation-tested prompt body>
#   inputs:
#     - role: system | user | tool
#       content: ...

# Each expected.yaml is a STRUCTURED baseline, not free prose:
#   schema_version: "1.0"
#   required_sections: [list of named headings the answer MUST contain]
#   forbidden_substrings: [list — e.g., absolute paths in path-handling test]
#   required_substrings_any: [list — at least one match required]
#   numerical_assertions: []  # empty for non-numeric workflows
#   verdict: APPROVE | MINOR | MAJOR    # adversarial_review only
#   max_output_tokens: <integer>        # truncation safety bound

# Scoring (score_battery.py):
function score_task(actual_output, expected, rubric, normalization):
    actual_normalized = apply_normalization(actual_output, normalization)
    score = 0
    for section in expected.required_sections:
        if section in actual_normalized: score += rubric.weights.required_section
    for sub in expected.required_substrings_any:
        if sub in actual_normalized: score += rubric.weights.required_substring; break
    for sub in expected.forbidden_substrings:
        if sub in actual_normalized: score -= rubric.weights.forbidden_substring
    if expected.has("verdict"): score += rubric.weights.verdict_match if matches else -X
    return clamp(score, 0, rubric.max_score)

# Validation (validate_battery_fixtures.py):
for each task directory:
    assert input.yaml, expected.yaml, meta.yaml exist
    assert schema_version is current
    assert input.read_budget_tokens <= ECOSYSTEM_BUDGET_CAP
    assert expected.max_output_tokens <= 4096  # truncation safety
    assert RUBRIC.yaml exists at class root
    assert identity block in first 500 bytes of every YAML
exit 1 if any assertion fails

# CI hook calls validate_battery_fixtures.py on any path under
# tests/fixtures/model_release_battery/**
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/fixtures/model_release_battery/README.md` | identity + read-budget + class index (Dimension 1) |
| Create | `tests/fixtures/model_release_battery/SCHEMA.md` | runner-agnostic fixture schema |
| Create | `tests/fixtures/model_release_battery/NORMALIZATION.yaml` | whitespace/path/casing pre-score normalization |
| Create | `tests/fixtures/model_release_battery/DRIFT_POLICY.md` | distinguishes baseline-staleness from regression |
| Create | `tests/fixtures/model_release_battery/issue_planning/RUBRIC.yaml` | scoring weights for this class |
| Create | `tests/fixtures/model_release_battery/issue_planning/task-001..003/` | 3 fixtures (input/expected/meta) |
| Create | `tests/fixtures/model_release_battery/adversarial_review/RUBRIC.yaml` | scoring weights for verdict-bearing class |
| Create | `tests/fixtures/model_release_battery/adversarial_review/task-001..003/` | 3 fixtures, one per verdict (APPROVE/MINOR/MAJOR) |
| Create | `tests/fixtures/model_release_battery/repo_navigation/RUBRIC.yaml` | scoring weights including negative-case (not-found) |
| Create | `tests/fixtures/model_release_battery/repo_navigation/task-001..003/` | 3 fixtures incl. negative case |
| Create | `tests/fixtures/model_release_battery/code_modification_discipline/RUBRIC.yaml` | scoring weights with forbidden-substring emphasis |
| Create | `tests/fixtures/model_release_battery/code_modification_discipline/task-001..003/` | 3 fixtures bound to coding-style.md rules |
| Create | `tests/fixtures/model_release_battery/session_handoff_integrity/RUBRIC.yaml` | scoring weights for handoff completeness |
| Create | `tests/fixtures/model_release_battery/session_handoff_integrity/task-001..003/` | 3 fixtures incl. stale-marker drift |
| Create | `scripts/release_readiness/validate_battery_fixtures.py` | schema/budget/identity-block validator |
| Create | `scripts/release_readiness/score_battery.py` | offline scorer over actual_output JSONL |
| Create | `tests/release_readiness/test_battery_fixtures.py` | TDD tests for validator + scorer |
| Create | `.github/workflows/validate-battery-fixtures.yml` | CI hook firing on fixture path changes |
| Update | `docs/plans/README.md` | add this plan to index |
| Update | `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` | add Discoverability anchor pointing to corpus README (Dimension 5) |
| Update | `AGENTS.md` | add discoverability pointer to the corpus per readiness contract Dimension 5 |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_corpus_has_all_five_workflow_classes` | each required class directory exists | `tests/fixtures/model_release_battery/` | 5 class subdirs present |
| `test_each_class_has_minimum_three_fixtures` | task count threshold | each class subdir | ≥3 task-*/ subdirs |
| `test_each_fixture_has_input_expected_meta` | required files per task | each task subdir | `input.yaml`, `expected.yaml`, `meta.yaml` exist |
| `test_each_class_has_rubric` | rubric is per-class, not global | each class subdir | `RUBRIC.yaml` exists with `weights:` and `max_score:` keys |
| `test_identity_block_in_first_500_bytes` | Dimension 2 (truncation-safe) | every fixture YAML | first 500 bytes contain `schema_version`, `class`, `task_id` |
| `test_input_read_budget_under_cap` | Dimension 1 (context-budget) | every `input.yaml` | `read_budget_tokens` ≤ ecosystem cap (default 16K) |
| `test_expected_max_output_tokens_under_cap` | truncation safety on output side | every `expected.yaml` | `max_output_tokens` ≤ 4096 |
| `test_adversarial_review_fixtures_cover_all_verdicts` | verdict distribution | adversarial_review class | at least one each of APPROVE/MINOR/MAJOR |
| `test_repo_navigation_includes_negative_case` | not-found discipline | repo_navigation class | at least one fixture with `expected.verdict == NOT_FOUND` or empty `required_substrings_any` + non-empty `forbidden_substrings` |
| `test_code_modification_fixtures_bind_to_coding_style_rules` | rules are referenced not copied | code_modification_discipline | each `expected.yaml` cites a `.claude/rules/coding-style.md` clause id |
| `test_session_handoff_includes_drift_case` | stale-marker drift coverage | session_handoff_integrity | at least one fixture targets stale-marker / approval-drift handling |
| `test_score_battery_deterministic` | scorer reproducibility | same actual_output run twice | identical score |
| `test_score_battery_normalization_idempotent` | normalization safety | normalize(normalize(x)) | == normalize(x) |
| `test_score_battery_partial_credit` | partial credit shape | partial-match actual | score ∈ (0, max_score) |
| `test_validate_battery_fixtures_fails_on_missing_field` | fail-closed on schema breach | corrupted fixture | exit 1 |
| `test_drift_policy_documents_refresh_cadence` | DRIFT_POLICY.md is non-empty + names cadence | DRIFT_POLICY.md | mentions cadence + ownership + versioning |
| `test_ci_hook_runs_validator` | `.github/workflows/validate-battery-fixtures.yml` invokes the validator on fixture-path changes | workflow YAML | references `validate_battery_fixtures.py` |

---

## Acceptance Criteria

- [ ] `tests/fixtures/model_release_battery/` exists with all 5 workflow-class subdirectories.
- [ ] Each workflow class has ≥3 task fixtures (target ≥3 per acceptance, designed to scale to 5+ without schema change — see Adversarial Review for the "are 5 enough?" question).
- [ ] Every task fixture has `input.yaml`, `expected.yaml`, and `meta.yaml`.
- [ ] Every class has a `RUBRIC.yaml` defining weights and `max_score`.
- [ ] `NORMALIZATION.yaml` defines whitespace/path/casing rules applied before scoring.
- [ ] `DRIFT_POLICY.md` defines how to refresh baselines without silently masking regression.
- [ ] Identity block (`schema_version`, `class`, `task_id`) appears in the first 500 bytes of every fixture YAML (Dimension 2).
- [ ] Every `input.yaml` declares `read_budget_tokens` and the value ≤ ecosystem cap (Dimension 1).
- [ ] Every `expected.yaml` declares `max_output_tokens` and the value ≤ 4096 (truncation safety).
- [ ] `scripts/release_readiness/validate_battery_fixtures.py` exits 1 on any schema/budget/identity violation.
- [ ] `scripts/release_readiness/score_battery.py` produces deterministic scores (same input → same output) and supports partial credit.
- [ ] All TDD tests pass: `uv run pytest tests/release_readiness/ -v`.
- [ ] Adversarial-review class fixtures cover all three verdict classes (APPROVE / MINOR / MAJOR).
- [ ] Repo-navigation class includes at least one negative case (the right answer is "not found / does not exist").
- [ ] Code-modification class fixtures bind to a specific clause in `.claude/rules/coding-style.md` so rule edits trigger fixture review.
- [ ] Session-handoff class includes at least one fixture targeting stale-marker / approval-state drift (per known feedback in memory).
- [ ] CI workflow `.github/workflows/validate-battery-fixtures.yml` runs the validator on any change under `tests/fixtures/model_release_battery/**` and fails the PR on validator exit 1.
- [ ] Discoverability anchors added: `AGENTS.md` and `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` both reference the corpus README (Dimension 5).
- [ ] Schema is runner-agnostic — the corpus does not depend on the runner #2410 will define; cross-reference is one-way.
- [ ] Review artifacts are posted to `scripts/review/results/`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Awaiting review |
| Codex | PENDING | Awaiting review |
| Gemini | PENDING | Awaiting review |

**Overall result:** PENDING

Pre-empted reviewer critiques (addressed in this plan; reviewers should still verify):

1. *"How will baselines avoid drift as models improve?"* — `DRIFT_POLICY.md` is a required deliverable. Drift policy will state: (a) baselines are versioned (`schema_version` per fixture); (b) a baseline refresh requires a matching plan + cross-review per `MODEL_RELEASE_UPGRADE_PLAYBOOK.md` repo-owned-drift branch — never a silent edit; (c) refresh cadence is event-driven (on a confirmed model-release readiness wave), not calendar-driven; (d) every refresh records the prior baseline's git SHA so regression deltas remain reproducible against the old baseline.
2. *"Are 5 fixtures per class enough?"* — The acceptance criteria require ≥3 per class as the minimum (not 5). The corpus is designed to grow: the schema is per-task-directory, so adding a 4th, 5th, or Nth task is purely additive and does not require rubric changes. The plan deliberately starts at 3 to keep the initial corpus reviewable; later issues can extend.
3. *"How do we differentiate model regression from baseline staleness?"* — A failing score triggers the DRIFT_POLICY decision tree: (a) does the actual output also fail a `forbidden_substrings` check? → genuine regression. (b) does the actual output match an *alternative* expected pattern not yet listed in `required_substrings_any`? → candidate baseline staleness, requires plan + cross-review to add the new pattern. (c) does the score drop only on a single rubric weight? → targeted regression. The policy makes regression-vs-staleness a documented call, not an ad hoc one.
4. *"Why YAML, not JSON?"* — Per memory `data_format_guidelines`: YAML default for agent-facing structured data; JSON only for machine-consumed tool output. Fixtures are agent-facing.
5. *"Does this pre-empt #2410's runner contract?"* — No: the corpus schema is intentionally runner-agnostic (input/expected/meta YAML files, no execution semantics). The cross-reference is one-way: the runner contract #2410 will reference the corpus; the corpus does not encode runner behavior.
6. *"What stops fixtures from blowing context budgets when fed to a real provider?"* — Every `input.yaml` carries a `read_budget_tokens` field validated by `validate_battery_fixtures.py` against an ecosystem cap (default 16K, configurable). Every `expected.yaml` carries `max_output_tokens` ≤ 4096.
7. *"How is this enforced — prose, script, or hook?"* — Tier 2 (script) per `.claude/rules/patterns.md` enforcement gradient: a CI workflow runs the validator on every fixture-path change. Tier 3 (commit hook) is deferred to a follow-up if validator exit-1 friction appears in practice.

Revisions made based on review:
- (none yet — to be populated post-review)

---

## Risks and Open Questions

- **Risk:** Reviewers may push for >3 fixtures per class. Mitigation: schema is additive; defer breadth expansion to a follow-up issue rather than ballooning this one.
- **Risk:** Hand-authored expected-output baselines could encode reviewer bias rather than ground truth. Mitigation: every `expected.yaml` cites a specific repo file or rule clause as its authority (e.g., a coding-style rule id), so the baseline is rule-derived, not opinion-derived.
- **Risk:** CI workflow path filter may miss new fixture sub-trees. Mitigation: workflow uses `tests/fixtures/model_release_battery/**` glob, validated by a TDD test.
- **Risk:** Identity-block-in-first-500-bytes constraint conflicts with YAML readability when keys are alphabetically sorted. Mitigation: SCHEMA.md fixes key order — identity keys first, body second; validator enforces order.
- **Risk:** `expected.yaml` "verdict" field for adversarial-review fixtures could be over-fit to the current `submit-to-codex.sh` / `submit-to-gemini.sh` output shape. Mitigation: verdict is normalized to {APPROVE, MINOR, MAJOR} per `scripts/review/plan-review-prompt.md` — provider-agnostic.
- **Risk:** Sparse-checkout overlay blindness (per memory `feedback_gemini_sandbox_overlay_blindness`) could cause Gemini reviewer to misread the corpus tree. Mitigation: review prompt will list fixture paths explicitly so reviewer doesn't rely on `find`/`ls`.
- **Open:** Should `DRIFT_POLICY.md` mandate that a baseline refresh requires the user-approval gate (not just plan-approved label)? Defer to user during plan approval.
- **Open:** Should the corpus include cross-provider expected-output variance (e.g., one baseline per provider) or a single canonical baseline? Plan currently assumes single canonical baseline; flag for user.
- **Open:** Should `score_battery.py` emit a JSON or YAML report? Per `data_format_guidelines`, JSON because the score report is machine-consumed by future readiness dashboards.

---

## Complexity: T2

**T2** — bounded fixture-corpus + validator + scorer + CI hook. New module surface, multiple files, TDD required, two existing standard files modified for discoverability anchors. No standards-derived numerical computation, so no calc-citation contract applies.
