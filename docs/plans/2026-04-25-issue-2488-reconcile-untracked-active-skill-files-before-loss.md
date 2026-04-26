# Plan for #2488: reconcile untracked active skill files before loss

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2488
> **Review artifacts:** scripts/review/results/20260425T125029Z-plan-2488-claude.md | scripts/review/results/20260425T125029Z-plan-2488-codex.md | scripts/review/results/20260425T125029Z-plan-2488-gemini.md | scripts/review/results/20260425T125029Z-plan-2488-disagreement.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/weekly_skills_audit.py` — deterministic weekly skill audit entrypoint already exists from #2281/#2486. It scans `.claude/skills`, excludes `_archive` and `_diverged`, classifies duplicate canonical names / leaf collisions / wrapper pairs, applies baseline and waiver logic, and emits JSON + Markdown artifacts. Gap: it does not currently model tracked-vs-filesystem inventory or filesystem-only active skills as a first-class high-signal finding.
- Found: `scripts/cron/skills-curation.sh` — existing cron wrapper runs `uv run --no-project python scripts/skills/weekly_skills_audit.py` and supports `SKILLS_AUDIT_OUTPUT_ROOT` for redirectable test output. #2488 must preserve this local-only deterministic wrapper and avoid adding network posting.
- Found: `tests/skills/test_weekly_skills_audit.py` — existing pytest coverage for inventory scope, classification buckets, output schema, baseline delta, waiver handling, read-only behavior, and `TestScheduleIntegration.test_validate_schedule_still_passes_with_skills_curation_task` for `config/scheduled-tasks/schedule-tasks.yaml`. Gap: no coverage currently asserts that active filesystem-only `SKILL.md` files are detected/reported distinctly from tracked active skills.
- Found: `tests/cron/test_skills_curation.py` — existing wrapper regression coverage for `--dry-run`, `--help`, `SKILLS_AUDIT_OUTPUT_ROOT` forwarding, and stale `WORKSPACE_HUB` handling; #2488 must preserve these invariants while keeping manual reconcile outside the cron path.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — authoritative scheduled-task source includes `id: skills-curation`, Monday 04:00 schedule, wrapper command, and description currently saying duplicate/leaf/wrapper audit and “Read-only in v1. Issue #2281.” #2488 should update the YAML description only if the recurring task contract text changes; the command remains the wrapper.
- Found: current live inventory re-check on 2026-04-25 from repo root: tracked total `3028`, tracked active `922` when excluding `_archive` and `_archived`, filesystem total `3100`, filesystem active `928`, untracked/filesystem-only total `72`, untracked/filesystem-only active `6`, missing tracked active from filesystem `0`. This matches the issue-body conclusion: no tracked active skills are missing, but six active filesystem-only skills are at loss risk. Note: excluding only `_archive` and `_diverged` yields tracked active `928`; adding `_archived` excludes the six tracked `email/_archived` skills and yields the stricter active baseline `922`: `.claude/skills/email/_archived/gmail-data-extraction/SKILL.md`, `.claude/skills/email/_archived/gmail-email-to-repo-extraction/SKILL.md`, `.claude/skills/email/_archived/gmail-extract-and-clean/SKILL.md`, `.claude/skills/email/_archived/gmail-extract-archive/SKILL.md`, `.claude/skills/email/_archived/gmail-touchbase/SKILL.md`, `.claude/skills/email/_archived/gmail-unsubscribe/SKILL.md`.
- Found: mirror state remains canonical and must be preserved: `.codex/skills -> ../.claude/skills`; `.gemini/skills -> ../.claude/skills`. #2488 must not duplicate provider skill trees.

### Standards
| Standard | Status | Source |
|---|---|---|
| Mandatory issue planning gate | required | `AGENTS.md`, `docs/plans/README.md`, `docs/plans/_template-issue-plan.md` |
| TDD before implementation | required | `AGENTS.md` |
| Weekly skills audit policy | active / relevant | `config/skills/weekly-audit-policy.yaml`, `docs/standards/weekly-skills-audit-policy.md` |
| Document intelligence entry point | checked / low direct relevance | `docs/document-intelligence/README.md` — navigation/provenance context; no additional skill-curation constraints found. |
| Existing scheduled-task contract | active / relevant | `config/scheduled-tasks/schedule-tasks.yaml`, `scripts/cron/skills-curation.sh`, `tests/cron/test_skills_curation.py`, `docs/ops/scheduled-tasks.md` |

### LLM Wiki pages consulted
- No relevant domain wiki pages apply. This is repo-maintenance / control-plane skill hygiene work, not offshore engineering knowledge content.

### Documents consulted
- Issue #2488 — defines the exact loss-risk problem, six active filesystem-only skills, scope exclusions, and acceptance criteria.
- Issue #2486 — completed v2 periodic skill ecosystem housekeeping audit; established the active/archive/symlink count model and should not be reopened by #2488.
- `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md` — prior deterministic weekly audit plan; #2488 should extend that surface rather than invent a second audit runner.
- `docs/plans/README.md` — plan index and mandatory approval workflow; this plan must be indexed and moved only to `status:plan-review`, not self-approved.
- `docs/ops/scheduled-tasks.md` — operator-facing scheduled-task table already lists Monday 04:00 `skills-curation`; #2488 should update docs only if output semantics materially change.

### Gaps identified
- No first-class audit field/report currently distinguishes tracked skill files, filesystem skill files, active filesystem-only skill files, archived filesystem-only skill files, mirror/symlink state, and missing tracked active files in one canonical inventory summary.
- No regression test currently fixtures a skill tree plus a simulated tracked-file manifest to prove active filesystem-only `SKILL.md` files are surfaced as high-signal maintenance findings.
- The six currently known active filesystem-only skills have not been individually dispositioned as `promote/commit`, `archive`, `ignore/generated/transient`, or `delete`. Implementation must disposition every active filesystem-only skill discovered at runtime, not just these six if live state drifts.
- No durable disposition ledger/report exists for the current 72 filesystem-only `SKILL.md` files. #2488 prioritizes active loss-risk files; archived-only filesystem-only files should be reported informationally and explicitly accepted as non-active loss risk unless separately promoted by follow-up.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-25 via `gh issue view`):
- `#2488` — OPEN — `chore(skills): reconcile untracked active skill files before loss`
- `#2486` — CLOSED / COMPLETED — `chore(skills): v2 periodic skill ecosystem housekeeping audit`

**File existence and excerpts** (verified 2026-04-25):
- EXISTS: `scripts/skills/weekly_skills_audit.py` — deterministic audit script; current top-level constants include `EXCLUDED_DIRS = {"_archive", "_diverged"}` and do not include `_archived` in the v1 duplicate/collision exclusion set.
- EXISTS: `scripts/cron/skills-curation.sh` — lines 41-47 build the command array and append `--output-dir` when `SKILLS_AUDIT_OUTPUT_ROOT` is set; lines 51-58 print that command and exit in dry-run mode.
- EXISTS: `tests/skills/test_weekly_skills_audit.py` — tests cover inventory/classification/output but not tracked-vs-filesystem loss-risk reporting.
- EXISTS: `tests/cron/test_skills_curation.py` — wrapper tests cover dry-run/help/output-root/stale-workspace behavior; add coverage here if CLI or wrapper expectations are touched.
- EXISTS: `config/skills/weekly-audit-policy.yaml` — authoritative schema uses `signal_vocabulary`, `classification_buckets`, `precedence_order`, and `v2.rules`; #2488 must extend the existing schema append-only rather than inventing a separate top-level `signals` map.
- EXISTS: `config/scheduled-tasks/schedule-tasks.yaml` — authoritative `skills-curation` task uses `bash scripts/cron/skills-curation.sh`; command remains unchanged.

