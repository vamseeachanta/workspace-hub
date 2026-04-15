# Plan for #2280: weekly skill ecosystem audit and consolidation maintenance loop

> Status: draft
> Complexity: T2
> Date: 2026-04-14
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2280
> Review artifacts: scripts/review/results/2026-04-14-plan-2280-claude.md | scripts/review/results/2026-04-14-plan-2280-codex.md | scripts/review/results/2026-04-14-plan-2280-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — the canonical scheduler already declares a weekly `skills-curation` task (`id: skills-curation`) that runs every Monday at 04:00 and writes to `logs/maintenance/skills-curation-*.log`; #2280 must upgrade/replace this existing workflow rather than introduce a second overlapping weekly cron.
- Found: `scripts/cron/skills-curation.sh` — current implementation is a thin Claude prompt wrapper (`claude -p ... --dangerously-skip-permissions`) and does not produce deterministic JSON/Markdown artifacts or taxonomy-aware classification.
- Found: `tests/cron/test_skills_curation.py` — current test contract expects explicit `--print`-mode invocation and dry-run visibility, and the live test suite currently fails (`uv run pytest tests/cron/test_skills_curation.py -q` => 2 failures), confirming the wrapper is already drifted from expected behavior.
- Found: `scripts/skills/detect_duplicate_skills.py` — repo already has a deterministic detector for duplicate frontmatter names and leaf-directory collisions, so v1 should compose this rather than reinvent raw duplicate scanning.
- Found: `scripts/skills/skill-usage-report.py` — repo already has usage/reference scoring logic that can feed low-signal/stale-skill review, but its audit universe differs from the duplicate detector and must be reconciled by policy.
- Found: `tests/skills/test_skill_name_canonicalization.py` — existing tests encode the rule that frontmatter `name` should be preferred over leaf directory name, which should become an explicit canonical identity rule in #2280.

### Standards
| Standard | Status | Source |
|---|---|---|
| Control-plane adapter/scheduler model | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Cron task governance via YAML + installer + validator | done / active operational pattern | `docs/ops/scheduled-tasks.md`, `scripts/cron/setup-cron.sh`, `scripts/cron/validate-schedule.py` |
| Hard-stop planning workflow | applicable to this issue | `docs/plans/README.md`, `docs/standards/HARD-STOP-POLICY.md` |

### LLM Wiki pages consulted
- No relevant wiki pages found; this is harness/taxonomy/cron governance work anchored in repo code, issue history, and scheduled-task documentation rather than domain wiki content.

### Documents consulted
- `docs/ops/scheduled-tasks.md` — confirms `skills-curation` already exists as a Monday 04:00 weekly job and should be treated as the canonical weekly slot to upgrade.
- `docs/plans/2026-04-12-issue-2239-automate-weekly-hermes-cross-machine-parity-review.md` — provides the closest precedent for a bounded weekly cron plan with deterministic artifact paths, validator checks, and explicit v1 boundaries.
- Related issue #2083 — concrete example of a true same-capability duplicate (`session-corpus-audit`) that should appear in weekly skill-governance output.
- Related issue #2019 — concrete example of planned consolidation of overlapping skill families (email skills), showing the weekly report must support merge/wrap/archive recommendations without auto-executing them.
- Related issue #1726 — dead-but-relevant skills issue, showing stale/under-referenced skills should be part of the weekly signal mix.
- Related issue #1725 — historical discoverability audit showing taxonomy/discoverability work must not rely only on raw invocation counts.
- GitHub issue #2281 — child implementation issue created during planning to hold the bounded v1 execution slice for deterministic script/cron/reporting work.

### Gaps identified
- No deterministic weekly skills-audit entrypoint currently exists; the current wrapper delegates to a free-form Claude prompt.
- No explicit policy currently reconciles the audit universe mismatch between `detect_duplicate_skills.py` and `skill-usage-report.py`.
- No checked-in suppression/waiver or classification contract exists for wrapper/reference patterns, adjacent specializations, or accepted generic leaf collisions.
- No canonical JSON + Markdown artifact set currently exists for the weekly `skills-curation` run.
- No child implementation issue previously existed to separate umbrella governance from bounded v1 execution; this planning pass created #2281 to close that gap.

<!-- Verification: distinct sources >= 3. Current count: 10 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` |
| Parent issue | `#2280` |
| Child implementation issue | `#2281` |
| Existing weekly schedule entry | `config/scheduled-tasks/schedule-tasks.yaml` |
| Existing cron wrapper | `scripts/cron/skills-curation.sh` |
| Duplicate detector | `scripts/skills/detect_duplicate_skills.py` |
| Usage/staleness scorer | `scripts/skills/skill-usage-report.py` |
| Existing wrapper tests | `tests/cron/test_skills_curation.py` |
| Canonical naming tests | `tests/skills/test_skill_name_canonicalization.py` |
| Plan review — Claude | `scripts/review/results/2026-04-14-plan-2280-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-14-plan-2280-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-14-plan-2280-gemini.md` |
| Docs index update | `docs/plans/README.md` |

---

## Deliverable

