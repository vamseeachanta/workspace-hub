# Plan for #2281: implement v1 weekly audit for existing skills-curation workflow

> **Status:** completed
> Complexity: T2
> Date: 2026-04-14
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2281
> Review artifacts: scripts/review/results/2026-04-14-plan-2281-claude.md | scripts/review/results/2026-04-14-plan-2281-codex.md | scripts/review/results/2026-04-14-plan-2281-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — the canonical scheduler already declares `skills-curation` as a Monday 04:00 weekly task; #2281 should maintain that task ID/path rather than invent a second weekly job.
- Found: `scripts/cron/skills-curation.sh` — current wrapper is only a Claude prompt launcher, so the main implementation gap is replacing or upgrading it to a deterministic entrypoint with stable outputs.
- Found: `tests/cron/test_skills_curation.py` — the existing wrapper test contract is currently failing and expects explicit `--print` behavior for invocation/dry-run, so #2281 should either satisfy or deliberately update that wrapper contract through TDD.
- Found: `scripts/skills/detect_duplicate_skills.py` — available deterministic detector for duplicate frontmatter names and leaf collisions; this should be a core input into the new weekly audit instead of duplicating the logic.
- Found: `scripts/skills/skill-usage-report.py` — available usage/reference scoring script; useful for stale/low-signal review, but it currently uses a different exclusion policy than the duplicate detector.
- Found: `tests/skills/test_skill_name_canonicalization.py` — canonical-name test already proves frontmatter `name` should be preferred over leaf directory names; #2281 should preserve this rule in the weekly audit logic.

### Standards
| Standard | Status | Source |
|---|---|---|
| Cron task governance via YAML + installer + validator | done / required pattern | `docs/ops/scheduled-tasks.md`, `scripts/cron/setup-cron.sh`, `scripts/cron/validate-schedule.py` |
| Control-plane contract | done / relevant | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Parent governance contract for weekly skills maintenance | draft but authoritative for this child | `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` |

### LLM Wiki pages consulted
- No relevant wiki pages found; this is deterministic harness/taxonomy cron work, not domain wiki content.

### Documents consulted
- Parent issue #2280 — defines the umbrella governance intent and v1 guardrails for the child implementation.
- `docs/ops/scheduled-tasks.md` — operator-facing scheduled-task inventory; currently references `skills-curation` and should be updated to reflect the deterministic v1 workflow.
- Related issue #2083 — concrete exact-duplicate case (`session-corpus-audit`) useful as a fixture/example for duplicate classification.
- Related issue #2019 — concrete consolidation family (email skills) useful as a fixture/example for near-duplicate vs intentional grouping.
- Related issue #1726 — dead-but-relevant skill review input showing weekly maintenance must account for low-signal but active-domain skills.

### Gaps identified
- No deterministic skills-audit entrypoint currently exists.
- No canonical JSON + Markdown artifact contract exists for weekly `skills-curation` output.
- No single normalized audit universe is shared across duplicate and usage/staleness analysis.
- No suppression/waiver mechanism exists for accepted wrapper/reference or adjacent-specialization cases.
- Current wrapper tests are red, so the existing weekly workflow is already not aligned with repo expectations.

<!-- Verification: distinct sources >= 3. Current count: 9 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md` |
| Parent plan | `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` |
| Existing cron wrapper | `scripts/cron/skills-curation.sh` |
| Deterministic audit entrypoint | `scripts/skills/weekly_skills_audit.py` (proposed) |
| Schedule config | `config/scheduled-tasks/schedule-tasks.yaml` |
| Operator docs | `docs/ops/scheduled-tasks.md` |
| Cron wrapper tests | `tests/cron/test_skills_curation.py` |
| Audit classification tests | `tests/skills/test_weekly_skills_audit.py` (proposed) |
| Plan review — Claude | `scripts/review/results/2026-04-14-plan-2281-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-14-plan-2281-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-14-plan-2281-gemini.md` |

---

## Deliverable

A deterministic, read-only weekly `skills-curation` workflow that preserves the existing scheduled-task path, runs a canonical v1 skills audit over the defined skill universe, and emits stable JSON + Markdown + cron-log artifacts suitable for weekly maintenance review.

### V1 implementation contract
- Keep task ID `skills-curation` in `config/scheduled-tasks/schedule-tasks.yaml`
- Implement deterministic audit logic in `scripts/skills/weekly_skills_audit.py`
- Keep `scripts/cron/skills-curation.sh` as a thin wrapper around that deterministic script
- Update the scheduler contract so `skills-curation` no longer advertises a Claude-only task once the deterministic implementation lands (`requires` and `is_claude_task` must match reality)
- Treat frontmatter `name` as the canonical skill identifier
- Exclude `_archive` and `_diverged`
- Treat `_core` and `_internal` as informational-only in v1: separate bucket, excluded from main ranked findings
- Use a minimal deterministic bucket rubric only:
  - `exact-duplicate`
  - `canonical-wrapper-pair`
  - `adjacent-specialization`
  - `generic-leaf-collision`
  - `needs-human-review`
- Defer richer ranking/classification refinements to follow-up issue `#2282`
- Keep the workflow read-only in v1: no auto-rename, no auto-archive, no auto-issue creation
- Use checked-in waiver registry path `config/skills/weekly-audit-waivers.yaml`

