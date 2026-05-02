# Plan for #2486: v2 periodic skill ecosystem housekeeping audit

> Status: plan-approved (awaiting implementation)
> Complexity: T2
> Date: 2026-04-24
> Issue: [#2486](https://github.com/vamseeachanta/workspace-hub/issues/2486)
> Review artifacts: scripts/review/results/2026-04-24-plan-2486-claude.md | scripts/review/results/2026-04-24-plan-2486-codex.md | scripts/review/results/2026-04-24-plan-2486-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/cron/skills-curation.sh` — the canonical scheduled wrapper is already deterministic and launches `uv run --no-project python scripts/skills/weekly_skills_audit.py`; #2486 must extend this existing weekly path rather than create a second housekeeping cron.
- Found: `scripts/skills/weekly_skills_audit.py` — v1 emits JSON + Markdown artifacts, uses `config/skills/weekly-audit-policy.yaml`, applies stable finding keys, baseline deltas, waivers, informational `_core/_internal` handling, and read-only output under `logs/maintenance/skills-curation/`.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — `skills-curation` already runs at `04:00 Mon`, logs to `logs/maintenance/skills-curation-*.log`, is `is_claude_task: false`, and points at the deterministic wrapper.
- Found: `docs/ops/scheduled-tasks.md` — operator-facing inventory already documents `skills-curation` as a deterministic weekly JSON + Markdown skills audit.
- Found: `config/skills/weekly-audit-policy.yaml` — v1 policy covers duplicate/wrapper/near-duplicate/adjacent-specialization/generic-leaf/stale/human-review classification, severity/confidence, ranking, carry-forward, and candidate escalation.
- Found: `tests/cron/test_skills_curation.py` and `tests/skills/test_weekly_skills_audit.py` — regression coverage exists for wrapper dry-run, output-root forwarding, stale `WORKSPACE_HUB` protection, v1 inventory scope, classification, output schema, baseline deltas, waiver handling, and read-only behavior.
- Found: `scripts/skills/audit-skills.py` and `scripts/skills/skill_eval_ecosystem.py` — existing quality evaluators can provide content-quality signals such as missing category/frontmatter, path/category drift, critical findings, and coverage gaps; #2486 should consume or align with these instead of inventing another scanner.
- Found: `scripts/skills/detect_duplicate_skills.py` and `scripts/skills/skill-usage-report.py` — existing duplicate and usage/staleness logic is useful as prior art, but v2 must not directly call writeful or differently-scoped scripts from the scheduled cron path; every v2 signal must consume the canonical `weekly_skills_audit.py` inventory or a read-only normalized adapter.

### Prior plans and issues
- `#2280` / `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` — parent governance plan for the weekly skills-maintenance loop; establishes frontmatter `name` as canonical identity, v1 audit universe, classification ladder, waiver expectations, and artifact contract.
- `#2281` / `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md` — completed v1 implementation plan for deterministic weekly audit entrypoint and cron wrapper.
- `#2282` / `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md` — completed policy plan; the checked-in `weekly-audit-policy.yaml` is the canonical policy source.
- `#2290` — completed cleanup for exact-copy skills and leaf collisions; useful precedent for turning weekly findings into bounded follow-up cleanup issues.
- `#2083` — still-open duplicate/session-corpus-audit reconciliation example; useful live fixture for exact duplicate or wrapper-vs-canonical decision boundaries.
- `#2320` — implemented skill invocation scanner/baseline report; relevant if v2 adds usage/dead-skill trend signals.
- `#2486` issue body — created as a v2 periodic housekeeping umbrella after a live snapshot showed active skill parity across Claude/Codex/Gemini and remaining quality/grouping issues.

### Live verification and observed state
- Active skill mirrors were previously counted as `.claude/skills = 932`, `.codex/skills = 932`, `.gemini/skills = 932`, with Codex/Gemini symlinks verified OK.
- Existing skill validation previously passed for `3098` skill files.
- The initial #2486 issue body recorded v2 audit findings: `38` critical eval failures, `321` missing category frontmatter entries, `32` category mismatches, `7` duplicate active names, `17` oversized active skills over 500 lines, and grouping inconsistencies including `workspace_hub_learned` vs `workspace-hub-learned`, `business_admin` vs `business/admin`, and `_archive` vs `_archived`.
- Targeted regression check on 2026-04-24 passed: `uv run pytest tests/cron/test_skills_curation.py tests/skills/test_weekly_skills_audit.py -q` => `26 passed in 24.22s`.
- `git status --short` timed out during planning on 2026-04-24; use narrower status commands before implementation to avoid assuming a clean working tree.

### Standards and workflow constraints
| Standard | Status | Source |
|---|---|---|
| GitHub issue must be planned before implementation | required | `AGENTS.md`, `docs/plans/README.md`, hard-stop policy |
| TDD mandatory before implementation | required | `AGENTS.md` |
| Existing scheduled-task registry is source of truth | required | `config/scheduled-tasks/schedule-tasks.yaml`, `docs/ops/scheduled-tasks.md` |
| Reviews at plan and implementation stages | required | AI review routing policy and user profile |
| Skills are mirrored across agents; parity matters | required | active `.claude/.codex/.gemini` skill symlink checks |

### Gaps identified
- V1 weekly audit focuses mainly on duplicate/frontmatter-name/leaf-collision/wrapper classification; it does not yet unify broader deterministic content-quality, category-frontmatter, grouping taxonomy, and size signals into one operator report.
- Existing quality scripts have partially overlapping scopes and inconsistent runtime behavior; prior broad shell audit timed out at 300s, so v2 needs bounded, performant entrypoints, explicit timeouts, and tests.
- Category/grouping hygiene is not yet encoded as a first-class finding type with stable keys, waivers, and trend deltas.
- The prior draft left GitHub issue updates and follow-up issue creation too open-ended; v2 must keep the scheduled cron path network-free and artifact-only, producing at most a local GitHub-update payload for manual use.
- Existing usage/staleness tooling is writeful and has different scope semantics; v2 must not invoke it directly from `skills-curation` until a read-only adapter or stdout-only mode exists.

<!-- Verification: distinct sources >= 3. Current count: 14 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-2486-v2-periodic-skill-ecosystem-housekeeping-audit.md` |
| GitHub issue | `https://github.com/vamseeachanta/workspace-hub/issues/2486` |
| Existing weekly wrapper | `scripts/cron/skills-curation.sh` |
| Existing v1 audit entrypoint | `scripts/skills/weekly_skills_audit.py` |
| Existing v1 policy | `config/skills/weekly-audit-policy.yaml` |
| Existing waiver registry | `config/skills/weekly-audit-waivers.yaml` |
| Scheduled task registry | `config/scheduled-tasks/schedule-tasks.yaml` |
| Scheduled-task docs | `docs/ops/scheduled-tasks.md` |
| V1 wrapper tests | `tests/cron/test_skills_curation.py` |
| V1 audit tests | `tests/skills/test_weekly_skills_audit.py` |
| Proposed v2 tests | `tests/skills/test_weekly_skills_audit_v2.py` |
| Plan review — Claude | `scripts/review/results/2026-04-24-plan-2486-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-24-plan-2486-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-24-plan-2486-gemini.md` |

---

## Deliverable

Upgrade the existing deterministic weekly `skills-curation` loop into a **v2 periodic skill ecosystem housekeeping audit** that reports deterministic content-quality, grouping/taxonomy, size, duplication, waiver, and follow-up-candidate signals in one stable, low-noise operator report without automatically mutating skills or invoking writeful sidecar tools.

### V2 scope boundaries
- Preserve the existing scheduled task ID: `skills-curation`.
- Preserve the existing wrapper path: `scripts/cron/skills-curation.sh`.
- Preserve read-only behavior for the skills tree in v2; no auto-rename, auto-archive, or auto-rewrite.
- Extend the deterministic audit/report contract rather than replacing it with an LLM prompt.
- The scheduled cron path must be artifact-first, network-free, and must not require `gh` or GitHub auth.
- Treat `.claude/skills` as the canonical scanned tree and continue relying on Codex/Gemini symlink parity checks rather than scanning the same mirrored content three times.
- Every v2 signal family must consume one canonical inventory builder from `weekly_skills_audit.py` or a normalized read-only adapter using the same inclusion/exclusion semantics.
- Any normalized read-only adapter must declare: matching include/exclude universe, required normalized fields, `source_id`, timeout behavior, no network access, and no filesystem writes outside the configured audit output root.
- Direct invocation of writeful tooling such as the current `scripts/skills/skill-usage-report.py` is forbidden in the scheduled path unless that tooling first gains a tested read-only/stdout-only mode.

### Required v2 signal families
1. **Content-quality signals**
   - missing or malformed frontmatter
   - missing `category` or invalid category values
   - deterministic description length/shape violations using thresholds defined in policy
   - pinned deterministic fields from checked-in evaluator/library code only; no LLM or free-form evaluator calls in the cron path
2. **Grouping/taxonomy signals**
   - category frontmatter vs path mismatch
   - underscore-vs-hyphen category drift such as `workspace_hub_learned` vs `workspace-hub-learned`, but only via alias families declared in policy YAML
   - legacy grouping drift such as `_archive` vs `_archived`, but only via policy-declared aliases
   - duplicate top-level grouping aliases such as `business_admin` vs `business/admin`, but no hardcoded alias strings in Python
3. **Duplication and overlap signals**
   - exact canonical-name duplicates
   - leaf collisions
   - wrapper/canonical pairs
   - near-duplicate same-intent candidates
4. **Size and maintainability signals**
   - oversized active skills, with threshold configurable in policy
   - deterministic related-skill/cross-reference absence only when a policy threshold is met, e.g. active skill exceeds the configured line-count threshold and has zero `related_skills` / `see_also` entries
   - split/wrap/consolidate recommendations only as non-blocking manual-review text derived from deterministic size/duplicate/grouping findings
5. **Usage/staleness signals — deferred unless read-only**
   - no direct invocation of the current writeful `skill-usage-report.py` from scheduled `skills-curation`
   - usage tier changes are included only if supplied by a read-only adapter, stdout-only mode, or pre-existing static artifact that cannot dirty `.claude/state`
   - stale-superseded candidates require deterministic maintained-replacement metadata in policy/frontmatter
   - dead/low-signal findings are manual-review candidates only, not auto-archive actions
6. **Escalation/follow-up signals**
   - stable `candidate` findings that may deserve bounded cleanup GitHub issues
   - idempotent mapping from finding key to existing/open follow-up issue if implemented
   - compact carry-forward of already-known findings

### Output contract
Extend the existing weekly JSON + Markdown artifact rather than creating a parallel artifact family.

Required JSON additions:
- `schema_version: 2` plus `policy_version` from the single source-of-truth policy file `config/skills/weekly-audit-policy.yaml`
- `baseline_compatibility` recording whether a prior artifact was compatible, ignored, or absent
- append-only v2 schema contract: all required v1 fields remain present; v2 readers use tolerant `dict.get()` / unknown-key-ignore behavior for baseline comparisons
- `scan_durations` and/or per-signal runtime metadata
- `skill_counts` with active, informational, excluded, malformed counts
- `category_summary`
- `grouping_findings[]`
- `content_quality_findings[]`
- `size_findings[]`
- `usage_findings[]` always present; empty list when no read-only usage source is available
- `follow_up_candidates[]` always present as local report data only
- `github_update_payload_path` when a manual/offline payload is rendered

Markdown report must include stable sections:
1. scope / policy / runtime summary
2. headline deltas since prior run
3. critical content-quality findings
4. grouping and taxonomy drift
5. duplicate / overlap findings
6. oversized and maintainability findings
7. stale / usage findings
8. follow-up candidates
9. waived / suppressed / informational carry-forward
10. operational errors or skipped inputs

### GitHub issue update contract
- Default and scheduled cron path: write local artifacts only; no `gh`, no network calls, no issue comments, and no issue creation.
- V2 may render a local Markdown payload for a human/operator to post to #2486, but posting that payload is out of scope for the scheduled task.
- Automatic per-finding issue creation and existing-issue correlation are explicitly deferred to a separate follow-up issue after multiple stable v2 weekly reports.
- The default invocation must have a regression test proving it does not attempt GitHub/network access and performs no writes outside the configured audit output root.

---

## Pseudocode

```text
run_v2_skills_housekeeping_audit():
    load v1 policy and v2 extension policy
    build canonical skill inventory from .claude/skills
    verify mirror parity metadata for .codex/skills and .gemini/skills when cheap
    collect v1 duplicate/wrapper/leaf findings
    collect content-quality findings from deterministic evaluator/library fields only
    collect grouping/taxonomy drift findings from path + frontmatter comparisons using policy-declared aliases
    collect oversized/maintainability findings using configured thresholds
    collect usage/staleness signals only from read-only sources; otherwise emit operational warning
    normalize all findings into the existing finding schema plus v2 extensions
    compute stable finding keys per family:
        v1 duplicate/wrapper/leaf keys remain unchanged
        grouping key = family + alias_family_id + normalized_target + stable hash of sorted offender paths (or bounded category-level path summary for very large offender sets)
        content key = family + rule_id + canonical_name + normalized path
        size key = family + threshold_id + canonical_name + normalized path
        usage key = family + source_id + canonical_name + normalized path
    apply waivers and informational bucketing
    compare with prior compatible JSON baseline
    produce stable JSON and Markdown artifacts
    optionally produce GitHub update payload in dry-run mode first
    exit zero when findings exist but the audit completed successfully
    exit non-zero only for execution failures that make the report untrustworthy
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/skills/weekly_skills_audit.py` | add v2 signal collection, normalized findings, runtime metadata, stable v2 finding keys, and extended artifact schema |
| Modify | `config/skills/weekly-audit-policy.yaml` | single source of truth; bump to v2 and configure deterministic thresholds, grouping aliases, category normalization, escalation rules, and timeout settings |
| Modify | `config/skills/weekly-audit-waivers.yaml` | add/adjust waivers for known accepted grouping or wrapper cases if needed |
| No default change | `scripts/cron/skills-curation.sh` | stable wrapper; change only if a specific reviewed CLI contract requires it |
| No default change | `config/scheduled-tasks/schedule-tasks.yaml` | stable schedule; change only if description/log contract must be updated, never to add `gh` as a cron requirement |
| Modify | `docs/ops/scheduled-tasks.md` | document v2 artifact semantics and explicitly state scheduled path is local/network-free |
| Modify | `tests/skills/test_weekly_skills_audit.py` | preserve existing v1 regression coverage while extending schema expectations where appropriate |
| Create | `tests/skills/test_weekly_skills_audit_v2.py` | fixture-backed tests for content-quality, grouping, size, usage, and follow-up-candidate signals |
| Update | `docs/plans/README.md` | add #2486 plan row |
| Update | GitHub issue `#2486` | planning progress, review results, and approval state |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_v2_preserves_existing_v1_duplicate_findings` | v2 does not regress v1 duplicate/leaf/wrapper behavior | fixture duplicate + leaf + wrapper corpus | same v1 classifications still present |
| `test_v2_reports_missing_category_frontmatter` | missing category becomes content-quality finding | skill with valid name/description but no category | content-quality finding with stable key |
| `test_v2_reports_category_path_mismatch` | category/path drift is first-class | frontmatter category not aligned with path policy | grouping finding with recommended action |
| `test_v2_normalizes_underscore_hyphen_group_aliases` | known alias families are detected consistently | `workspace_hub_learned` + `workspace-hub-learned` fixtures | grouping drift finding, not duplicate false positive |
| `test_v2_detects_archive_archived_drift` | `_archive` vs `_archived` drift is visible | fixture tree with both spellings | grouping finding and excluded-scope metadata |
| `test_v2_reports_oversized_active_skill` | size threshold is configurable and stable | skill over configured line threshold | size finding with severity/recommendation |
| `test_v2_does_not_flag_informational_internal_size_as_headline` | `_core/_internal` remain de-emphasized | oversized internal/core skill fixture | suppressed/informational section, not headline finding |
| `test_v2_schema_contains_runtime_and_skill_counts` | artifact schema supports trend/reporting | fixture audit run | JSON contains `scan_durations`, `skill_counts`, and v2 sections |
| `test_v2_baseline_delta_marks_new_changed_carry_forward` | trend semantics work for v2 findings | prior/current fixture artifacts | correct `is_new`, `is_changed`, carry-forward behavior |
| `test_v2_waiver_suppresses_known_grouping_exception` | waivers apply to v2 grouping findings | grouping drift + waiver registry | suppressed finding remains visible with reason |
| `test_v2_follow_up_candidates_are_idempotent` | candidate keys are stable for future issue creation | repeated audit of same candidate | same `finding_key`, no duplicate candidate identity |
| `test_v2_default_run_does_not_call_gh_or_network` | canonical cron path remains local-only | default fixture audit run with network/GH call trap | no GitHub/network invocation attempted |
| `test_v2_renders_manual_github_payload_without_posting` | optional GH payload is local-only | `--render-github-payload` in temp output root | Markdown payload written, no `gh` call |
| `test_v2_usage_signal_unavailable_is_operational_warning_not_crash` | usage scan failure or unavailable read-only source does not break core audit | unavailable usage fixture | operational warning and successful core audit |
| `test_v2_does_not_invoke_writeful_usage_report` | scheduled audit does not dirty `.claude/state` | trap/fixture for `skill-usage-report.py` writes | no `.claude/state/skill-scores.yaml` or usage-report write |
| `test_v2_external_signal_timeout_degrades_to_warning` | external read-only adapters cannot hang cron | adapter fixture that sleeps past timeout | operational warning and bounded runtime |
| `test_v2_finding_keys_are_stable_per_family` | grouping/content/size keys are stable and waiver-safe | repeated fixture with alias family and content rules | same finding keys across runs |
| `test_v2_first_run_after_v1_baseline_has_explicit_compatibility_state` | schema migration is deterministic | existing v1 artifact + v2 run | explicit baseline compatibility field and no accidental wrong comparison |
| `test_skills_curation_wrapper_contract_still_passes` | wrapper behavior remains stable | existing cron wrapper tests | all existing tests pass |
| `test_validate_schedule_still_passes` | scheduler registry remains valid | updated schedule docs/config if touched | validator exits 0 |

---

## Acceptance Criteria

- [ ] Existing `skills-curation` scheduled task remains the single canonical periodic path.
- [ ] Existing v1 tests still pass.
- [ ] V2 tests cover content-quality, grouping/taxonomy, size, baseline delta, waiver, and follow-up-candidate behavior.
- [ ] Weekly audit remains read-only against the skills tree.
- [ ] JSON artifact schema is extended without breaking existing required v1 fields.
- [ ] Markdown report includes all required v2 sections with stable headings.
- [ ] `config/skills/weekly-audit-policy.yaml` remains the single policy source and is bumped/extended for v2; no parallel split-brain v2 policy file is introduced.
- [ ] V2 policy/config defines category/grouping normalization, alias families, description thresholds, size thresholds, timeout settings, and deterministic rule IDs.
- [ ] Known grouping aliases are detected deterministically from policy config, with no hardcoded alias strings in Python.
- [ ] V1 duplicate/wrapper/leaf finding keys are preserved unchanged; new v2 families define stable key recipes, with bounded hashed grouping keys for large offender sets.
- [ ] First v2 run against existing v1 artifacts has explicit baseline compatibility behavior.
- [ ] Default weekly run does not create GitHub issue spam and does not call `gh` or the network.
- [ ] V2 JSON preserves required v1 fields and keeps optional top-level collections structurally stable, e.g. `usage_findings: []` when unavailable.
- [ ] Default weekly run produces no GitHub payload file and no `github_update_payload_path` JSON field.
- [ ] Optional `--render-github-payload` writes one deterministic filename inside the configured audit output root only, without posting or invoking `gh`.
- [ ] Any GitHub update support is local-payload-only in v2; actual posting and per-finding issue creation are deferred.
- [ ] `uv run pytest tests/cron/test_skills_curation.py tests/skills/test_weekly_skills_audit.py tests/skills/test_weekly_skills_audit_v2.py -q` passes, or the final implemented test subset is explicitly justified.
- [ ] `uv run --no-project python scripts/cron/validate-schedule.py` passes if scheduled-task config changes.
- [ ] `bash scripts/cron/skills-curation.sh --dry-run` still prints a deterministic Python invocation.
- [ ] One manual redirected-output run produces JSON + Markdown artifacts in a temp output root without dirtying the repo.
- [ ] The scheduled/default run writes nothing outside `logs/maintenance/skills-curation/` or the redirected audit output root; it does not update `.claude/state/skill-scores.yaml` or `.claude/state/skill-usage-report/`.
- [ ] Any external read-only adapters have explicit timeouts and degrade failures to operational warnings.
- [ ] Plan review artifacts are posted before implementation begins.

---

## Adversarial Review Plan

Three-provider plan review is appropriate because this touches cross-agent skill governance, scheduled-task behavior, and future issue-generation policy.

Review questions:
1. Does the plan safely extend #2281/#2282 without duplicating or regressing the existing weekly audit?
2. Are v2 signal families bounded enough to implement without turning into open-ended taxonomy redesign?
3. Is the GitHub update/follow-up candidate model safe against weekly issue spam?
4. Are grouping/category findings deterministic enough for stable baselines and waivers?
5. Are tests sufficient to protect the cron wrapper, artifact schema, and read-only behavior?

If any provider returns MAJOR, keep #2486 in draft/plan-review and revise before asking for approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude/delegated | MAJOR | writeful usage tooling risk; v2 key/schema migration underspecified; subjective signal scope; GitHub network/spam boundaries |
| Codex | MAJOR | CRITICAL read-only violation risk from `skill-usage-report.py`; canonical inventory mismatch; subjective signals; GitHub correlation ambiguity; grouping key instability; cron must stay GH-free |
| Gemini | MINOR | avoid nondeterministic evaluator calls; choose single policy migration; add timeouts; keep taxonomy aliases in YAML |
| Codex re-review | MINOR | no remaining MAJOR blocker; requested adapter-contract, severity/headline determinism, and local payload filename tests |
| Gemini re-review | MINOR | plan safe to implement; requested stable optional keys, append-only v1 compatibility, and bounded grouping-key hashing |

**Overall result:** initial FAIL, revised, then re-reviewed. Remaining findings are MINOR and have been incorporated into the plan. The plan is approval-ready for user decision; implementation remains blocked until explicit user approval per issue workflow.

Revisions applied from review:
- Forbid direct invocation of writeful `skill-usage-report.py` from the scheduled path unless a read-only/stdout-only mode exists.
- Require every v2 signal to consume one canonical inventory or normalized read-only adapter.
- Narrow subjective content signals to policy-pinned deterministic thresholds and manual-review text.
- Make the scheduled path local-only: no `gh`, no network, no issue creation.
- Defer per-finding issue creation/correlation to a separate follow-up after stable v2 reports.
- Choose single policy source `config/skills/weekly-audit-policy.yaml` extended to v2.
- Add stable key recipes for new v2 finding families and explicit v1 baseline compatibility behavior.
- Add timeout and no-side-effect tests.
- Add read-only adapter contract, severity/headline determinism, and local GitHub payload path tests from Codex re-review.
- Add stable optional schema keys, append-only v1 compatibility, and bounded grouping-key hashing from Gemini re-review.

---

## Risks and Open Questions

- Risk: integrating all evaluators into one weekly run could become slow or flaky; v2 must use deterministic/static fields only, record runtime, and degrade optional signals to warnings.
- Risk: category/grouping rules may overfit current naming drift; use explicit policy aliases and fixtures rather than free-form heuristics.
- Risk: automatic GitHub issue creation can create noise; v2 defers issue creation and actual posting entirely.
- Risk: usage/staleness data may have a different audit universe than duplicate/content scans; include it only through canonical inventory-normalized read-only sources.
- Decision: v2 extends the existing `config/skills/weekly-audit-policy.yaml` as the single source of truth; no separate `weekly-audit-v2-policy.yaml` unless a future reviewed migration issue approves it.
- Decision: #2486 remains the long-lived umbrella/tracker; scheduled weekly reports stay artifact-only, with optional local payload rendering for manual posting.

---

## Complexity: T2

T2 — bounded multi-file maintenance automation extending an existing deterministic audit path, policy file, tests, docs, and optional GitHub reporting behavior. It is cross-cutting but should not require architectural rewrites or multi-repo changes.