A canonical governance-and-planning package for weekly skills maintenance: refined umbrella issue #2280, bounded child implementation issue #2281, and an approved plan that defines the audit universe, classification ladder, suppression rules, artifact schema contract, and cron integration rules for upgrading the existing weekly `skills-curation` workflow.

### V1 governance contract

#### Canonical identity rule
- Frontmatter `name` is the canonical skill identifier.
- Leaf-directory names are secondary signals only.
- Path/category placement is advisory unless it creates real loader/discovery ambiguity.

#### Canonical audit universe for v1
- Include repo-tracked skills under `.claude/skills/`.
- Exclude `_archive` and `_diverged` completely from v1 weekly ranking/output except optional summary metadata.
- Include `_core` and `_internal` only in a separate informational bucket; they are excluded from the main ranked section and from automatic follow-up recommendation lists in v1.
- Treat nested subskills as first-class findings only when they create canonical-name ambiguity, loader/discovery ambiguity, or true duplicate pressure; otherwise summarize them under their parent family.

#### Classification ladder and precedence
When a finding matches multiple categories, use the highest-precedence applicable class:
1. `exact-duplicate`
2. `canonical-wrapper-pair`
3. `near-duplicate-same-intent`
4. `adjacent-specialization`
5. `generic-leaf-collision`
6. `stale-superseded`
7. `needs-human-review`

Precedence rules:
- exact same canonical frontmatter `name` across active skills outranks all other classes
- a documented thin reference/stub/wrapper pointing to a richer canonical skill is `canonical-wrapper-pair`, not merge-by-default
- different canonical names with overlapping domain intent but distinct scope remain `near-duplicate-same-intent` or `adjacent-specialization`, not exact duplicates
- low-signal/dead status never overrides a higher-confidence duplicate classification

#### Suppression / waiver policy for v1
- v1 implementation must support a checked-in suppression/waiver registry consumed by the weekly audit.
- Canonical proposed path: `config/skills/weekly-audit-waivers.yaml`.
- Each waiver entry must contain at minimum:
  - `finding_key`
  - `classification`
  - `rationale`
  - `approved_by_issue`
  - `date_added`
  - optional `review_after`
- Suppressed findings must remain visible in a compact carry-forward section; they must not silently disappear.
- Unknown/expired waivers must be surfaced as audit findings.

#### Artifact contract for weekly output
The weekly job must emit a deterministic artifact set consisting of:
- JSON artifact at `logs/maintenance/skills-curation/YYYY-MM-DD.json`
- Markdown artifact at `logs/maintenance/skills-curation/YYYY-MM-DD.md`
- Cron log at `logs/maintenance/skills-curation-YYYYMMDD.log` or the canonical glob maintained by the scheduler entry

JSON artifact required fields:
- `generated_at`
- `policy_version`
- `audit_scope`
- `baseline_artifact`
- `summary_counts`
- `findings[]`
- `suppressed_findings[]`
- `errors[]`

Each finding entry must contain at minimum:
- `finding_key`
- `classification`
- `severity`
- `confidence`
- `canonical_names`
- `paths`
- `summary`
- `recommended_action`
- `is_new`
- `is_changed`

Severity / confidence rubric for v1:
- `severity=high`: exact duplicates, canonical-wrapper conflicts causing discovery ambiguity, or unstable findings likely to misroute agents today
- `severity=medium`: near-duplicates or leaf collisions with plausible productivity cost but no proven active breakage
- `severity=low`: informational findings, accepted/suppressed carry-forward items, or low-signal hygiene observations
- `confidence=high`: classification determined by deterministic repo evidence with little ambiguity
- `confidence=medium`: classification relies on bounded heuristics but remains likely correct
- `confidence=low`: evidence is conflicting or incomplete and should map to `needs-human-review`

Markdown artifact required sections:
- scope/policy summary
- new findings
- changed findings
- unresolved high-confidence findings
- suppressed/carry-forward findings
- operational errors or skipped inputs

#### Stable key / delta baseline rules
- `finding_key` must be stable across runs and derived from normalized classification + canonical names + normalized path set.
- First run behavior: if no prior JSON artifact exists, all findings are `is_new=true`, `is_changed=false`, and `baseline_artifact=null`.
- Subsequent runs compare against the most recent prior JSON artifact in `logs/maintenance/skills-curation/`.
- Unchanged findings must not be surfaced in the “new findings” section.
- `_core` and `_internal` findings are excluded from the main ranked section and from automatic follow-up recommendation lists in v1; they appear only in a separate informational bucket.

#### Decision rubric for subjective classes
- `canonical-wrapper-pair`: one artifact explicitly points to a richer canonical skill or is documented as a stub/reference/discovery path.
- `near-duplicate-same-intent`: different canonical names, substantial overlap in user intent and workflow, but neither is clearly just a wrapper/reference.
- `adjacent-specialization`: similar high-level topic but distinct domain/tool/runtime context; keep separate by default.
- `needs-human-review`: evidence is insufficient or conflicting after applying the prior rules.