### Required output contract
- JSON artifact: `logs/maintenance/skills-curation/YYYY-MM-DD.json`
- Markdown artifact: `logs/maintenance/skills-curation/YYYY-MM-DD.md`
- Cron log: `logs/maintenance/skills-curation-YYYYMMDD.log` or canonical scheduler glob
- Manual/TDD runs must support redirectable output roots via CLI flag or environment variable so tests can write to temp directories without dirtying the repo
- In v1, Markdown summary behavior is intentionally bounded:
  - section 1: new findings
  - section 2: changed findings
  - section 3: unresolved high-confidence findings
  - section 4: suppressed/carry-forward findings
  - section 5: operational errors
- Detailed ranking-policy refinements beyond this minimal summary structure are deferred to follow-up issue `#2282`

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

---

## Pseudocode

```text
main():
    load canonical skill inventory from .claude/skills using one normalized exclusion policy
    exclude _archive and _diverged
    treat _core and _internal as informational-only findings
    collect duplicate frontmatter names and leaf collisions
    classify findings into the bounded v1 buckets only:
        exact duplicate
        canonical + wrapper/reference
        adjacent specialization
        generic leaf collision only
        needs-human-review
    load waiver registry from config/skills/weekly-audit-waivers.yaml when present
    compute stable finding keys and compare against the most recent prior JSON artifact
    write stable JSON artifact
    write bounded Markdown summary
    exit zero on successful audit even when findings exist
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/skills/weekly_skills_audit.py` | deterministic weekly audit entrypoint |
| Modify | `scripts/cron/skills-curation.sh` | convert wrapper to deterministic script launcher with correct dry-run/print contract |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | preserve canonical task ID while updating `requires`, `is_claude_task`, description, and log/command contract for deterministic execution |
| Modify | `docs/ops/scheduled-tasks.md` | document the deterministic workflow and output paths |
| Modify | `tests/cron/test_skills_curation.py` | preserve or intentionally evolve wrapper contract through TDD |
| Create | `tests/skills/test_weekly_skills_audit.py` | fixture-based tests for classification, inventory scope, output schema, delta behavior, and waiver handling |
| Update | `docs/plans/README.md` | add this plan to the plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_skills_curation_wrapper_prints_deterministic_command` | wrapper dry-run/print contract is explicit and stable | `bash scripts/cron/skills-curation.sh --dry-run` | output shows deterministic script invocation and no live run |
| `test_weekly_skills_audit_excludes_archive_and_diverged` | inventory uses v1 exclusion policy | fixture tree with `_archive`, `_diverged`, normal skills | archived/diverged skills absent from findings |
| `test_weekly_skills_audit_treats_frontmatter_name_as_canonical` | canonical identity uses frontmatter `name` | fixture pair with same leaf but distinct frontmatter names | finding reflects canonical names, not forced duplicate |
| `test_weekly_skills_audit_handles_missing_or_malformed_frontmatter` | malformed skills are reported deterministically instead of corrupting the audit | fixture corpus with missing/invalid frontmatter | finding/error recorded without crashing run |
| `test_weekly_skills_audit_reports_duplicate_frontmatter_names_separately_from_leaf_collisions` | duplicate types are bucketed distinctly | fixture corpus with both cases | separate finding sections/buckets |
| `test_weekly_skills_audit_buckets_internal_and_core_findings_separately` | `_core` and `_internal` do not dominate ranking | fixture corpus with repeated internal/core subskills | findings placed in informational-only bucket |
| `test_weekly_skills_audit_classifies_known_wrapper_pair` | documented wrapper/reference pair is not escalated as a merge candidate | fixture corpus with canonical+stub pair | classification = `canonical-wrapper-pair` |
| `test_weekly_skills_audit_classifies_adjacent_specialization` | similar topic but distinct domain/tooling stays separate | fixture corpus with specialized pair | classification = `adjacent-specialization` |
| `test_weekly_skills_audit_computes_stable_finding_keys_across_unchanged_runs` | unchanged inputs do not churn delta semantics | same fixture corpus across two runs | same `finding_key`, `is_new=false` on second run |
| `test_weekly_skills_audit_handles_first_run_without_baseline` | first run behavior is explicit | no prior JSON artifact present | `baseline_artifact=null`, findings marked new |
| `test_weekly_skills_audit_ignores_incompatible_baseline_versions` | incompatible prior artifacts do not corrupt weekly delta logic | prior JSON with different `policy_version` or `audit_scope` | run succeeds and marks baseline incompatible/ignored |
| `test_weekly_skills_audit_applies_and_surfaces_waivers` | waiver registry suppresses but does not hide accepted findings | fixture corpus + waiver file | suppressed finding appears in carry-forward section |
| `test_weekly_skills_audit_outputs_json_schema_and_markdown_summary` | artifact contract is stable | fixture audit run | JSON + Markdown files created with required keys/sections |
| `test_weekly_skills_audit_is_read_only` | v1 makes no repo mutations | fixture repo state | no file changes outside artifact paths |
| `test_validate_schedule_still_passes_with_skills_curation_task` | scheduler config remains valid | updated YAML | validator exits 0 |

---

## Acceptance Criteria

- [ ] New deterministic audit entrypoint exists and runs manually
- [ ] Existing `skills-curation` task remains the canonical weekly scheduler path
- [ ] Scheduler metadata (`requires`, `is_claude_task`, description/log contract) matches the deterministic implementation reality
- [ ] Wrapper dry-run/print behavior is deterministic and covered by tests
- [ ] Frontmatter `name` is used as the canonical identifier in audit logic
- [ ] `_archive` and `_diverged` are excluded from v1 scope
- [ ] `_core` and `_internal` findings are separately bucketed/de-emphasized
- [ ] Duplicate frontmatter names and leaf collisions are reported separately
- [ ] JSON + Markdown + cron-log outputs are produced in stable paths
- [ ] Manual/TDD runs can redirect output roots to temp paths without dirtying the repo
- [ ] Workflow is read-only in v1
- [ ] `uv run --no-project python scripts/cron/validate-schedule.py` passes
- [ ] `bash scripts/cron/setup-cron.sh --dry-run` renders the maintained `skills-curation` task cleanly
- [ ] Plan review artifacts are posted before implementation begins

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | bounded implementation plan is much stronger, but subjective classification rules, baseline behavior, and scheduler-metadata migration still need tighter deterministic definition |
| Codex | MAJOR | scheduler metadata, baseline handling, redirectable output roots, and ranking/carry-forward behavior remain underspecified for trustworthy weekly operation |
| Gemini | UNAVAILABLE | provider returned repeated `429 RESOURCE_EXHAUSTED / MODEL_CAPACITY_EXHAUSTED`; no substantive review completed |

**Overall result:** FAIL — re-draft required before plan-review

Revisions made based on review:
- Added deterministic implementation location: `scripts/skills/weekly_skills_audit.py` with thin cron wrapper in `scripts/cron/skills-curation.sh`.
- Added canonical waiver-registry path `config/skills/weekly-audit-waivers.yaml`.
- Added concrete artifact paths, output-root redirection requirement for TDD/manual runs, and richer output schema expectations.
- Added tests for malformed frontmatter, stable finding keys across unchanged runs, first-run baseline behavior, incompatible baseline handling, and waiver application.
- Elevated scheduler metadata alignment (`requires`, `is_claude_task`, description/log contract) into explicit implementation acceptance criteria.

---

## Risks and Open Questions

- Risk: detector-scope mismatch between duplicate and usage/staleness inputs may create unstable weekly findings unless normalized early.
- Risk: wrapper tests may need a deliberate contract rewrite if the deterministic entrypoint changes CLI shape.
- Risk: accepted wrapper/reference cases may create recurring noise until the waiver mechanism is implemented correctly.
- Decision: suppression/waiver data should live in repo-tracked config at `config/skills/weekly-audit-waivers.yaml`.
- Decision: the deterministic audit entrypoint should live under `scripts/skills/` with a thin cron wrapper in `scripts/cron/skills-curation.sh`.
- Decision: v1 uses only the bounded deterministic bucket set defined in this plan; richer ranking/classification policy is deferred to `#2282`.
- Open: should v1 `severity` / `confidence` stay at simple `high|medium|low` levels or gain a richer numeric score in a follow-on issue after signal quality is proven?

---

## Complexity: T2

**T2** — bounded multi-file harness work touching one new deterministic script, one cron wrapper, one schedule declaration, docs, and tests, without requiring broader multi-repo architecture changes.
