You are an adversarial reviewer. Assume defects until proven otherwise. Do not praise or restate. Focus only on blocking or near-blocking issues. Return ONLY minified JSON under 1800 characters with keys verdict,summary,issues_found,suggestions,questions_for_author. Use at most 4 issues_found, 4 suggestions, 3 questions. Mark MAJOR if evaluator contract, schema migration, or workflow-config bounds are under-specified.

PLAN TO REVIEW:
# Plan for #2417: Generalize skill-autoresearch into repo-ecosystem autoresearch runner

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2417
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2417-claude.md | scripts/review/results/2026-04-20-plan-2417-codex.md | scripts/review/results/2026-04-20-plan-2417-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/cron/skill-autoresearch-nightly.sh` — current single-target loop already provides branch isolation, revert-on-non-improvement, dry-run support, results logging, and `git_safe_commit` integration.
- Found: `tests/cron/test_skill_autoresearch.sh` — current shell smoke/TDD contract verifies branch naming, results logging, eval integration, revert mechanism, main-branch protection, and dry-run/help support.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — repo already has a scheduled `skills-curation` task and the broader scheduled-task inventory pattern this runner must fit into.
- Found: `scripts/skills/` contains a dense ecosystem of skill-oriented analyzers and reporting utilities (`skill-usage-report.py`, `weekly_skills_audit.py`, `skill-health-dashboard.sh`) but no generic autoresearch runner abstraction.
- Gap: no existing reusable framework can target `.claude/agents/`, `.claude/get-shit-done/templates/`, or workflow config surfaces using the same accept/reject loop as skills.

### Standards
| Standard | Status | Source |
|---|---|---|
| Harness/planning workflow only — no external engineering standard applies | not applicable | AGENTS.md + issue-planning workflow |

### LLM Wiki pages consulted
- No relevant wiki pages; this is a harness/automation issue.

### Documents consulted
- `.planning/ROADMAP.md` — Phase 999.4 explicitly calls for extending autoresearch to agent definitions, templates, and workflow configs.
- `.planning/milestones/v1.0-ROADMAP.md` — same backlog item preserved in milestone roadmap, confirming this is existing roadmap scope rather than a new idea.
- Issue #1760 — self-improvement command surface depends on stronger repo-self-improvement plumbing.
- Issue #1720 — corpus mining already frames session/tool evidence as an ecosystem curation input, relevant to future evaluator design.
- Issue #2418 — compounding multi-iteration mode is already split out and should remain out of scope for this plan.

### Gaps identified
- No target-type abstraction layer exists.
- No evaluator interface exists for non-skill assets.
- Results tracking is skill-specific (`skill` column only), so future non-skill improvement runs cannot be audited consistently.
- No fixture-backed tests exist for agent/template/workflow-config dispatch.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-04-20 via `gh issue view`):
- `#2417` — OPEN — feat(automation): generalize skill-autoresearch into repo-ecosystem autoresearch runner
- `#2418` — OPEN — feat(automation): add compounding multi-iteration autoresearch with budget guards
- `#1760` — OPEN — feat(self-improvement): operationalize /powerup, /insights, /improve, /compound, /reflect, and /knowledge commands for the repo ecosystem
- `#1720` — OPEN — analysis: cross-agent session corpus audit — mine 1M+ tool calls for ecosystem curation opportunities

**File existence** (verified 2026-04-20):
- EXISTS: `scripts/cron/skill-autoresearch-nightly.sh`
- EXISTS: `tests/cron/test_skill_autoresearch.sh`
- EXISTS: `.planning/ROADMAP.md`
- EXISTS: `.planning/milestones/v1.0-ROADMAP.md`
- MISSING (new — this plan creates): `scripts/skills/repo_ecosystem_autoresearch.py`
- MISSING (new — this plan creates): `tests/skills/test_repo_ecosystem_autoresearch.py`

**Line excerpts**
- `.planning/ROADMAP.md` includes `### Phase 999.4: Extend Autoresearch to Agent & Template Definitions (BACKLOG)` and states the current loop only targets `.claude/skills/`.
- `scripts/cron/skill-autoresearch-nightly.sh` defines `BRANCH="autoresearch/skills-${DATE}"`, `RESULTS_FILE="${WS_HUB}/.claude/state/skill-autoresearch/results.tsv"`, and uses `git_safe_commit` for kept improvements.
- `tests/cron/test_skill_autoresearch.sh` asserts branch naming, results logging, time budget, branch isolation, revert mechanism, and dry-run/help support.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2417-repo-ecosystem-autoresearch-runner.md` |
| Generic runner | `scripts/skills/repo_ecosystem_autoresearch.py` |
| Skill wrapper update | `scripts/cron/skill-autoresearch-nightly.sh` |
| Tests | `tests/skills/test_repo_ecosystem_autoresearch.py` |
| Existing shell smoke test update | `tests/cron/test_skill_autoresearch.sh` |
| Optional evaluator fixtures | `tests/skills/fixtures/repo_ecosystem_autoresearch/` |
| Results artifact schema note | `docs/standards/repo-ecosystem-autoresearch.md` |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2417-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-20-plan-2417-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-20-plan-2417-gemini.md` |