**Live inventory proof** (command embedded per the plan evidence contract, 2026-04-25):
```bash
uv run --no-project python - <<'PY'
from pathlib import Path
import subprocess
root = Path('.').resolve()
skills = root / '.claude/skills'
tracked = [p for p in subprocess.check_output(['git','ls-files','.claude/skills'], text=True).splitlines() if p.endswith('/SKILL.md')]
fs = [str(p.relative_to(root)) for p in skills.rglob('SKILL.md')]
from pathlib import PurePosixPath
def active(p):
    parts = PurePosixPath(p).parts
    return not any(x in parts for x in ('_archive','_archived'))
print('tracked_total', len(tracked))
print('tracked_active_excluding_archive_archived', sum(active(p) for p in tracked))
print('filesystem_total', len(fs))
print('filesystem_active_excluding_archive_archived', sum(active(p) for p in fs))
print('filesystem_only_total', len(set(fs) - set(tracked)))
print('filesystem_only_active_excluding_archive_archived', sum(active(p) for p in set(fs) - set(tracked)))
print('missing_tracked_active_from_filesystem', sum(active(p) and p not in set(fs) for p in tracked))
for p in sorted(set(fs) - set(tracked)):
    if active(p):
        print('UNTRACKED_ACTIVE', p)
print('codex_link', Path('.codex/skills').readlink() if Path('.codex/skills').is_symlink() else 'not-symlink')
print('gemini_link', Path('.gemini/skills').readlink() if Path('.gemini/skills').is_symlink() else 'not-symlink')
PY
```
Output:
```text
tracked_total 3028
tracked_active_excluding_archive_archived 922
filesystem_total 3100
filesystem_active_excluding_archive_archived 928
filesystem_only_total 72
filesystem_only_active_excluding_archive_archived 6
missing_tracked_active_from_filesystem 0
UNTRACKED_ACTIVE .claude/skills/business_admin/personal-tax-filing-packet/SKILL.md
UNTRACKED_ACTIVE .claude/skills/digitalmodel/blender-worktree-test-hardening/SKILL.md
UNTRACKED_ACTIVE .claude/skills/digitalmodel/digitalmodel-worktree-test-execution-with-shared-venv/SKILL.md
UNTRACKED_ACTIVE .claude/skills/digitalmodel/library-evaluation-integration/SKILL.md
UNTRACKED_ACTIVE .claude/skills/digitalmodel/orcaflex-reporting-fixture-proof-pattern/SKILL.md
UNTRACKED_ACTIVE .claude/skills/memory/hermes-memory-bridge/SKILL.md
codex_link ../.claude/skills
gemini_link ../.claude/skills
```
Note: the 2026-04-25 proof uses the #2488 active filter (`_archive`, `_archived`). A parity spot-check found zero current `_diverged` filesystem-only active SKILL.md paths, so earlier strict-triple counts happened to match but are not the implementation rule.

<!-- Verification: distinct sources >= 3. Current count: 8 -->

### Tentative disposition table for the known active filesystem-only skills

These are plan-review dispositions for the six currently known active filesystem-only skills. Implementation must recompute the live list and apply the same decision rules to every active filesystem-only skill found at that time.

| Path | Tentative disposition | Rationale |
|---|---|---|
| `.claude/skills/business_admin/personal-tax-filing-packet/SKILL.md` | `pending_full_file_scan_and_user_authorization` | Local personal/tax workflow evidence only; ignored by `.gitignore:270 personal-*`; do not promote unless full-file scan is clean/redacted and user explicitly authorizes tracking a formerly ignored skill in this public-by-default repo. |
| `.claude/skills/digitalmodel/blender-worktree-test-hardening/SKILL.md` | `pending_full_scan` | Captures a recurring digitalmodel worktree/Blender test-hardening failure mode; promote/consolidate/archive/delete only after live scan and ignored-path evidence (`.gitignore:14 digitalmodel/`). |
| `.claude/skills/digitalmodel/digitalmodel-worktree-test-execution-with-shared-venv/SKILL.md` | `pending_full_scan` | Valuable shared-venv workaround candidate; may overlap with Blender-specific skill, so implementation decides promote-separate vs consolidate with rationale and ignored-path evidence (`.gitignore:14 digitalmodel/`). |
| `.claude/skills/digitalmodel/library-evaluation-integration/SKILL.md` | `pending_full_scan` | Reusable scientific-library evaluation candidate; promote/consolidate/archive/delete only after live scan and ignored-path evidence (`.gitignore:14 digitalmodel/`). |
| `.claude/skills/digitalmodel/orcaflex-reporting-fixture-proof-pattern/SKILL.md` | `pending_full_scan` | Reusable OrcaFlex reporting fixture/snapshot candidate; promote/consolidate/archive/delete only after live scan and ignored-path evidence (`.gitignore:14 digitalmodel/`). |
| `.claude/skills/memory/hermes-memory-bridge/SKILL.md` | `pending_full_scan` | Durable memory-bridge candidate; ignored by `.gitignore:291 memory/`; promote/redact/archive/delete only after live scan, accuracy check, and ignored-path evidence. |

Archived-only filesystem-only `SKILL.md` files are not silent: the audit should count them and list them as informational, but #2488 does not require per-file promotion/archive/delete decisions for archived-only local artifacts unless an archived-only file is intentionally promoted by follow-up.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-25-issue-2488-reconcile-untracked-active-skill-files-before-loss.md` |
| Existing audit script | `scripts/skills/weekly_skills_audit.py` |
| Existing cron wrapper | `scripts/cron/skills-curation.sh` |
| Existing audit tests | `tests/skills/test_weekly_skills_audit.py` |
| Policy contract | `config/skills/weekly-audit-policy.yaml` |
| Operator docs, if output contract changes | `docs/ops/scheduled-tasks.md` |
| Machine-readable disposition ledger | `config/skills/filesystem-only-skill-dispositions.yaml` |
| Durable disposition report | `docs/reports/2026-04-25-skills-disposition-2488.md` |
| Mutable fanout output — Claude (diagnostic only; not approval evidence) | `scripts/review/results/2026-04-25-plan-2488-claude.md` |
| Mutable fanout output — Codex (diagnostic only; not approval evidence) | `scripts/review/results/2026-04-25-plan-2488-codex.md` |
| Mutable fanout output — Gemini (not approval evidence if empty/overwritten) | `scripts/review/results/2026-04-25-plan-2488-gemini.md` |
| Mutable fanout output — disagreement/synthesis (diagnostic only; provider artifacts are authoritative on conflict) | `scripts/review/results/2026-04-25-plan-2488-disagreement.md` |
| Immutable review evidence — Claude | `scripts/review/results/20260425T125029Z-plan-2488-claude.md` |
| Immutable review evidence — Codex | `scripts/review/results/20260425T125029Z-plan-2488-codex.md` |
| Immutable review evidence — Gemini unavailable placeholder | `scripts/review/results/20260425T125029Z-plan-2488-gemini.md` |
| Immutable review evidence — disagreement | `scripts/review/results/20260425T125029Z-plan-2488-disagreement.md` |

---

## Deliverable

A deterministic extension to the weekly skills housekeeping workflow that surfaces active filesystem-only skills as loss-risk findings, plus a one-time disposition of every active filesystem-only skill discovered at implementation time so valuable skills are preserved and junk/transient artifacts are explicitly classified.

---

## Pseudocode

