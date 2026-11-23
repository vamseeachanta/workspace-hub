     1|You are an adversarial reviewer. Assume this plan has defects until proven otherwise.
     2|
     3|MANDATORY STANCE
     4|1. Do not praise. Do not restate the plan. Focus only on what is wrong, missing, contradictory, underspecified, or risky.
     5|2. Return APPROVE only after affirmatively verifying each correctness-critical claim.
     6|3. When in doubt, return MINOR or MAJOR.
     7|4. Each finding must cite a specific plan section, file path, line excerpt, issue number, or quoted claim.
     8|5. Treat all cited file paths, issue numbers, and repo assertions as claims to verify, not facts to trust.
     9|6. Empty reviews are failures. If nothing is wrong, explicitly list what you verified.
    10|
    11|REVIEW TARGET
    12|- Issue: #2417
    13|- Title: feat(automation): generalize skill-autoresearch into repo-ecosystem autoresearch runner
    14|- Plan path: docs/plans/2026-04-20-issue-2417-repo-ecosystem-autoresearch-runner.md
    15|
    16|REQUIRED CHECKS
    17|1. Resource intelligence adequacy
    18|   - Are there at least 3 distinct grounded sources?
    19|   - Do the cited existing files/issues actually support the claimed gap?
    20|   - Is there any omitted existing implementation surface that would materially change the plan?
    21|2. Scope discipline
    22|   - Is the deliverable bounded to generic runner abstraction, not compounding iterations or unrelated self-improvement command work?
    23|   - Are target types sufficiently bounded for v1?
    24|3. Architecture correctness
    25|   - Is the evaluator contract concrete enough to implement?
    26|   - Is `workflow-config` too vague / too broad for a safe v1?
    27|   - Is results-schema migration/backward compatibility under-specified?
    28|4. TDD sufficiency
    29|   - Does every acceptance criterion have a plausible corresponding test?
    30|   - Are there missing tests around downstream consumers of existing `results.tsv`?
    31|5. Safety and rollback
    32|   - Does the plan preserve branch isolation, revert-on-non-improvement, and wrapper compatibility without hidden migration risk?
    33|6. Files-to-change consistency
    34|   - Do Artifact Map, Files to Change, TDD list, and Acceptance Criteria agree?
    35|7. Future-issue separation
    36|   - Does the plan correctly defer multi-iteration/compounding work to #2418 instead of silently absorbing it?
    37|
    38|OUTPUT FORMAT
    39|Return ONLY a JSON object matching this schema:
    40|{
    41|  "verdict": "APPROVE" | "MINOR" | "MAJOR" | "REJECT",
    42|  "summary": "1-3 sentence overall assessment naming the dominant defect class",
    43|  "issues_found": ["[P1] blocking: ...", "[P2] ..."],
    44|  "suggestions": ["specific fix ..."],
    45|  "questions_for_author": ["explicit question ..."]
    46|}
    47|
    48|Verdict guidance:
    49|- APPROVE: zero blocking defects, plan is approval-ready
    50|- MINOR: non-blocking issues only
    51|- MAJOR: any blocking gap, under-specified contract, scope ambiguity that could mislead implementation, or missing test coverage for a correctness-critical acceptance criterion
    52|- REJECT: fundamentally wrong direction
    53|

