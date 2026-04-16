# Plan for #2271: harden shared-skill propagation for engineering portability

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2271
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2271-claude-overnight.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/sync-knowledge-work-plugins.sh` — existing propagation script that syncs skills from `anthropics/knowledge-work-plugins` into workspace-hub. Supports `--dry-run`, `--sync`, `--diff`, `--plugin=<name>` modes. Maps 11 upstream plugin categories to local skill directory paths. This is the primary existing propagation mechanism and the strongest candidate for hardening.
- Found: `scripts/skills/merge-submodule-skills.sh` — one-time script for merging skills from submodule repos (digitalmodel, worldenergydata, aceengineer-admin, aceengineer-website) into workspace-hub's centralized skill directory. Supports `--apply`, `--diff`, dry-run by default. Has routing functions (`dm_route`, `wed_route`, `admin_route`, `website_route`) with pattern-matched skill-to-directory mapping. Has a `SKIP_DIRS` variable for shared/template directories. This script handles internal cross-repo propagation.
- Found: `scripts/skills/detect_duplicate_skills.py` — detects duplicate skills across the ecosystem.
- Found: `scripts/skills/audit-skills.py` — audits skill quality and structure.
- Found: `scripts/skills/audit-diverged.py` — audits skills that have diverged from their upstream sources.
- Found: `scripts/skills/check-skill-pipeline-health.sh` — health check for the skill pipeline.
- Gap: neither propagation script has regression tests in `tests/`.
- Gap: `merge-submodule-skills.sh` does not report skipped repos with reasons (only skips directories matching `SKIP_DIRS` silently).
- Gap: neither script validates provider adapter state after propagation.
- Gap: no explicit dry-run review workflow is documented — the `--dry-run` flag exists but there is no enforced "review before apply" gate.

### Standards
| Standard | Status | Source |
|---|---|---|
| Skill propagation contracts | partially covered | `scripts/skills/sync-knowledge-work-plugins.sh`, `scripts/skills/merge-submodule-skills.sh` |
| Engineering artifact portability | done | `docs/engineering/portability/PORTABILITY_CONTRACT.md` |
| Control plane contract | exists | referenced in plan template; checked `CONTROL_PLANE_CONTRACT.md` locations |

### LLM Wiki pages consulted
- No relevant wiki pages found for skill propagation mechanics. The engineering wiki covers domain knowledge (OpenFOAM, mooring, etc.) but not harness infrastructure.

### Documents consulted
- GitHub issue #2271 — defines acceptance criteria for hardening shared-skill propagation with dry-run safety, skip reporting, and regression tests.
- GitHub issue #1782 — parent epic (zero-loss agent learnings) driving portability and propagation hardening.
- GitHub issue #26 — Blender configs (related to engineering portability scope).
- GitHub issue #25 — OpenFOAM capability (related to engineering portability scope).
- `docs/engineering/portability/PORTABILITY_CONTRACT.md` — defines what must be portable; skill propagation is the mechanism that delivers portability.
- `.claude/rules/patterns.md` — enforcement gradient (Level 0-3); propagation hardening aligns with Level 2 (script) enforcement.
- `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` — sibling plan demonstrating the delivery pattern for #1782 child issues.
- `docs/SKILLS_INDEX.md` — skills index that propagation scripts must keep consistent.

### Gaps identified
- No regression tests exist for either propagation script (`sync-knowledge-work-plugins.sh` or `merge-submodule-skills.sh`).
- Skipped repos are not reported with reasons in `merge-submodule-skills.sh` — the `SKIP_DIRS` mechanism is silent.
- Placeholder/shared-link edge cases are not documented or handled explicitly (e.g., symlinks, empty SKILL.md files, shared templates that are not actual skills).
- No enforced dry-run-before-apply gate exists; the `--dry-run` flag is available but not mandatory.
- Provider adapter state (e.g., `config/ai-tools/` JSON files, `.claude/settings.json`) is not validated after propagation.
- No machine-readable propagation report is generated (only terminal stdout).

<!-- Verification: distinct sources >= 3. Current count: 8 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-16-issue-2271-harden-shared-skill-propagation-for-engineering-portability.md` |
| Updated propagation script (external) | `scripts/skills/sync-knowledge-work-plugins.sh` |
| Updated propagation script (internal) | `scripts/skills/merge-submodule-skills.sh` |
| Propagation dry-run report template | `scripts/skills/propagation-report-template.yaml` |
| Regression test harness | `tests/skills/test_propagation_scripts.py` |
| Propagation hardening doc | `docs/engineering/portability/skill-propagation-hardening.md` |
| Plan review — Claude | `scripts/review/results/2026-04-16-plan-2271-claude-overnight.md` |

---

## Deliverable