#### Follow-up policy split
- The full classification/ranking policy is intentionally split into follow-up issue `#2282`.
- #2280 defines only the minimum v1 governance contract needed to keep #2281 bounded and read-only.
- #2281 must implement only the deterministic subset already frozen here; it must not invent broader ranking policy beyond this minimum contract.

#### Exit behavior
- Exit non-zero only for audit execution failures (for example: unreadable required inputs, malformed registry that prevents audit completion, or artifact write failure).
- Exit zero when findings are present but the audit completed successfully.

---

## Pseudocode

```text
plan_parent_issue_2280():
    inspect current weekly skills-curation scheduler, wrapper, detectors, docs, and tests
    define parent scope as governance + decision contract, not direct code execution
    create bounded child issue for v1 deterministic implementation slice
    codify canonical identity rule: frontmatter name wins over leaf name
    codify audit universe and suppression/waiver expectations
    codify artifact contract: JSON + Markdown + cron log
    codify classification ladder and allowed actions
    leave implementation work to child issue after approval
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` | canonical plan artifact for the umbrella issue |
| Update | `docs/plans/README.md` | add plan index row for #2280 |
| Update | GitHub issue `#2280` | tighten parent scope and record planning progress |
| Create | GitHub issue `#2281` | bounded child issue for v1 implementation of deterministic weekly audit |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_skills_curation_current_wrapper_contract_fails` | current workflow is not yet aligned with expected deterministic wrapper contract | `uv run pytest tests/cron/test_skills_curation.py -q` | failing baseline (currently 2 failures) captured as planning evidence |
| `test_child_issue_exists_for_v1_execution_slice` | umbrella issue is decomposed into a bounded implementation issue | GitHub issues `#2280` and `#2281` | `#2281` exists and links back to `#2280` |
| `test_plan_index_contains_2280_entry` | planning registry tracks the umbrella issue | `docs/plans/README.md` | row for `#2280` present |
| `test_plan_defines_audit_universe_and_classification_contract` | parent plan contains the governance rules the child implementation must follow | this plan file | explicit audit-universe, canonical-identity, and classification sections present |

---

## Acceptance Criteria

- [ ] Parent issue `#2280` is explicitly scoped as the governance/planning umbrella for weekly skills maintenance
- [ ] Child issue `#2281` exists for the bounded v1 deterministic implementation slice
- [ ] This plan is indexed in `docs/plans/README.md`
- [ ] The plan defines the canonical identity rule that frontmatter `name` is authoritative
- [ ] The plan defines the v1 audit universe and states how `_archive`, `_diverged`, `_core`, and `_internal` are handled
- [ ] The plan defines a classification ladder with precedence rules for weekly findings
- [ ] The plan defines the required weekly artifact schema contract: JSON + Markdown + cron log
- [ ] The plan defines the minimum suppression/waiver contract for accepted findings
- [ ] The plan keeps v1 read-only and explicitly forbids automatic rename/archive/issue creation in the weekly run
- [ ] Adversarial plan review artifacts are created before the plan is posted for approval

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | governance contract improved, but deterministic policy remains incomplete enough that the child issue would still have to invent core semantics during implementation |
| Codex | MAJOR | plan still leaves detector reconciliation, stable finding keys, severity/confidence rules, and baseline behavior underspecified for a trustworthy weekly audit |
| Gemini | UNAVAILABLE | provider returned repeated `429 RESOURCE_EXHAUSTED / MODEL_CAPACITY_EXHAUSTED`; no substantive review completed |

**Overall result:** FAIL — re-draft required before plan-review

Revisions made based on review:
- Revised the GitHub issue body to treat `skills-curation` as the canonical weekly path to upgrade rather than introducing a second weekly loop.
- Added explicit canonical identity rules, audit-universe guidance, classification ladder, read-only v1 constraints, and anti-churn reporting rules.
- Added concrete waiver-registry path, artifact paths, delta-baseline rules, subjective-class decision rubric, and exit-behavior expectations.
- Created bounded child issue `#2281` for the actual deterministic script/cron/reporting implementation slice.
- Saved current review artifacts under `scripts/review/results/2026-04-14-plan-2280-*.md`.

---

## Risks and Open Questions

- Risk: the parent issue could still sprawl if implementation specifics are pulled back from `#2281` into `#2280`.
- Risk: existing detectors use different inclusion/exclusion rules, so the child implementation may require explicit policy normalization before stable weekly reporting is possible.
- Risk: without a waiver/suppression mechanism, accepted wrapper/reference or adjacent-specialization patterns may reappear as noisy weekly findings.
- Decision: `_core` and `_internal` are informational-only in v1 and excluded from the main ranked section.
- Decision: the deterministic audit entrypoint should live under `scripts/skills/` with a thin cron wrapper in `scripts/cron/skills-curation.sh`.
- Open: should `severity` and `confidence` use a simple 3-level rubric in v1 (`high|medium|low`) or a richer numeric score in a follow-on issue?

---

## Complexity: T2

**T2** — this is a bounded multi-artifact planning/governance issue: one parent plan, one child implementation issue, and clear cron/taxonomy policy constraints, but no architecture-wide multi-repo decomposition is required at this stage.