---
PLAN TO REVIEW
---

     1|# Plan for #2417: Generalize skill-autoresearch into repo-ecosystem autoresearch runner
     2|
     3|> **Status:** draft
     4|> **Complexity:** T2
     5|> **Date:** 2026-04-20
     6|> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2417
     7|> **Review artifacts:** scripts/review/results/2026-04-20-plan-2417-claude.md | scripts/review/results/2026-04-20-plan-2417-codex.md | scripts/review/results/2026-04-20-plan-2417-gemini.md
     8|
     9|---
    10|
    11|## Resource Intelligence Summary
    12|
    13|### Existing repo code
    14|- Found: `scripts/cron/skill-autoresearch-nightly.sh` — current single-target loop already provides branch isolation, revert-on-non-improvement, dry-run support, results logging, and `git_safe_commit` integration.
    15|- Found: `tests/cron/test_skill_autoresearch.sh` — current shell smoke/TDD contract verifies branch naming, results logging, eval integration, revert mechanism, main-branch protection, and dry-run/help support.
    16|- Found: `config/scheduled-tasks/schedule-tasks.yaml` — repo already has a scheduled `skills-curation` task and the broader scheduled-task inventory pattern this runner must fit into.
    17|- Found: `scripts/skills/` contains a dense ecosystem of skill-oriented analyzers and reporting utilities (`skill-usage-report.py`, `weekly_skills_audit.py`, `skill-health-dashboard.sh`) but no generic autoresearch runner abstraction.
    18|- Gap: no existing reusable framework can target `.claude/agents/`, `.claude/get-shit-done/templates/`, or workflow config surfaces using the same accept/reject loop as skills.
    19|
    20|### Standards
    21|| Standard | Status | Source |
    22||---|---|---|
    23|| Harness/planning workflow only — no external engineering standard applies | not applicable | AGENTS.md + issue-planning workflow |
    24|
    25|### LLM Wiki pages consulted
    26|- No relevant wiki pages; this is a harness/automation issue.
    27|
    28|### Documents consulted
    29|- `.planning/ROADMAP.md` — Phase 999.4 explicitly calls for extending autoresearch to agent definitions, templates, and workflow configs.
    30|- `.planning/milestones/v1.0-ROADMAP.md` — same backlog item preserved in milestone roadmap, confirming this is existing roadmap scope rather than a new idea.
    31|- Issue #1760 — self-improvement command surface depends on stronger repo-self-improvement plumbing.
    32|- Issue #1720 — corpus mining already frames session/tool evidence as an ecosystem curation input, relevant to future evaluator design.
    33|- Issue #2418 — compounding multi-iteration mode is already split out and should remain out of scope for this plan.
    34|
    35|### Gaps identified
    36|- No target-type abstraction layer exists.
    37|- No evaluator interface exists for non-skill assets.
    38|- Results tracking is skill-specific (`skill` column only), so future non-skill improvement runs cannot be audited consistently.
    39|- No fixture-backed tests exist for agent/template/workflow-config dispatch.
    40|
    41|### Evidence (embedded verification)
    42|**Issue statuses** (verified 2026-04-20 via `gh issue view`):
    43|- `#2417` — OPEN — feat(automation): generalize skill-autoresearch into repo-ecosystem autoresearch runner
    44|- `#2418` — OPEN — feat(automation): add compounding multi-iteration autoresearch with budget guards
    45|- `#1760` — OPEN — feat(self-improvement): operationalize /powerup, /insights, /improve, /compound, /reflect, and /knowledge commands for the repo ecosystem
    46|- `#1720` — OPEN — analysis: cross-agent session corpus audit — mine 1M+ tool calls for ecosystem curation opportunities
    47|
    48|**File existence** (verified 2026-04-20):
    49|- EXISTS: `scripts/cron/skill-autoresearch-nightly.sh`
    50|- EXISTS: `tests/cron/test_skill_autoresearch.sh`
    51|- EXISTS: `.planning/ROADMAP.md`
    52|- EXISTS: `.planning/milestones/v1.0-ROADMAP.md`
    53|- MISSING (new — this plan creates): `scripts/skills/repo_ecosystem_autoresearch.py`
    54|- MISSING (new — this plan creates): `tests/skills/test_repo_ecosystem_autoresearch.py`
    55|
    56|**Line excerpts**
    57|- `.planning/ROADMAP.md` includes `### Phase 999.4: Extend Autoresearch to Agent & Template Definitions (BACKLOG)` and states the current loop only targets `.claude/skills/`.
    58|- `scripts/cron/skill-autoresearch-nightly.sh` defines `BRANCH="autoresearch/skills-${DATE}"`, `RESULTS_FILE="${WS_HUB}/.claude/state/skill-autoresearch/results.tsv"`, and uses `git_safe_commit` for kept improvements.
    59|- `tests/cron/test_skill_autoresearch.sh` asserts branch naming, results logging, time budget, branch isolation, revert mechanism, and dry-run/help support.
    60|
    61|---
    62|
    63|## Artifact Map
    64|
    65|| Artifact | Path |
    66||---|---|
    67|| This plan | `docs/plans/2026-04-20-issue-2417-repo-ecosystem-autoresearch-runner.md` |
    68|| Generic runner | `scripts/skills/repo_ecosystem_autoresearch.py` |
    69|| Skill wrapper update | `scripts/cron/skill-autoresearch-nightly.sh` |
    70|| Tests | `tests/skills/test_repo_ecosystem_autoresearch.py` |
    71|| Existing shell smoke test update | `tests/cron/test_skill_autoresearch.sh` |
    72|| Optional evaluator fixtures | `tests/skills/fixtures/repo_ecosystem_autoresearch/` |
    73|| Results artifact schema note | `docs/standards/repo-ecosystem-autoresearch.md` |
    74|| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2417-claude.md` |
    75|| Plan review — Codex | `scripts/review/results/2026-04-20-plan-2417-codex.md` |
    76|| Plan review — Gemini | `scripts/review/results/2026-04-20-plan-2417-gemini.md` |
    77|
    78|---
    79|
    80|## Deliverable
    81|
    82|A reusable repo-ecosystem autoresearch runner that preserves today’s skill-improvement behavior while adding target-type dispatch and evaluator contracts for non-skill repo assets.
    83|
    84|---
    85|
    86|## Pseudocode
    87|
    88|```
    89|function discover_targets(target_type, root):
    90|    if target_type == "skill": return all SKILL.md paths under .claude/skills/
    91|    if target_type == "agent": return prompt/config files under .claude/agents/
    92|    if target_type == "template": return files under .claude/get-shit-done/templates/
    93|    if target_type == "workflow-config": return whitelisted config/planning surfaces
    94|    else: raise ValueError
    95|
    96|function evaluate_target(target_type, path):
    97|    load evaluator registered for target_type
    98|    return structured result {warnings, criticals, findings, score?}
    99|
   100|function run_attempt(target_type, target_path, evaluator, time_budget):
   101|    capture baseline evaluation
   102|    ask model for minimal update constrained to target contract
   103|    write candidate change
   104|    re-evaluate
   105|    if regresses or no improvement: revert
   106|    else: keep and commit via git_safe_commit
   107|    append results.tsv/json row with target_type + target_path + before/after
   108|
   109|function main():
   110|    parse args (target_type, dry_run, max_attempts, roots)
   111|    discover candidates
   112|    rank candidates by evaluator warnings
   113|    iterate bounded attempts
   114|    print summary + write durable results artifact
   115|```
   116|
   117|---
   118|
   119|## Files to Change
   120|
   121|| Action | Path | Reason |
   122||---|---|---|
   123|| Create | `scripts/skills/repo_ecosystem_autoresearch.py` | generic target-type runner |
   124|| Modify | `scripts/cron/skill-autoresearch-nightly.sh` | delegate existing skill flow into generic runner or share its core logic |
   125|| Create | `tests/skills/test_repo_ecosystem_autoresearch.py` | fixture-backed dispatch and keep/revert tests |
   126|| Modify | `tests/cron/test_skill_autoresearch.sh` | preserve current wrapper contract while allowing the new runner integration |
   127|| Create | `tests/skills/fixtures/repo_ecosystem_autoresearch/` | agent/template/workflow-config fixtures |
   128|| Create | `docs/standards/repo-ecosystem-autoresearch.md` | document evaluator contract, supported target types, and result schema |
   129|| Update | `docs/plans/README.md` | add this plan to the index |
   130|
   131|---
   132|
   133|## TDD Test List
   134|
   135|| Test name | What it verifies | Expected input | Expected output |
   136||---|---|---|---|
   137|| `test_discover_skill_targets` | skill discovery matches current SKILL.md convention | fixture tree with 2 skills | both returned |
   138|| `test_discover_agent_targets` | agent discovery finds supported agent files | fixture `.claude/agents/` tree | agent files returned |
   139|| `test_discover_template_targets` | template discovery finds template files | fixture templates dir | template files returned |
   140|| `test_dispatches_to_registered_evaluator` | target type uses the right evaluator contract | mocked evaluators | matching evaluator called |
   141|| `test_revert_on_non_improvement` | unchanged/worse result restores original file | fixture target + mocked eval | file restored, result logged as revert |
   142|| `test_keep_on_improvement` | improved result is committed/logged | fixture target + mocked eval | keep recorded with before/after |
   143|| `test_results_include_target_type_and_path` | durable results schema is generalized | one kept run | row contains `target_type` + `target_path` |
   144|| `test_shell_wrapper_preserves_dry_run_contract` | legacy skill wrapper still supports dry-run/help | wrapper invocation | exit 0 + dry-run banner |
   145|
   146|---
   147|
   148|## Acceptance Criteria
   149|
   150|- [ ] A generic runner exists at `scripts/skills/repo_ecosystem_autoresearch.py`.
   151|- [ ] Current skill-autoresearch behavior remains available through `scripts/cron/skill-autoresearch-nightly.sh`.
   152|- [ ] Supported v1 target types include `skill` plus at least two of `agent`, `template`, `workflow-config`.
   153|- [ ] Durable results include `target_type` and `target_path` instead of skill-only naming.
   154|- [ ] Dry-run mode works for every supported target type.
   155|- [ ] Tests cover target discovery, evaluator dispatch, keep/revert behavior, and wrapper compatibility.
   156|- [ ] The evaluator/plugin contract is documented so future target types can be added without rewriting the runner.
   157|
   158|---
   159|
   160|## Adversarial Review Summary
   161|
   162|| Provider | Verdict | Key findings |
   163||---|---|---|
   164|| Claude | PENDING | not run yet |
   165|| Codex | PENDING | not run yet |
   166|| Gemini | PENDING | not run yet |
   167|
   168|**Overall result:** PENDING — review not yet run.
   169|
   170|---
   171|
   172|## Risks and Open Questions
   173|
   174|- **Risk:** `workflow-config` can sprawl into unrelated config surfaces; v1 must use a tight allowlist rather than broad repo scanning.
   175|- **Risk:** evaluator quality for non-skill targets may be weaker than the current skill-eval path; v1 should keep evaluator interfaces explicit and bounded.
   176|- **Risk:** current `results.tsv` schema may be consumed by downstream tooling that assumes a `skill` column; integration impact must be checked before changing the artifact shape.
   177|- **Open:** should the generalized runner write a new JSONL/TSV artifact beside the existing one rather than mutate the old schema in place?
   178|- **Open:** should `commands/` be first-class in v1, or deferred until agent/template evaluator quality is proven?
   179|
   180|---
   181|
   182|## Complexity: T2
   183|
   184|**T2** — one new reusable runner, one existing wrapper adaptation, new tests/fixtures, and a bounded documentation contract. No cross-machine coordination or implementation fan-out is required for v1.
   185|
