# Existing pull request test coverage

The workflow definitions at the starting revision run selected Python and shell
tests on pull requests. They do not run the complete hub test inventory.
This is a source inspection, not evidence of hosted execution or branch protection.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| 1 | 2026-10-22 | Record every existing workflow before adding family selection. |

All existing files in `.github/workflows/` were read. The new family workflow is
described separately in [the family guide](hub-test-families.md).

| Workflow file | Pull request trigger and filters | Test commands and other checks |
|---|---|---|
| `baseline-check.yml` | PRs targeting main; no path filter | Python test commands listed below; advisory ruff and governance checks |
| `enforcement-gate.yml` | PRs targeting main: opened, synchronize, reopened; no path filter | Import smoke test; two shell harnesses listed below; scheduler, prompt, review, retired-approval compatibility, label provenance, queue, model and skill-index guards |
| `skills-validation.yml` | PRs targeting main; skill definitions, skill tooling, two regression files and the workflow itself | Validator; `tests/enforcement/test_validate_skills_frontmatter.py`; `tests/cron/test_skill_validation_uv_resolution.py` |
| `fleet-snapshot-labels.yml` | PRs targeting main; snapshot reports, label script, its test and the workflow itself | `tests/fleet/test_fleet_snapshot_labels.py`, with `-k "not only_the_latest_snapshot_is_kept"` |
| `public-surface-guard.yml` | PRs targeting main: opened, synchronize, reopened; no path filter | Added-line guard and identifier warning; no fixed test command |
| `no-abs-paths-report.yml` | PRs targeting main; no path filter | Report-only path guard; no pytest command |
| `claude-code-review.yml` | PRs: opened, synchronize, ready_for_review, reopened; no active path filter | Review action; no fixed test command |
| `claude.yml` | Comment, review and issue events, conditional on a mention | Assistant action; no fixed PR test command |
| `domain-matrix.yml` | Reusable workflow_call only | Caller-provided selector and test command; no hub PR caller |
| `domain-coverage.yml` | Schedule and manual only | Coverage guard; no PR tests |
| `multi-ai-review.yml` | Manual only | Prints review instructions and checks script existence |
| `pages.yml` | Push to main with source path filters; manual | Builds the site; no PR tests |
| `scheduler-mutation-main.yml` | Push to main only | Scheduler registry, identity inventory and report checks |
| `autoapply-completeness-label.yml` | Issue opened/labeled only | Label mutation; no PR tests |
| `completeness-gate.yml` | Issue closed only | Completeness evaluation; no PR tests |

Table 1. Existing workflow triggers and fixed test coverage, read from their definitions.

The baseline workflow invokes `uv run python -m pytest` on these targets:

- `tests/test_deduplication_fix.py`, `tests/quality/test_gitleaks_config.py`,
  `scripts/operations/tests/test_job_queue_windows.py`,
  `scripts/operations/tests/test_job_queue_cleanup_recent.py` and
  `tests/enforcement/test_check_codex_model_pin.py`, with `--noconftest`.
- `tests/ci_smoke/`, with `PYTHONPATH=src`.
- `tests/enforcement/test_script_reference_integrity.py`.
- `tests/enforcement/test_check_engineering_register.py`,
  `tests/enforcement/test_check_shell_conditional_helpers.py`,
  `tests/enforcement/test_check_shell_conditional_helpers_scopes.py`,
  `tests/enforcement/test_shell_test_guards.py` and
  `tests/enforcement/test_no_abs_paths_ci_report.py`.
- `tests/operations/storage`.

The enforcement workflow also runs
`tests/ci_smoke/test_workspace_hub_importable.py`,
`scripts/enforcement/tests/test_check_archived_marine_skills.sh` and
`scripts/cron/tests/test_ecosystem_sync_push_guard.sh`.
Shell harnesses remain outside the new Python inventory.

The requested open-PR search for `ci test families` returned no matches.
Other open changes edit `enforcement-gate.yml` and `domain-coverage.yml`; neither
file is changed here. An open collection-audit change uses separate files under
`scripts/testing/`, `tests/testing/` and `docs/testing/`; those files are also
unchanged. The reusable domain workflow remains unchanged.