```text
function build_skill_inventory_with_git(skills_dir, repo_root, tracked_paths=None, git_list_fn=None, symlink_resolver=None):
    if tracked_paths is provided, use it (test seam for tmp_path fixtures); symlink_resolver(path: Path) -> {is_symlink: bool, target: str|null, error: str|null} and never raises
    else call git_list_fn or default git ls-files for repo-relative skills_dir ending /SKILL.md; never hard-code .claude/skills when --skills-dir points elsewhere
    filesystem_skill_paths = all SKILL.md under skills_dir using a non-pruning walk; do not reuse the existing duplicate/collision `build_inventory` walk for inventory totals because it prunes `_archive` and `_diverged` while not pruning `_archived`, so neither the legacy walk nor the strict #2488 active filter alone is sufficient
    active_filter(path): use `PurePosixPath(path).parts`/`Path.parts` exact segment equality; exact path segments `_archive` and `_archived` are non-active for #2488 loss-risk counts, matching the issue definition. `_diverged` is excluded from active-loss findings to preserve the existing quarantine semantic, but is reported separately as legacy compatibility metrics so the difference between #2488 issue-body counts and legacy audit counts is visible and create/follow a separate policy-drift follow-up if that convention should change.
    _core and _internal remain in-scope for filesystem-only loss-risk reporting; do not reuse INFORMATIONAL_DIRS to suppress them
    audit_inventory_filter(path): keep existing EXCLUDED_DIRS behavior for duplicate/collision pipeline; do not add _archived to EXCLUDED_DIRS unless a separate review approves changing legacy audit semantics
    return counts and path sets:
        tracked_total, tracked_active
        filesystem_total, filesystem_active
        filesystem_only_total, filesystem_only_active
        missing_tracked_total, missing_tracked_active
        filesystem_only_archived_total
        legacy_diverged_compatibility_total = count of de-duplicated union of tracked and filesystem SKILL.md paths containing an exact `_diverged` path segment; these paths are excluded from #2488 active-loss findings but visible as compatibility/quarantine inventory
        codex_skills_link, gemini_skills_link
    JSON schema:
        inventory_summary.counts = {tracked_total, tracked_active, filesystem_total, filesystem_active, filesystem_only_total, filesystem_only_active, missing_tracked_total, missing_tracked_active, filesystem_only_archived_total, legacy_diverged_compatibility_total}
        inventory_summary.paths = {filesystem_only_active: [{path, informational_namespace, ledger_status}], missing_tracked_active: [{path, informational_namespace, ledger_status}], filesystem_only_archived: [{path, informational_namespace, ledger_status}], issue_body_six_drift: [{path, drift_status, reason}]}; every path object in the first three arrays must include `path`, `informational_namespace`, and `ledger_status` (`ledger_status: null` when no ledger entry exists); `issue_body_six_drift` objects must include `path`, `drift_status`, and `reason`; allowed drift_status values are `present_active`, `present_tracked`, `archived_or_non_active`, and `vanished_before_reconcile`
        inventory_summary.mirrors = {codex_skills_link, gemini_skills_link}

function classify_filesystem_only_skill(path):
    read full file for scan-sensitive skills; read frontmatter and first content section for initial routing
    inspect current file content and frontmatter first
    inspect git history using deterministic fallback keys (frontmatter name and leaf slug), because a filesystem-only path itself may have no git history; git-history lookup failures are non-fatal warnings in weekly_report evidence, but trusted full git/filesystem inventory is mandatory for manual reconcile
    search canonical active skills for same frontmatter name, same leaf slug, or documented replacement
    assign disposition:
        promote_commit if valuable, unique, reusable, clean after scan, and either not ignored or approved for targeted `git add -f` with the matching ignore rule recorded
        consolidate_then_commit if valuable but overlapping with an existing skill; final_path points to the consolidated tracked skill
        redact_then_commit if valuable but full-file scan finds redactable PII/secrets/local-only details; require targeted `git add -f` evidence if final path remains ignored
        archive_intentionally if useful reference but not active routing material
        ignore_generated_transient if tool-generated or machine-local with policy rationale
        delete_if_junk only when provably useless and safe; closeout must remove the file and record terminal status
    require a reason, structured scan attestation when applicable, and terminal-state rule for every disposition

function run_weekly_audit_extension():
    run existing weekly audit duplicate/collision logic with unchanged EXCLUDED_DIRS semantics
    compute separate inventory_summary using the active loss-risk filter
    load config/skills/filesystem-only-skill-dispositions.yaml if present
    use existing v2 policy/ranking from config/skills/weekly-audit-policy.yaml for filesystem_only_active by extending the existing policy loader, `_finding_defaults()`, `_baseline_finding_sources()`, `_all_active_findings()`, `run_audit()` `summary_counts`, and `_write_markdown_artifact()` family rendering path instead of hard-coding a second policy surface. Pin the naming contract: family key `filesystem_inventory_findings` derived from policy family `filesystem-inventory`; finding_key/rule id `filesystem-inventory.filesystem-only-active` so `_finding_defaults()` can resolve it using the current family.rule_id convention; classification `filesystem-only-active`; finding objects must contain classification, finding_key, severity, confidence, paths, recommended_action, summary, headline, and ledger_status. Register `filesystem_inventory_findings` in `_baseline_finding_sources()` alongside current keys (`findings`, `suppressed_findings`, `content_quality_findings`, `grouping_findings`, `size_findings`, `usage_findings`); add it to `_all_active_findings()` and `active_all_findings`; add `filesystem_inventory_total: len(filesystem_inventory_findings)` to `summary_counts`; emit top-level JSON array `filesystem_inventory_findings`.
    append inventory_summary to JSON artifact
    append Markdown section "Filesystem-only skill files" listing every filesystem_only_active path regardless of ledger state; refactor `_write_markdown_artifact()` to consume `ranking_policy.section_order` for the exact six policy-governed sections after #2488 (`new_findings`, `changed_findings`, `filesystem_only_inventory`, `unresolved_high_confidence_findings`, `suppressed_carry_forward_findings`, `operational_errors_or_skipped_inputs`) instead of relying only on literal section calls for those sections; v2-family sections such as Content Quality, Grouping / Taxonomy Drift, Oversized / Maintainability, Usage / Staleness, and Follow-up Candidates remain literal legacy sections unless separately added to policy in future work; add `filesystem_only_inventory` immediately after `changed_findings` and immediately before `unresolved_high_confidence_findings`, and update docs/standards/weekly-skills-audit-policy.md to document the sixth policy entry (not necessarily the sixth visible Markdown H2); ledger can annotate `unresolved|reviewed|resolved_ignored|resolved_promoted|resolved_archived|resolved_deleted`, but does not remove active filesystem-only paths from the inventory list while they remain on disk
    mark unresolved filesystem_only_active_count > 0 as high-signal maintenance finding
    unresolved findings are reportable, not a weekly-cron hard failure
    preserve local-only/no-network behavior and write recurring outputs only under the configured output_dir/logs/maintenance/skills-curation/ tree

manual CLI contract for scripts/skills/reconcile_filesystem_only_skills.py:
    argparse flags: --skills-dir PATH (default .claude/skills), --ledger PATH (default config/skills/filesystem-only-skill-dispositions.yaml), --disposition-report PATH (required for tracked Markdown report), --trust-attestation PATH (default docs/reports/2026-04-25-skills-disposition-2488-trust-attestation.json), --policy PATH (default config/skills/weekly-audit-policy.yaml), --base-ref REF and --head-ref REF (baseline-order range, default merge-base of origin/main and HEAD through HEAD), `--strict/--no-strict` using `argparse.BooleanOptionalAction` with strict default true, --inventory-json PATH optional for replay/testing only and rejected for real manual closeout unless paired with --trust-attestation containing a matching live trust attestation generated during the same run; `--no-strict` may downgrade only advisory documentation/report-formatting warnings and missing optional notes, never git trust checks, inventory truncation checks, terminal disposition validity, ignored-path attestation, personal/redaction authorization, baseline-order verification, or unresolved active filesystem-only files
    exit codes: 0 when missing_tracked_active=0 and unresolved_filesystem_only_active=0 after applying ledger; 2 for ledger validation/terminal-state failures after successful argument parsing; 3 for untrusted git/filesystem inventory; 4 for CLI usage errors (missing required flags, invalid enum values, malformed YAML/JSON that cannot be parsed as a ledger). Implement with an explicit `ArgumentParser` subclass or equivalent parser wrapper so argparse usage errors return 4 instead of argparse default 2
    inventory trust checks: fail hard when `git rev-parse --is-inside-work-tree` fails, `git config --bool core.sparseCheckout` is true, `git ls-files -z -- <resolved skills_dir relative to repo_root>` exits nonzero, or git adapter reports a partial/truncated result; mocked adapter failures are allowed in tests but must correspond to these real signals; all trust checks use the resolved `--skills-dir` relative to `repo_root`, and `.claude/skills` appears only as the default value, never as a hard-coded validation path

function validate_and_render_dispositions_for_manual_reconcile(disposition_yaml):
    separate manual entrypoint, not the cron-owned weekly audit CLI; weekly_skills_audit.py remains read-only and local-output-only
    require trusted full git/filesystem inventory; git errors, sparse checkout, or partial inventory are hard failures in manual reconcile but warning-only in weekly_report; write trust_attestation JSON at the configured path with schema {repo_root, skills_dir, git_head, base_ref, head_ref, generated_at, sparse_checkout, git_ls_files_count, filesystem_walk_count, git_ls_files_sha256, filesystem_walk_sha256, partial_inventory, inventory_json_sha256_when_replayed}
    require one entry per active filesystem-only skill discovered at implementation time; fail on missing/invalid entries; render docs/reports/2026-04-25-skills-disposition-2488.md
    require fields: path, disposition, reason, reviewed_at (UTC ISO-8601), reviewer, file_hashes, final_status, final_path, scan_attestation, force_add_attestation_when_ignored, user_authorization_when_personal, and issue_body_drift_note when a known issue-body path is absent before reconcile
    define file_hashes per disposition: promote_commit = {reviewed_file_sha256} of final on-disk SKILL.md that must match tracked final_path; redact_then_commit = {pre_redaction_sha256, final_file_sha256} after redaction, with final_file_sha256 matching tracked final_path; consolidate_then_commit = {original_file_sha256, final_consolidated_sha256} at final_path; archive_intentionally/delete_if_junk = {original_file_sha256} plus final_status/final_path or deletion status; ignore_generated_transient = {reviewed_file_sha256} current on-disk sha256 that must match while status remains resolved_ignored. issue_body_drift_note lives on the ledger entry for the missing issue-body path and has schema {path, last_seen_evidence, vanished_at_reconcile_at, reviewer, rationale}
    allowed dispositions: promote_commit, consolidate_then_commit, redact_then_commit, archive_intentionally, ignore_generated_transient, delete_if_junk
    scan_attestation schema: {tool_or_method, scope: full_file|frontmatter|content_overlap, scanned_at, finding_count, finding_summary, reviewer}; force_add_attestation schema when ignored: {gitignore_rule, gitignore_line, git_add_force_required, git_add_force_invoked_at (UTC ISO-8601), final_git_ls_files_contains_path}
    terminal-state rules:
        promote_commit/redact_then_commit: resolved when final_path exists in tracked active skills and disposition records whether the final path required `git add -f`; consolidate_then_commit: resolved when final_path exists in tracked active skills AND original path is absent from active filesystem-only inventory
        archive_intentionally: resolved only when original path is absent from active filesystem-only set and final_path is under an archive segment or tracked archive path
        delete_if_junk: resolved only when original path is absent and final_status is deleted_with_reason
        ignore_generated_transient: resolved_ignored only when a matching durable policy/ignore rationale exists in the ledger/YAML policy; while the file remains active filesystem-only on disk, weekly reports must still list it in inventory_summary.paths.filesystem_only_active with resolved_ignored status
    future weekly audit runs may read the YAML ledger to annotate reviewed/resolved state, but remain read-only; file_hashes.reviewed_file_sha256 matching on non-terminal unchanged filesystem-only entries marks them reviewed but still visible in local filesystem-only inventory; terminal entries govern unresolved loss-risk status, but active filesystem-only files that remain on disk are always listed in the recurring inventory section

implementation_flow():
    RED-FIRST HARD GATE: before editing `scripts/skills/weekly_skills_audit.py` or policy logic, capture `tests/fixtures/skills/issue-2488-archived-duplicate-baseline.json` from current pre-change audit behavior and commit/include it in a strict predecessor commit that touches only the fixture and supporting test/scaffold before any commit that edits `scripts/skills/weekly_skills_audit.py` or `config/skills/weekly-audit-policy.yaml`; have `scripts/skills/reconcile_filesystem_only_skills.py` invoke `scripts/skills/verify_issue_2488_baseline_order.py --base-ref <base> --head-ref <head>` in strict mode before writing the disposition report; also include the helper output in the final adversarial implementation review prompt. This is a closeout-script hard failure (not a global pre-push hook), so closeout exits nonzero if the fixture commit is absent, in the same commit as, or after the first audit/policy logic change
    RED: add tests for inventory_summary and filesystem_only_active reporting
    GREEN: implement minimal tracked-vs-filesystem inventory helper and output section
    RED/GREEN: add fixture tests for symlink mirror reporting and _archived exclusion
    RED/GREEN: add separate manual reconcile script for disposition ledger validation/report generation for every active filesystem-only skill discovered at implementation time
    verify no unrelated local dirt is staged
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/skills/weekly_skills_audit.py` | Add tracked-vs-filesystem inventory summary, filesystem-only active skill reporting, optional read-only ledger annotation, and mirror/symlink status reporting. Keep legacy duplicate/collision `EXCLUDED_DIRS` behavior unchanged; use a separate active loss-risk filter. Do not add tracked-doc write behavior to this cron-owned script. |
| Modify | `tests/skills/test_weekly_skills_audit.py` | Add TDD coverage for tracked-vs-filesystem inventory via injectable tracked manifest/git adapter seam, active filesystem-only findings, missing tracked active files, active loss-risk filtering, optional read-only ledger annotation, symlink status serialization, and the existing `TestScheduleIntegration.test_validate_schedule_still_passes_with_skills_curation_task` guard if scheduled YAML description changes. |
| Create | `scripts/skills/reconcile_filesystem_only_skills.py` | Separate manual reconcile entrypoint that validates disposition ledger, hard-fails on untrusted/partial inventory, and renders the tracked disposition report. This keeps the weekly cron entrypoint read-only. |
| Create | `tests/skills/test_reconcile_filesystem_only_skills.py` | TDD coverage for manual reconcile strictness, terminal-state rules, force-add evidence, personal-skill authorization, and tracked report rendering. |
| Modify | `tests/cron/test_skills_curation.py` | Add/adjust wrapper dry-run coverage proving the existing cron command remains compatible and does not invoke manual reconcile behavior. |
| Modify | `config/skills/weekly-audit-policy.yaml` | Append `filesystem_only_active` / `filesystem-only-active` to the existing v2 schema: `v2.rules.filesystem-inventory.filesystem-only-active` (family.rule_id form consumed by `_finding_defaults()`), and `weekly_summary_sections` + `ranking_policy.section_order` entry `filesystem_only_inventory` placed immediately after `changed_findings` and immediately before `unresolved_high_confidence_findings`. Do not create an undocumented top-level `signals` map. Implementation must route this family through the existing policy loader and active-finding/Markdown rendering path so severity/reporting are policy-driven rather than bespoke constants. Manual reconcile schema lives with the separate reconcile script/ledger docs, not the cron policy. |
| Create | `config/skills/filesystem-only-skill-dispositions.yaml` | Machine-readable disposition ledger for active filesystem-only skills; gives future audit runs a durable resolved/ignored/consolidated source of truth without overloading duplicate-skill buckets. |
| Modify | `docs/standards/weekly-skills-audit-policy.md` | Document new inventory summary schema and where `filesystem_only_active` lives in the existing policy schema. |
| Modify | `docs/ops/scheduled-tasks.md` | Document that recurring `skills-curation` remains local-only/read-only and reference the separate manual reconcile command as an operator action, not a cron path. |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Update only the `skills-curation` description to exact v2 wording while preserving schedule, command, machines, and log path: “Weekly skills curation v2: duplicate names, leaf collisions, wrapper pairs, and filesystem-only active skill loss-risk inventory. Local-only/report-only; no network posting. Issue #2488.” |
| Create | `docs/reports/2026-04-25-skills-disposition-2488.md` | Durable, tracked disposition report for every active filesystem-only skill discovered at implementation-time. Date is intentionally bound to the plan artifact date for #2488 traceability, not the implementation date. Use this tracked docs path because `.gitignore` ignores `logs/*`, including `logs/maintenance/...`. |
| Create | `docs/reports/2026-04-25-skills-disposition-2488-trust-attestation.json` | Machine-readable manual-closeout trust proof written by `reconcile_filesystem_only_skills.py`; records repo/head/range, sparse-checkout state, git/filesystem inventory counts, and SHA256s so `--inventory-json` replay cannot bypass live trust checks. |
| Create | `tests/fixtures/skills/issue-2488-archived-duplicate-baseline.json` | Frozen pre-change `_archived` duplicate/collision baseline used by regression tests to assert duplicate/collision `{finding_key, severity, paths}` tuple set plus summary counts are unchanged rather than absolute no-findings. Must be produced before audit-logic edits. |
| Create | `scripts/skills/verify_issue_2488_baseline_order.sh` | Manual review-package helper (kept under `scripts/skills/`, not `scripts/enforcement/`, because it is not hook/CI-bound) invoked during implementation closeout and final implementation review prep; calls `scripts/skills/verify_issue_2488_baseline_order.py` over the implementation branch/range and reports nonzero if the fixture is absent, in the same commit as the first audit/policy logic change, or newer than the first audit/policy logic change. The manual reconcile script invokes this in strict mode, making it a closeout-script gate without adding a global hook/CI job. |
| Create | `scripts/skills/verify_issue_2488_baseline_order.py` | Helper used by `scripts/skills/verify_issue_2488_baseline_order.sh`: accept `--base-ref` and `--head-ref` (defaulting to merge-base of origin/main and HEAD, then HEAD), compare the fixture-add commit for `tests/fixtures/skills/issue-2488-archived-duplicate-baseline.json` against the first changed commit touching `scripts/skills/weekly_skills_audit.py` or `config/skills/weekly-audit-policy.yaml` in that branch/range; require a strict predecessor commit using graph reachability: `git merge-base --is-ancestor <fixture_sha> <first_logic_sha>` and `<fixture_sha> != <first_logic_sha>`; do not use commit timestamps as authoritative ordering. |
| Add when disposition requires tracking | active filesystem-only `SKILL.md` paths discovered at implementation time | Promote only those classified as valuable active skills; do not mass-add all 72 filesystem-only files. If a promoted path is ignored by `.gitignore`, use explicit `git add -f <path>` only after ledger scan/disposition evidence is recorded; do not broadly relax `.gitignore` for `digitalmodel/`, `personal-*`, or `memory/`. |
| Document-only by default | `.gitignore` | Do not change by default; record the current ignore rule for any promoted path in the disposition ledger and use targeted `git add -f` for approved promotions. For the known parent-directory ignore rules, single-line negations are ineffective; modify `.gitignore` only in a separately reviewed follow-up if a full multi-line re-include cascade is justified. |
| Planning lifecycle only | `docs/plans/README.md` | Add/update the #2488 row during plan-gate work; do not treat this as an implementation file. Status should be `plan-review` when the approval gate is posted. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_inventory_summary_distinguishes_tracked_and_filesystem_skills` | canonical counts are explicit and testable without a real git repo | fixture skills + injected tracked manifest/git adapter | JSON summary includes tracked/filesystem totals and active counts |
| `test_inventory_summary_schema_separates_counts_paths_and_mirrors` | JSON shape is deterministic | fixture with filesystem-only and missing-tracked paths | `inventory_summary.counts` has numbers, `inventory_summary.paths` arrays use stable object keys including `ledger_status` (or drift fields for issue-body drift), `inventory_summary.mirrors` has symlink targets |
| `test_inventory_summary_reports_filesystem_only_active_skills` | loss-risk skills are visible | fixture active `SKILL.md` absent from tracked manifest | `filesystem_only_active` contains path and count > 0 |
| `test_inventory_summary_reports_missing_tracked_active_skills` | actual tracked skill loss would be detected | tracked manifest contains absent active path | `missing_tracked_active` contains path and count > 0 |
| `test_inventory_summary_excludes_archive_archived_and_reports_diverged_compatibility_count` | active filter matches #2488 loss-risk semantics and preserves segment-name pruning | fixture `_archive`, `_archived`, a nonzero `_diverged` SKILL.md plus matching tracked path, normal paths, plus `_core`/`_internal` paths | `_archive`/`_archived` are excluded from #2488 loss-risk counts; `_diverged` is excluded from active-loss findings and reported in a separate legacy-compatibility count; `_core`/`_internal` filesystem-only skills still count as active loss-risk; substring-only names do not over-match |
| `test_inventory_summary_records_provider_skill_mirror_symlinks` | mirror status remains explicit | resolver-injection seam supplies `.codex/skills` and `.gemini/skills` link targets | JSON records links to `../.claude/skills` without platform-dependent symlink setup |
| `test_weekly_markdown_surfaces_filesystem_only_active_skills` | operator report is high-signal | audit result with active filesystem-only path | Markdown includes `Filesystem-only skill files` section and path |
| `test_filesystem_only_archived_skills_do_not_escalate_active_loss_risk` | archived local files do not create false active alarms | untracked `_archive` and `_archived` SKILL.md files | active loss-risk count remains 0; archived count is reported separately |
| `test_filesystem_only_core_and_internal_skills_are_not_suppressed` | control-plane/internal namespaces are still protected against untracked loss | untracked `_core` and `_internal` SKILL.md files | active filesystem-only count includes these paths and each path object carries `informational_namespace: true` |
| `test_disposition_ledger_accepts_only_known_disposition_values` | dispositions are machine-checkable | invalid disposition string | manual reconcile validation fails |
| `test_weekly_mode_reports_unresolved_without_hard_failure` | recurring cron remains report-only | active filesystem-only skill without ledger entry | weekly result records high-signal unresolved finding and exits successfully |
| `test_weekly_mode_lists_resolved_ignored_filesystem_only_skills` | ledger resolution does not hide active files that remain on disk | active filesystem-only skill with durable `ignore_generated_transient` ledger entry | weekly JSON/Markdown still lists the path with resolved_ignored status but unresolved count excludes it |
| `test_git_inventory_failure_is_reported_not_cron_fatal` | weekly cron remains deterministic on Git errors | git_list_fn raises or skills_dir is outside a repo | weekly result records inventory warning and exits successfully |
| `test_manual_reconcile_hard_fails_on_untrusted_or_partial_inventory` | reconcile proof is authoritative | git adapter errors, `core.sparseCheckout=true`, `git ls-files -- <resolved skills_dir>` nonzero/truncated result, or partial tracked manifest | manual reconcile script exits code 3 before writing tracked report |
| `test_manual_reconcile_strict_boolean_optional_action` | strict mode CLI is runnable | argparse for default, `--strict`, and `--no-strict` | default and `--strict` are strict; `--no-strict` parses and downgrades only documented non-authoritative checks |
| `test_manual_reconcile_non_default_skills_dir_uses_resolved_git_path` | no hard-coded `.claude/skills` trust checks | `--skills-dir custom/skills` with git adapter spy | trust check invokes `git ls-files -z -- custom/skills` and inventory uses that tree |
| `test_manual_reconcile_rejects_out_of_worktree_skills_dir` | escaped skills roots are untrusted | `--skills-dir` resolves outside repo_root via symlink or `..` path | manual reconcile exits code 3 before inventory/report output |
| `test_manual_reconcile_inventory_json_requires_trust_attestation` | replay does not bypass trust | `--inventory-json` without matching trust_attestation in closeout mode | manual reconcile exits code 3; replay is allowed only in tests or with recorded live trust attestation at `docs/reports/2026-04-25-skills-disposition-2488-trust-attestation.json` |
| `test_policy_yaml_defines_filesystem_only_active_signal` | YAML is authoritative | policy fixture following existing `weekly_summary_sections`, `ranking_policy.section_order`, and `v2.rules` shape without adding to legacy `signal_vocabulary` | weekly-audit parser, `_finding_defaults()` using `filesystem-inventory.filesystem-only-active`, `_baseline_finding_sources()`, `_all_active_findings()`, `run_audit()` summary counts, and `_write_markdown_artifact()` policy-order rendering expose the append-only `filesystem_only_active` signal/rule and `filesystem_only_inventory` section without requiring a new top-level `signals` map or hard-coded severity |
| `test_existing_weekly_audit_cli_flags_remain_backward_compatible` | wrapper invariance is protected | argparse invocation with existing flags only | command parses, remains read-only, and does not write tracked docs |
| `test_cron_wrapper_executes_weekly_audit_not_manual_reconcile` | wrapper command remains compatible and execution path is pinned | dry-run output plus exec-shim/mocked argv capture | printed and executed argv match `python scripts/skills/weekly_skills_audit.py [...]` and never reference manual reconcile script |
| `test_schedule_description_exact_v2_string` | scheduled task wording is deterministic | schedule-tasks fixture | `skills-curation` description equals the exact v2 string in this plan while schedule/command stay unchanged |
| `test_filesystem_only_family_participates_in_baseline_and_summary_counts` | family is not new every week and appears in totals | baseline plus current filesystem-only finding | `_baseline_finding_sources()`, carry-forward/is_new logic, and `run_audit()` summary_counts include `filesystem_inventory_findings` |
| `test_policy_section_order_reorders_all_policy_governed_sections` | policy-driven rendering is real | policy fixture reorders exactly the six policy-governed sections (`new_findings`, `changed_findings`, `filesystem_only_inventory`, `unresolved_high_confidence_findings`, `suppressed_carry_forward_findings`, `operational_errors_or_skipped_inputs`) | `_write_markdown_artifact()` renders those six sections in YAML order, while v2-family legacy sections remain literal until a future policy-extension issue |
| `test_sparse_checkout_or_partial_git_inventory_is_warned_not_trusted` | successful-but-partial git inventory does not create false loss findings | git adapter reports sparse checkout or unexpectedly low tracked count | weekly report emits inventory warning and does not assert missing-tracked loss without explicit confirmation |
| `test_manual_reconcile_requires_complete_terminal_dispositions` | closeout gate is strict | active filesystem-only skill missing ledger entry or terminal state | manual reconcile validation fails |
| `test_issue_body_vanished_path_requires_drift_note_schema` | six issue-body paths remain accountable if they vanish | one issue-body path absent at reconcile and ledger lacks issue_body_drift_note | validation fails until the structured drift note is present |
| `test_disposition_report_written_to_tracked_docs_path_with_stable_schema` | one-time closeout report is generated where Git can track it | valid disposition ledger | `docs/reports/2026-04-25-skills-disposition-2488.md` contains path/disposition/reason/file_hashes/final_status/risk_status table |
| `test_nonterminal_reviewed_entries_remain_visible_until_terminal_resolution` | reviewed unchanged filesystem-only skills are not hidden as resolved | inventory + matching non-terminal disposition ledger with `file_hashes.reviewed_file_sha256` | path is marked reviewed but remains visible/unresolved; only terminal final_status removes unresolved loss-risk |
| `test_promote_commit_disposition_requires_tracked_active_result` | promotion actually removes loss risk | disposition `promote_commit` for a filesystem-only skill | manual reconcile validation fails until final_path is present in tracked active skill files |
| `test_promote_ignored_skill_requires_force_add_attestation` | ignored-path promotions are intentional | gitignored filesystem-only skill with promote/redact disposition | manual reconcile validation requires `force_add_attestation_when_ignored` with ignore rule/line and final `git ls-files` evidence; personal paths additionally require `user_authorization_when_personal` |
| `test_archived_duplicate_collision_delta_is_zero_vs_prechange_baseline` | `_archived` loss-risk exclusion does not worsen legacy duplicate noise | frozen pre-change `_archived` duplicate/collision baseline captured before code edits + post-change run | duplicate/collision `{finding_key, severity, paths}` tuple set plus summary counts are unchanged; absolute pre-existing findings may remain documented |
| `test_issue_2488_baseline_order_guard_fails_when_fixture_added_after_logic_change` | pre-change proof is enforceable | `--base-ref`/`--head-ref` fake git log/range where fixture commit is newer than audit logic edit | `verify_issue_2488_baseline_order.py` and `scripts/skills/verify_issue_2488_baseline_order.sh` exit nonzero with actionable error |
| `test_issue_2488_baseline_order_guard_fails_same_commit` | same-commit baseline capture is not accepted as pre-change proof | `--base-ref`/`--head-ref` fake range where fixture and first audit/policy logic edit are in one commit | guard exits nonzero and instructs to split baseline into a predecessor commit |
| `test_manual_reconcile_invokes_baseline_order_guard_in_strict_mode` | baseline-order guard is bound to closeout, not prose-only | strict manual reconcile with audit/policy changes and mocked guard failure | reconcile exits nonzero before writing report; `--no-strict` cannot bypass this guard |
| `test_scan_attestation_required_for_promote_commit_and_personal_or_memory_skills` | conditional secret/content scans are contractual | promote/redact/consolidate disposition missing structured scan attestation | manual reconcile validation fails with actionable error |
| `test_file_hashes_rules_are_disposition_specific` | SHA evidence is not ambiguous | dispositions promote/redact/consolidate/archive/delete/ignore with mismatched original/final hashes | validator requires the disposition-specific `file_hashes` object and rejects singular legacy hash fields or mismatched original/final hashes with disposition-specific error |
| `test_personal_skill_promotion_requires_user_authorization_field` | personal ignored skills are not force-added on reviewer judgment alone | leaf slug matching `.gitignore`-style `personal-*` plus promote/redact disposition but no authorization field | manual reconcile validation fails |
| `test_deleted_or_archived_terminal_states_do_not_reopen_when_original_path_absent` | delete/archive lifecycles are deterministic | ledger entry with final_status deleted/archived and original path absent | weekly audit treats entry as resolved, not reopened |
| `test_existing_duplicate_collision_fixture_counts_unchanged` | duplicate/collision baseline behavior not broken | frozen existing fixture before and after inventory extension | duplicate/collision summary counts and finding IDs are unchanged |