Hardened shared-skill propagation scripts with mandatory dry-run reporting, explicit skip-reason logging, placeholder/shared-link edge case handling, provider adapter state validation, and a regression test harness that prevents propagation regressions across the multi-repo ecosystem.

---

## Pseudocode

```text
# --- Harden sync-knowledge-work-plugins.sh ---

enhance dry-run mode:
    when --dry-run is invoked:
        generate machine-readable YAML report to stdout or --report-file
        report format:
            generated_at: <timestamp>
            mode: dry-run
            source: anthropics/knowledge-work-plugins
            plugins_checked: <list>
            actions:
                - plugin: <name>
                  skill: <skill-slug>
                  action: create | update | skip | conflict
                  reason: <human-readable reason>
                  source_path: <upstream path>
                  target_path: <local path>
            skipped:
                - plugin: <name>
                  skill: <skill-slug>
                  reason: <why skipped>
            summary:
                total_checked: N
                would_create: N
                would_update: N
                skipped: N
                conflicts: N

add explicit skip reporting:
    when a skill is skipped (already exists, unmapped, conflicts):
        log the skill name, source path, and reason to the report
        do not silently continue

add placeholder/shared-link detection:
    before copying a skill:
        check if target is a symlink -> log as shared-link edge case
        check if source SKILL.md is empty or placeholder-only -> log and skip
        check if source is a shared template (in SKIP_DIRS) -> log and skip

# --- Harden merge-submodule-skills.sh ---

add skip-reason reporting:
    replace silent SKIP_DIRS filtering with explicit logging:
        for each skipped directory: log name and reason (matched SKIP_DIRS pattern)
    for each unmapped skill: log name and reason (no route match)
    for each repo that is not cloned/available: log repo name and reason

add propagation report:
    emit machine-readable YAML report alongside terminal output
    report format mirrors sync-knowledge-work-plugins.sh structure

# --- Provider adapter state validation ---

after propagation completes (in both scripts):
    validate provider adapter state:
        check .claude/settings.json is valid JSON
        check config/ai-tools/*.json files are valid JSON
        check no SKILL.md files have been corrupted (non-empty, valid frontmatter)
    if validation fails:
        report as propagation error, do not silently succeed
        suggest rollback command

# --- Regression tests ---

test_propagation_dry_run_produces_valid_report:
    run sync-knowledge-work-plugins.sh --dry-run
    parse YAML output
    verify structure matches schema

test_propagation_skip_reporting_captures_reasons:
    mock a scenario with unmapped skills
    verify each skip has a non-empty reason field

test_propagation_detects_placeholder_skills:
    create a fixture with an empty SKILL.md
    run propagation in dry-run mode
    verify the placeholder is reported and skipped

test_propagation_detects_symlink_edge_case:
    create a fixture with a symlinked skill directory
    run propagation in dry-run mode
    verify the symlink is reported

test_merge_submodule_reports_missing_repos:
    run merge-submodule-skills.sh with a nonexistent submodule path
    verify the missing repo is reported with reason

test_provider_adapter_state_valid_after_propagation:
    run propagation in apply mode against fixtures
    validate .claude/settings.json and config/ai-tools/*.json are valid JSON

test_propagation_does_not_corrupt_existing_skills:
    snapshot existing skill files before propagation
    run propagation
    verify no existing skill was deleted or truncated
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update | `scripts/skills/sync-knowledge-work-plugins.sh` | add dry-run YAML report, skip-reason logging, placeholder detection |
| Update | `scripts/skills/merge-submodule-skills.sh` | add skip-reason reporting, propagation report, missing-repo handling |
| Create | `scripts/skills/propagation-report-template.yaml` | schema definition for machine-readable propagation reports |
| Create | `tests/skills/test_propagation_scripts.py` | regression test harness for both propagation scripts |
| Create | `docs/engineering/portability/skill-propagation-hardening.md` | documents the propagation hardening contract, dry-run workflow, and edge cases |
| Update | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` | cross-reference skill propagation hardening |
| Update | `docs/README.md` | add discoverability link to propagation hardening doc |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_sync_dry_run_produces_valid_yaml_report` | dry-run mode emits parseable YAML with required schema fields | `--dry-run` invocation | YAML with generated_at, mode, source, plugins_checked, actions, skipped, summary |
| `test_sync_skip_reporting_captures_reasons` | every skipped skill has a non-empty reason | dry-run with unmapped/conflicting skills | all skipped entries have reason field |
| `test_sync_detects_placeholder_skills` | empty or placeholder SKILL.md files are detected and skipped | fixture with empty SKILL.md | placeholder reported in skipped list |
| `test_sync_detects_symlink_edge_case` | symlinked skill directories are reported | fixture with symlinked skill | symlink reported as edge case |
| `test_merge_reports_skipped_dirs_with_reasons` | SKIP_DIRS matches are logged with reason | standard run with shared/template dirs | each skipped dir has name and matched pattern |
| `test_merge_reports_missing_repos` | unavailable submodule repos are reported | nonexistent submodule path | missing repo reported with reason |
| `test_merge_reports_unmapped_skills` | skills with no route match are reported | fixture with unknown skill prefix | unmapped skill logged with name |
| `test_provider_adapter_state_valid_after_sync` | .claude/settings.json and config/ai-tools/*.json remain valid JSON | post-propagation state | all JSON files parse successfully |
| `test_propagation_does_not_corrupt_existing_skills` | existing skills are not deleted or truncated | pre/post snapshot comparison | no skill file smaller or missing after propagation |
| `test_dry_run_makes_no_file_changes` | dry-run mode does not modify any files | `--dry-run` with file timestamp snapshot | all timestamps unchanged |

---

## Acceptance Criteria

- [ ] `scripts/skills/sync-knowledge-work-plugins.sh --dry-run` produces a machine-readable YAML report with all required schema fields.
- [ ] Both propagation scripts report skipped repos/skills with explicit human-readable reasons.
- [ ] Placeholder/shared-link edge cases are detected and handled (empty SKILL.md, symlinks, shared templates).
- [ ] Provider adapter state (`.claude/settings.json`, `config/ai-tools/*.json`) is validated after propagation; corruption is reported as an error.
- [ ] `tests/skills/test_propagation_scripts.py` exists with regression tests covering dry-run report schema, skip reporting, placeholder detection, and state validation.
- [ ] Shared engineering skills propagate cleanly from upstream (anthropics/knowledge-work-plugins) and internal repos (digitalmodel, worldenergydata, etc.).
- [ ] `docs/engineering/portability/skill-propagation-hardening.md` documents the dry-run workflow, edge cases, and propagation report schema.
- [ ] Dry-run is reviewed before real changes are applied (workflow documented, though enforcement is Level 0 prose for now).

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | overnight draft review |
| Codex | pending | not yet reviewed |
| Gemini | pending | not yet reviewed |

**Overall result:** pending

Revisions made based on review:
- (none yet — initial draft)

---

## Requirement traceability

| Issue #2271 requirement | Planned deliverable(s) | Planned test(s) | Acceptance criteria |
|---|---|---|---|
| propagation dry-run reviewed before real changes | updated propagation scripts with YAML report, `docs/engineering/portability/skill-propagation-hardening.md` | `test_sync_dry_run_produces_valid_yaml_report`, `test_dry_run_makes_no_file_changes` | dry-run produces report; workflow documented |
| placeholder/shared-link edge cases resolved or documented | updated scripts with detection logic, hardening doc | `test_sync_detects_placeholder_skills`, `test_sync_detects_symlink_edge_case` | edge cases detected and reported |
| skipped repos reported with reasons | updated scripts with skip-reason logging | `test_sync_skip_reporting_captures_reasons`, `test_merge_reports_skipped_dirs_with_reasons`, `test_merge_reports_missing_repos` | all skips include reasons |
| shared engineering skills propagate cleanly | updated scripts, regression tests | `test_propagation_does_not_corrupt_existing_skills` | no corruption after propagation |
| propagation-script behavior changes covered by regression tests | `tests/skills/test_propagation_scripts.py` | all tests in harness | test file exists with required coverage |
| provider adapter state remains valid | post-propagation validation in scripts | `test_provider_adapter_state_valid_after_sync` | JSON files valid after propagation |

---

## Risks and Open Questions

- **Risk:** The two propagation scripts (`sync-knowledge-work-plugins.sh` and `merge-submodule-skills.sh`) have different architectures (external HTTP fetch vs local filesystem copy); hardening must respect each script's existing contract while adding consistent reporting.
- **Risk:** Adding YAML report generation to bash scripts may require `yq` or embedded Python for reliable YAML output; the implementation should prefer `python3` inline (matching the pattern from #2269) over introducing a new dependency.
- **Risk:** Testing bash scripts from pytest requires subprocess invocation and fixture management; the test harness must handle both "fixture-only" tests (any host) and "live propagation" tests (require network/repos).
- **Open:** Should dry-run be enforced as mandatory before `--sync`/`--apply`, or remain advisory? Current plan keeps it at Level 0 (prose) enforcement.
- **Open:** How should symlinked skills be handled — skip with warning, or resolve and propagate the target? Plan defaults to skip-with-warning pending user decision.

---

## Complexity: T2

**T2** — hardening two existing scripts with reporting enhancements, adding a new regression test harness, and creating one documentation file. Multiple files affected but bounded scope within the skill propagation subsystem.
