"""Regression guard — every script the repo INVOKES BY PATH must be tracked 100755.

Consolidates and replaces two near-duplicate guards:
  * tests/review/test_helpers_executable.py          (#3142, review helpers)
  * tests/operations/test_merge_helper_executable.py (#3798, merge babysitter)
Both hardcoded a one-element list and asserted the same property. A third
near-duplicate would have been the wrong answer to "56 more files are broken",
so the two originals are deleted and their entries carried into the single
canonical map below — no coverage is lost, and there is now exactly one place to
register a newly path-invoked script.

THE DISCRIMINATOR
-----------------
A blanket `chmod +x` on every tracked *.sh would be WRONG. Only scripts resolved
and executed by the kernel need the bit:

  NEEDS the bit (listed here):
      ./foo.sh              "$SCRIPT_DIR/foo.sh"      scripts/x/foo.sh --flag
      ExecStart=/…/foo.sh   run_check "$DIR/foo.sh"   (wrapper that runs "$@")

  Does NOT need the bit (deliberately absent):
      bash foo.sh / sh foo.sh          — the script is an ARGUMENT to an interpreter
      uv run python foo.py             — likewise
      source foo.sh / . foo.sh         — SOURCED into the caller's shell

Marking a sourced library executable is worse than leaving it alone: a missing
exec bit is a loud, obvious `Permission denied`, while a wrongly-executable
library is a silent lie about how the file is meant to be used. Example of a file
that must STAY 100644: scripts/operations/system/ssh-helpers.sh, whose own header
documents `source`-ing it.

WHY `git ls-tree HEAD` AND NOT `git ls-files -s`
------------------------------------------------
This repo sets `core.fileMode = false`. A staged `git update-index --chmod=+x`
can sit in the INDEX while `git commit -- <pathspec>` (which re-reads the working
tree and ignores the filesystem bit) commits 100644. `ls-files -s` then reports
the fix and the tree does not — a false green over a still-broken commit, which
is exactly what happened while #3798 was being written. HEAD is the artifact that
ships to a fresh clone; assert on HEAD.

Level-2 enforcement of the prose rule "scripts invoked directly must be
executable" (.claude/rules/patterns.md enforcement gradient).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# path -> one concrete invocation site proving the exec bit is required.
PATH_INVOKED_SCRIPTS: dict[str, str] = {
    # --- carried over from the two guards this file replaces ---
    'scripts/review/validate-review-output.sh':
        'scripts/review/submit-to-codex.sh — "$VALIDATOR" "$rendered_file" (#3142)',
    'scripts/operations/merge-when-clean.sh':
        '.claude/rules/merge-authorization.md rule 8 — mandatory path invocation (#3798)',

    # --- repo-wide audit of all 717 tracked-100644 *.sh files ---
    # Kept only where a real execution context (shell/CI/systemd/wrapper) or an
    # authoritative contract surface (.claude/rules, .claude/commands, a
    # co-located README) invokes the script BY PATH.
    'scripts/ai/review-routing-gate.sh':
        'scripts/ai/review-routing-gate.sh:6 — # git diff main...HEAD | scripts/ai/review-routing-gate.sh --stdin',
    'scripts/analysis/daily-reflect.sh':
        '.agents/skills/workspace-hub/claude-reflect/scripts/run-reflection.sh:75 — "$SCRIPT_DIR/daily-reflect.sh" >> "$LOG_FILE" 2>&1 || {',
    'scripts/automation/propagate-slash-commands.sh':
        'scripts/automation/README.md:28 — ./propagate-slash-commands.sh',
    'scripts/benchmarks/perf-bench.sh':
        'scripts/benchmarks/ntfs3-trial.sh:164 — [$BENCH <- L26] "$BENCH" post-ntfs3',
    'scripts/coordination/context/analyze_patterns.sh':
        'scripts/coordination/context/daily_context_check.sh:48 — "$SCRIPT_DIR/analyze_patterns.sh" 7 >> "$REPORT_FILE" 2>&1 || true',
    'scripts/coordination/context/improve_context.sh':
        'scripts/coordination/context/daily_context_check.sh:60 — "$SCRIPT_DIR/improve_context.sh" --dry-run >> "$REPORT_FILE" 2>&1 || true',
    'scripts/coordination/context/optimize_context.sh':
        'scripts/coordination/context/daily_context_analysis.sh:304 — if "$SCRIPT_DIR/optimize_context.sh" --repo "$repo" >> "$LOG_FILE" 2>&1; then',
    'scripts/coordination/context/validate_context.sh':
        'scripts/coordination/context/daily_context_check.sh:36 — "$SCRIPT_DIR/validate_context.sh" >> "$REPORT_FILE" 2>&1 || true',
    'scripts/coordination/git/batch_commit_all.sh':
        '_archive/modules/documentation/README_MANAGEMENT.md:111 — ./batch_commit_all.sh "commit message"',
    'scripts/coordination/git/check_all_repos_status.sh':
        '_archive/modules/documentation/README_MANAGEMENT.md:106 — ./check_all_repos_status.sh',
    'scripts/coordination/git/check_trunk_status.sh':
        '_archive/modules/ci-cd/FINAL_CLEANUP_REPORT.md:64 — ./check_trunk_status.sh',
    'scripts/coordination/git/git_sync_all.sh':
        '_archive/modules/documentation/README_MANAGEMENT.md:83 — ./git_sync_all.sh',
    'scripts/coordination/git/pull_all_repos.sh':
        'scripts/coordination/git/README.md:35 — ./pull_all_repos.sh',
    'scripts/cron/daily-cleanup.sh':
        '.claude/commands/reconcile-ecosystem.md:49 — scripts/cron/daily-cleanup.sh --dry-run',
    'scripts/data/og-standards/setup.sh':
        'scripts/data/og-standards/README.md:20 — ./setup.sh',
    'scripts/development/ai-review/codex-review.sh':
        'scripts/development/ai-review/cross-review-loop.sh:266 — "$SCRIPT_DIR/codex-review.sh" "$commit" > "$review_file" 2>&1 || true',
    'scripts/development/ai-workflow/auto-fix-loop.sh':
        'scripts/development/ai-workflow/run-workflow.sh:265 — "${SCRIPT_DIR}/auto-fix-loop.sh" "${args[@]}" || true',
    'scripts/development/ai-workflow/primary-claude.sh':
        'scripts/development/ai-workflow/run-workflow.sh:162 — "${SCRIPT_DIR}/primary-claude.sh" "${args[@]}" || true',
    'scripts/development/ai-workflow/review-openai.sh':
        'scripts/development/ai-workflow/auto-fix-loop.sh:304 — "${SCRIPT_DIR}/review-openai.sh" --files "$files" --report "$review_report" --severity',
    'scripts/development/ai-workflow/test-runner.sh':
        'scripts/development/ai-workflow/run-workflow.sh:219 — "${SCRIPT_DIR}/test-runner.sh" "${args[@]}" --coverage || true',
    'scripts/dispatch/overnight-2026-05-13/00-tonight-issue-2702-routing-audit.sh':
        'scripts/dispatch/overnight-2026-05-13/README.md:12 — ./00-tonight-issue-2702-routing-audit.sh',
    'scripts/enforcement/check-completeness-before-close.sh':
        '.claude/rules/completeness-before-close.md:19 — scripts/enforcement/check-completeness-before-close.sh <issue>',
    'scripts/enforcement/check-marker-label-parity.sh':
        '.github/workflows/enforcement-gate.yml:241 — if scripts/enforcement/check-marker-label-parity.sh \\',
    'scripts/enforcement/check-model-id-sourcing.sh':
        '.github/workflows/enforcement-gate.yml:275 — scripts/enforcement/check-model-id-sourcing.sh 2>&1 | tee /tmp/model-id.log',
    'scripts/enforcement/compliance-dashboard.sh':
        '.github/workflows/enforcement-gate.yml:329 — COMPLIANCE_WINDOW_HOURS=168 scripts/enforcement/compliance-dashboard.sh 2>&1 | tee /tm',
    'scripts/enforcement/require-plan-approval.sh':
        '.github/workflows/enforcement-gate.yml:196 — if scripts/enforcement/require-plan-approval.sh --strict 2>&1; then',
    'scripts/generate-resource-index.sh':
        'scripts/generate-resource-index.sh:125 — | Resource index | `./scripts/generate-resource-index.sh` |',
    'scripts/gsd/cost-tracker.sh':
        'scripts/gsd/test-cost-tracker.sh:27 — [$TRACKER <- L6] "$TRACKER" append_event \\',
    'scripts/operations/compliance/audit_skill_symlink_policy.sh':
        'scripts/operations/compliance/check_governance.sh:44 — run_check "audit_skill_symlink_policy" "$SCRIPT_DIR/audit_skill_symlink_policy.sh" --m',
    'scripts/operations/compliance/audit_spec_location.sh':
        'scripts/operations/compliance/check_governance.sh:46 — run_check "audit_spec_location" "$SCRIPT_DIR/audit_spec_location.sh" --mode "$MODE" --',
    'scripts/operations/compliance/audit_wrk_location.sh':
        'scripts/operations/compliance/check_governance.sh:40 — run_check "audit_wrk_location" "$SCRIPT_DIR/audit_wrk_location.sh" --mode "$MODE" --sc',
    'scripts/operations/compliance/check_governance.sh':
        '.github/workflows/baseline-check.yml:120 — ./scripts/operations/compliance/check_governance.sh \\',
    'scripts/operations/compliance/install_compliance_hooks.sh':
        'scripts/operations/compliance/propagate_guidelines.sh:266 — ./scripts/operations/compliance/install_compliance_hooks.sh . > /dev/null 2>&1 || true',
    'scripts/operations/compliance/validate_work_queue_schema.sh':
        'scripts/operations/compliance/check_governance.sh:42 — run_check "validate_work_queue_schema" "$SCRIPT_DIR/validate_work_queue_schema.sh" --m',
    'scripts/operations/maintenance/daily_repo_maintenance.sh':
        'scripts/operations/maintenance/setup_maintenance_cron.sh:145 — "$SCRIPT_DIR/daily_repo_maintenance.sh" --verbose',
    'scripts/operations/monitoring/check_claude_usage.sh':
        'scripts/operations/monitoring/suggest_model.sh:167 — "$SCRIPT_DIR/check_claude_usage.sh" log "$FINAL_MODEL" "$REPO" "$TASK" "${tokens:-0}"',
    'scripts/operations/monitoring/suggest_model.sh':
        'scripts/operations/monitoring/MODEL_SELECTION_ENHANCED.md:485 — ./suggest_model.sh digitalmodel "test task"',
    'scripts/planning/synthesise.sh':
        'scripts/planning/ensemble-plan.sh:246 — "${SCRIPT_DIR}/synthesise.sh" "$RESULTS_DIR" "$WRK_FILE" || synthesis_exit=$?',
    'scripts/productivity/daily-reflect-report.sh':
        '.claude/commands/today.md:162 — ./scripts/productivity/daily-reflect-report.sh 2>/dev/null',
    'scripts/productivity/daily_today.sh':
        '.claude/commands/today.md:17 — ./scripts/productivity/daily_today.sh 2>/dev/null || echo "Script not found, gathering',
    'scripts/release/generate-changelog.sh':
        'scripts/release/cut-release.sh:60 — changelog_entry=$("$WORKSPACE_ROOT/scripts/release/generate-changelog.sh" "$repo_path"',
    'scripts/review/submit-to-claude.sh':
        'scripts/review/cross-review.sh:286 — "${SCRIPT_DIR}/submit-to-claude.sh" --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$resu',
    'scripts/review/submit-to-codex.sh':
        'scripts/review/cross-review.sh:343 — "${SCRIPT_DIR}/submit-to-codex.sh" --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$resul',
    'scripts/tests/check_repo_mission_portfolio.sh':
        'docs/REPO_MISSION_PORTFOLIO.md:9 — scripts/tests/check_repo_mission_portfolio.sh --generate',
    'scripts/utilities/doc-to-context/doc2context.sh':
        'scripts/utilities/doc-to-context/examples/example_usage.sh:8 — ../doc2context.sh sample.pdf',
}


def _committed_mode(path: str) -> str:
    """Mode as COMMITTED at HEAD. See module docstring for why not `ls-files -s`."""
    out = subprocess.run(
        ["git", "ls-tree", "HEAD", "--", path],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert out, f"{path} is not tracked by git at HEAD"
    return out.split()[0]


@pytest.mark.parametrize("script", sorted(PATH_INVOKED_SCRIPTS))
def test_path_invoked_script_is_executable(script):
    assert (REPO_ROOT / script).exists(), f"missing script {script}"
    mode = _committed_mode(script)
    assert mode == "100755", (
        f"{script} is tracked {mode}; must be 100755 — it is invoked BY PATH at "
        f"{PATH_INVOKED_SCRIPTS[script]}, so a non-executable bit makes that "
        f"invocation fail with `Permission denied` on any fresh clone."
    )


def test_sourced_library_is_not_marked_executable():
    """The inverse guard: a `source`-only helper must NOT be made executable.

    Pins the discriminator itself. ssh-helpers.sh documents `source`-ing in its
    own header; marking it 100755 would misrepresent how it is used, and would be
    the signature failure of a blanket `chmod +x` sweep.
    """
    sourced_only = "scripts/operations/system/ssh-helpers.sh"
    assert sourced_only not in PATH_INVOKED_SCRIPTS, (
        f"{sourced_only} is sourced, not path-invoked — it must never be listed here"
    )
    assert _committed_mode(sourced_only) == "100644", (
        f"{sourced_only} is sourced (`source .../ssh-helpers.sh`), so it must stay "
        f"tracked 100644; an executable bit here is a silent lie about its usage"
    )