---

## Acceptance Criteria

- [ ] RED tests are added before implementation for tracked-vs-filesystem inventory and filesystem-only active skill reporting.
- [ ] Weekly audit JSON includes `inventory_summary.counts`, `inventory_summary.paths`, and `inventory_summary.mirrors`; counts are numeric and include exactly `tracked_total`, `tracked_active`, `filesystem_total`, `filesystem_active`, `filesystem_only_total`, `filesystem_only_active`, `missing_tracked_total`, `missing_tracked_active`, `filesystem_only_archived_total`, and `legacy_diverged_compatibility_total` where the diverged count is the de-duplicated union of tracked and filesystem `_diverged` SKILL.md paths; path arrays for filesystem/missing/archived use `{path, informational_namespace, ledger_status}` objects and `issue_body_six_drift` uses `{path, drift_status, reason}` objects; `_core`/`_internal` paths remain active loss-risk but carry `informational_namespace: true`, mirror fields are symlink/status strings. Stable field names include `missing_tracked_active` and `filesystem_only_active`. Active filesystem-only files that remain on disk are listed regardless of ledger status; ledger status only affects unresolved counts/severity.
- [ ] `config/skills/weekly-audit-policy.yaml` defines `filesystem_only_active` in the existing append-only v2 policy schema (`v2.rules.filesystem-inventory.filesystem-only-active`, `weekly_summary_sections`, and `ranking_policy.section_order` with `filesystem_only_inventory` immediately after `changed_findings` and immediately before `unresolved_high_confidence_findings`), and tests prove the weekly-audit parser plus `_finding_defaults()`, `_baseline_finding_sources()`, `_all_active_findings()`, `run_audit()` `summary_counts`, and Markdown rendering consume those keys rather than hard-coding severity in Python; do not introduce an undocumented top-level `signals` map.
- [ ] Weekly Markdown output includes a policy-ordered `filesystem_only_inventory` / “Filesystem-only skill files” policy entry listing active filesystem-only skills when any exist, documented in `docs/standards/weekly-skills-audit-policy.md`; `_write_markdown_artifact()` consumes `ranking_policy.section_order` for exactly these six policy-governed sections: `new_findings`, `changed_findings`, `filesystem_only_inventory`, `unresolved_high_confidence_findings`, `suppressed_carry_forward_findings`, and `operational_errors_or_skipped_inputs`; v2-family legacy sections remain literal unless future policy work moves them under `weekly_summary_sections`, while high-signal unresolved findings are rendered through the same active-finding shape used by existing families.
- [ ] Active loss-risk filtering for #2488 uses `Path.parts` exact segment equality and excludes exact path segments `_archive` and `_archived`; `_diverged` is excluded from #2488 active-loss findings to preserve the existing quarantine semantic, and it is additionally reported as a separate legacy-compatibility count so historical issue-body/count drift is explicit; `_core` and `_internal` filesystem-only skills remain reportable as active loss-risk; legacy duplicate/collision behavior is not worsened by #2488; implementation must record a pre-change `_archived` duplicate/collision baseline in a strict predecessor commit before audit/policy logic changes and assert duplicate/collision delta is zero against the `{finding_key, severity, paths}` tuple set, not just counts; absolute pre-existing findings may remain documented rather than changing `EXCLUDED_DIRS`.
- [ ] `.codex/skills` and `.gemini/skills` remain symlink mirrors; no provider duplicate skill trees are created.
- [ ] Every active filesystem-only skill discovered at the implementation-time manual reconcile pass is individually dispositioned in `config/skills/filesystem-only-skill-dispositions.yaml` with disposition, reason, reviewer/date, disposition-specific `file_hashes`, final_status/final_path, issue_body_drift_note when applicable, structured scan_attestation where applicable, and a trust attestation at `docs/reports/2026-04-25-skills-disposition-2488-trust-attestation.json` when replay evidence is used. The six issue-body paths must each have either a terminal disposition or `issue_body_drift_note: {path, last_seen_evidence, vanished_at_reconcile_at, reviewer, rationale}` if the path vanished before reconcile; success is not hard-coded to six if additional live filesystem-only active skills appear.
- [ ] Valuable skills are committed/promoted in canonical `.claude/skills/...` paths; every `promote_commit`, `redact_then_commit`, or `consolidate_then_commit` ledger entry is verified to appear in tracked active skill files after reconciliation; if a path is gitignored, the ledger records the exact ignore rule and the implementation uses targeted `git add -f` only after scan/disposition approval; non-active references are intentionally archived, deleted with reason, or documented as ignored/transient; nothing is mass-added blindly.
- [ ] Manual reconcile validation confirms both `missing_tracked_active = 0` and `unresolved_filesystem_only_active = 0` after applying terminal dispositions, and reports `risk_status=eliminated` for promote/archive/delete outcomes versus `risk_status=accepted` for intentionally ignored/generated/transient files that remain active filesystem-only on disk; using terminal-state rules and strict-mode baseline-order guard invocation: promoted/redacted/consolidated entries tracked active at final_path; archived/deleted entries absent from active filesystem-only inventory with recorded final_status; ignored entries backed by durable policy rationale. Recurring weekly reports still list any ignored active filesystem-only files that remain on disk with `ledger_status: resolved_ignored` rather than hiding them.
- [ ] Existing weekly audit behavior remains backward-compatible: pre-existing duplicate/collision tests still pass, and new tests are added for the inventory/disposition extension.
- [ ] `docs/reports/2026-04-25-skills-disposition-2488.md` is generated once during implementation closeout at the tracked docs path with stable Markdown schema and matches the YAML disposition ledger; the recurring weekly cron does not rewrite tracked docs.
- [ ] `scripts/cron/skills-curation.sh` remains unchanged unless a test proves wrapper changes are necessary; the existing weekly audit CLI flags (`--skills-dir`, `--output-dir`, `--policy`, `--waivers`, `--render-github-payload`) remain backward-compatible, and tracked reconcile report generation is only available through the separate manual `scripts/skills/reconcile_filesystem_only_skills.py --disposition-report docs/reports/2026-04-25-skills-disposition-2488.md` entrypoint; `tests/cron/test_skills_curation.py` continues to cover dry-run/help/output-root/stale-workspace behavior.
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` description for `skills-curation` is updated from v1 duplicate/leaf/wrapper-only wording to exact v2 wording “Weekly skills curation v2: duplicate names, leaf collisions, wrapper pairs, and filesystem-only active skill loss-risk inventory. Local-only/report-only; no network posting. Issue #2488.”; `TestScheduleIntegration.test_validate_schedule_still_passes_with_skills_curation_task` asserts the updated text while preserving schedule/command.
- [ ] `docs/ops/scheduled-tasks.md` documents the manual reconcile command, all CLI flags, exit codes 0/2/3/4, and git trust-check failure modes.
- [ ] Before posting `status:plan-review`, each cited immutable review artifact (fresh post-revision timestamped `*-plan-2488-*.md`, including explicit UNAVAILABLE placeholder and disagreement artifact when used) is non-empty, contains a parseable `## Verdict` or `## Verdicts` heading, records the reviewed plan commit or plan SHA256, and has no unresolved MAJOR findings before the gate; the Adversarial Review Summary cites the artifact path used as evidence.
- [ ] No unrelated local dirt is staged or committed.
- [ ] Final plan comment containing the plan link, scope, review synthesis, and explicit approval request is posted to [#2488](https://github.com/vamseeachanta/workspace-hub/issues/2488), `status:plan-review` is applied and verified on the issue, and implementation remains blocked until the user explicitly approves and the issue is moved to `status:plan-approved`.
- [ ] As the first implementation step before changing audit logic, the implementation records a pre-change `_archived` duplicate/collision baseline in `tests/fixtures/skills/issue-2488-archived-duplicate-baseline.json` and summarizes it in the disposition report so regression tests cannot claim “pre-existing” without evidence; `scripts/skills/verify_issue_2488_baseline_order.sh` is run in manual closeout, its output is included in the final implementation review prompt, and the manual reconcile strict mode exits nonzero and final implementation review package is incomplete if the fixture was added in the same commit as, or after, the first audit/policy logic change in the implementation branch/range.
- [ ] Sparse-checkout/partial `git ls-files` states are detected via `git rev-parse --is-inside-work-tree`, `git config --bool core.sparseCheckout`, nonzero `git ls-files -z -- <resolved skills_dir relative to repo_root>`, or adapter partial/truncated flags; weekly audit warns and avoids authoritative missing-tracked findings, while manual reconcile exits nonzero before writing reports.
- [ ] Any promotion of a personal skill, defined as a skill whose leaf directory slug matches `.gitignore`-style `personal-*` (including `personal-tax-filing-packet`), requires explicit user authorization recorded in `user_authorization_when_personal` in the disposition ledger in addition to scan attestation; if no explicit authorization is available during implementation, it must not be promoted and must be archived/deleted/ignored with rationale instead.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | Prior immutable `20260425T125029Z` evidence was MAJOR; latest mutable run is diagnostic only until copied to fresh immutable approval evidence | Latest review reduced blockers to interface-tightening items, but mutable fanout files are not approval evidence. This revision addresses the remaining items before the next immutable approval-evidence copy. |
| Codex | Prior immutable `20260425T125029Z` evidence was MAJOR; latest mutable run is diagnostic only until copied to fresh immutable approval evidence | Latest review still flagged review-evidence authority, drift-note schema, hash schema, replay trust, and family integration. This revision addresses those before the next immutable approval-evidence copy. |
| Gemini | UNAVAILABLE in immutable evidence `scripts/review/results/20260425T125029Z-plan-2488-gemini.md` | CLI filesystem scan errors; no substantive verdict. Treated as provider-infra N/A, not plan approval. |

**Overall result:** REVISING — current immutable review evidence `scripts/review/results/20260425T125029Z-plan-2488-*.md` and latest mutable diagnostics still contain MAJOR findings, so do not move to `status:plan-review` until a subsequent pushed re-review has no unresolved MAJOR findings. Gemini UNAVAILABLE is recorded as provider-infra N/A for this pass, not a content approval. Canonical mutable fanout files and mutable disagreement summaries are diagnostic only; fresh timestamped immutable provider artifacts are authoritative, and if a disagreement summary conflicts with provider artifacts the provider artifact verdicts win while the conflict itself blocks gate until adjudicated. If a provider dispatch produces empty output or CLI sandbox errors, create an explicit timestamped `UNAVAILABLE` artifact with the raw-error path and either retry with an artifact-inline/no-tools prompt or keep the approval gate blocked unless the user explicitly authorizes reduced-provider review for that run.

Revisions made based on review:
- Replaced stale PENDING review summary with latest provider state.
- Added `config/scheduled-tasks/schedule-tasks.yaml` and `tests/cron/test_skills_curation.py` to resource intelligence/evidence.
- Specified that `filesystem_only_active` extends the existing `weekly-audit-policy.yaml` schema append-only rather than introducing an undocumented top-level `signals` map.
- Made scheduled YAML description update mandatory for v2 text while preserving schedule/command/machines/log path.

---

## Risks and Open Questions

- **Risk:** live counts can drift between planning and implementation. Mitigation: implementation must compute live counts at runtime and record the timestamp/source rather than hard-coding counts; the current verified baseline is tracked total `3028`, tracked active `922`, filesystem total `3100`, filesystem active `928`, filesystem-only total `72`, filesystem-only active `6`. The planning-time six are local filesystem evidence and must be recomputed before closeout.
- **Risk:** `logs/maintenance/...` is transient/ignored. Mitigation: recurring generated weekly audit artifacts remain under `logs/maintenance/...` and operators see filesystem-only listings in local untracked cron output; durable disposition state lives in `config/skills/filesystem-only-skill-dispositions.yaml`; the tracked docs report is manual reconcile only.
- **Risk:** committing untracked active skills without content review could preserve low-quality, generated, PII, or secret-bearing artifacts. Mitigation: require per-skill disposition, structured scan attestation, final_status/final_path, and rationale before any `git add`.
- **Risk:** adding filesystem-only findings to the same duplicate/collision classification pipeline could create noisy false positives. Mitigation: use a separate `filesystem_inventory_findings` family and `filesystem_only_inventory` weekly section governed by append-only entries in the existing `config/skills/weekly-audit-policy.yaml` schema, not a second top-level policy surface.
- **Risk:** changing `EXCLUDED_DIRS` would alter legacy duplicate/collision audit semantics and expose existing policy/code drift (`weekly-audit-policy.yaml` treats `_archive`/`_archived` as aliases while code excludes `_archive`/`_diverged`). Mitigation: do not extend `EXCLUDED_DIRS`; implement a separate `Path.parts` active loss-risk filter that excludes exact path segments `_archive` and `_archived` for #2488 loss-risk counts only; `_diverged` is excluded from #2488 active-loss findings to preserve quarantine semantics and is reported as a separate legacy compatibility count; record the policy/code drift as a named follow-up issue during implementation if not fixed here; until then, the #2488 implementation must not change legacy `EXCLUDED_DIRS`.
- **Decision:** durable disposition state lives in `config/skills/filesystem-only-skill-dispositions.yaml`; v2 rule/weekly-summary ranking lives append-only in the existing `config/skills/weekly-audit-policy.yaml` schema; the human-readable one-time implementation triage report path is `docs/reports/2026-04-25-skills-disposition-2488.md`; recurring scheduled audit artifacts remain under `logs/maintenance/` only and must not mutate tracked docs.
- **Decision:** `scripts/cron/skills-curation.sh` should remain unchanged unless implementation tests prove otherwise; wrapper invariance is part of the implementation acceptance criteria.
- **Decision:** future ignored skills under broad ignore prefixes remain visible through the weekly filesystem-only signal; for approved promoted skills, implementation may use targeted `git add -f`, and must not broadly unignore private/vendor/generated namespaces.

---

## Complexity: T3

**T3** — moderate multi-file maintenance/audit enhancement with tests, one existing script, likely one existing test module, docs/policy updates, and a controlled disposition pass over locally discovered skill files, explicit ignored-path tracking evidence, and operator-facing docs. It does not require broad ecosystem rewrite or multi-repo architecture changes.