---

## Deliverable

A reusable repo-ecosystem autoresearch runner that preserves today’s skill-improvement behavior while adding target-type dispatch and evaluator contracts for non-skill repo assets.

---

## Pseudocode

```
function discover_targets(target_type, root):
    if target_type == "skill": return all SKILL.md paths under .claude/skills/
    if target_type == "agent": return prompt/config files under .claude/agents/
    if target_type == "template": return files under .claude/get-shit-done/templates/
    if target_type == "workflow-config": return whitelisted config/planning surfaces
    else: raise ValueError

function evaluate_target(target_type, path):
    load evaluator registered for target_type
    return structured result {warnings, criticals, findings, score?}

function run_attempt(target_type, target_path, evaluator, time_budget):
    capture baseline evaluation
    ask model for minimal update constrained to target contract
    write candidate change
    re-evaluate
    if regresses or no improvement: revert
    else: keep and commit via git_safe_commit
    append results.tsv/json row with target_type + target_path + before/after

function main():
    parse args (target_type, dry_run, max_attempts, roots)
    discover candidates
    rank candidates by evaluator warnings
    iterate bounded attempts
    print summary + write durable results artifact
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/skills/repo_ecosystem_autoresearch.py` | generic target-type runner |
| Modify | `scripts/cron/skill-autoresearch-nightly.sh` | delegate existing skill flow into generic runner or share its core logic |
| Create | `tests/skills/test_repo_ecosystem_autoresearch.py` | fixture-backed dispatch and keep/revert tests |
| Modify | `tests/cron/test_skill_autoresearch.sh` | preserve current wrapper contract while allowing the new runner integration |
| Create | `tests/skills/fixtures/repo_ecosystem_autoresearch/` | agent/template/workflow-config fixtures |
| Create | `docs/standards/repo-ecosystem-autoresearch.md` | document evaluator contract, supported target types, and result schema |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_discover_skill_targets` | skill discovery matches current SKILL.md convention | fixture tree with 2 skills | both returned |
| `test_discover_agent_targets` | agent discovery finds supported agent files | fixture `.claude/agents/` tree | agent files returned |
| `test_discover_template_targets` | template discovery finds template files | fixture templates dir | template files returned |
| `test_dispatches_to_registered_evaluator` | target type uses the right evaluator contract | mocked evaluators | matching evaluator called |
| `test_revert_on_non_improvement` | unchanged/worse result restores original file | fixture target + mocked eval | file restored, result logged as revert |
| `test_keep_on_improvement` | improved result is committed/logged | fixture target + mocked eval | keep recorded with before/after |
| `test_results_include_target_type_and_path` | durable results schema is generalized | one kept run | row contains `target_type` + `target_path` |
| `test_shell_wrapper_preserves_dry_run_contract` | legacy skill wrapper still supports dry-run/help | wrapper invocation | exit 0 + dry-run banner |

---

## Acceptance Criteria

- [ ] A generic runner exists at `scripts/skills/repo_ecosystem_autoresearch.py`.
- [ ] Current skill-autoresearch behavior remains available through `scripts/cron/skill-autoresearch-nightly.sh`.
- [ ] Supported v1 target types include `skill` plus at least two of `agent`, `template`, `workflow-config`.
- [ ] Durable results include `target_type` and `target_path` instead of skill-only naming.
- [ ] Dry-run mode works for every supported target type.
- [ ] Tests cover target discovery, evaluator dispatch, keep/revert behavior, and wrapper compatibility.
- [ ] The evaluator/plugin contract is documented so future target types can be added without rewriting the runner.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | not run yet |
| Codex | PENDING | not run yet |
| Gemini | PENDING | not run yet |

**Overall result:** PENDING — review not yet run.

---

## Risks and Open Questions

- **Risk:** `workflow-config` can sprawl into unrelated config surfaces; v1 must use a tight allowlist rather than broad repo scanning.
- **Risk:** evaluator quality for non-skill targets may be weaker than the current skill-eval path; v1 should keep evaluator interfaces explicit and bounded.
- **Risk:** current `results.tsv` schema may be consumed by downstream tooling that assumes a `skill` column; integration impact must be checked before changing the artifact shape.
- **Open:** should the generalized runner write a new JSONL/TSV artifact beside the existing one rather than mutate the old schema in place?
- **Open:** should `commands/` be first-class in v1, or deferred until agent/template evaluator quality is proven?

---

## Complexity: T2

**T2** — one new reusable runner, one existing wrapper adaptation, new tests/fixtures, and a bounded documentation contract. No cross-machine coordination or implementation fan-out is required for v1.
