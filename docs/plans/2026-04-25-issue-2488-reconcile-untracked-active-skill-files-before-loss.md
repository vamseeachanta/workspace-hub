# Plan for #2488: reconcile untracked active skill files before loss

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2488
> **Review artifacts:** scripts/review/results/2026-04-25-plan-2488-claude.md | scripts/review/results/2026-04-25-plan-2488-codex.md | scripts/review/results/2026-04-25-plan-2488-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/weekly_skills_audit.py` — deterministic weekly skill audit entrypoint already exists from #2281/#2486. It scans `.claude/skills`, excludes `_archive` and `_diverged`, classifies duplicate canonical names / leaf collisions / wrapper pairs, applies baseline and waiver logic, and emits JSON + Markdown artifacts. Gap: it does not currently model tracked-vs-filesystem inventory or filesystem-only active skills as a first-class high-signal finding.
- Found: `scripts/cron/skills-curation.sh` — existing cron wrapper runs `uv run --no-project python scripts/skills/weekly_skills_audit.py` and supports `SKILLS_AUDIT_OUTPUT_ROOT` for redirectable test output. #2488 must preserve this local-only deterministic wrapper and avoid adding network posting.
- Found: `tests/skills/test_weekly_skills_audit.py` — existing pytest coverage for inventory scope, classification buckets, output schema, baseline delta, waiver handling, and read-only behavior. Gap: no coverage currently asserts that active filesystem-only `SKILL.md` files are detected/reported distinctly from tracked active skills.
- Found: current live inventory re-check on 2026-04-25 from repo root: tracked total `3028`, tracked active `922` when excluding `_archive` and `_archived`, filesystem total `3100`, filesystem active `928`, untracked/filesystem-only total `72`, untracked/filesystem-only active `6`, missing tracked active from filesystem `0`. This matches the issue-body conclusion: no tracked active skills are missing, but six active filesystem-only skills are at loss risk. Note: excluding only `_archive` and `_diverged` yields tracked active `928`; adding `_archived` excludes the six tracked `email/_archived` skills and yields the stricter active baseline `922`.
- Found: mirror state remains canonical and must be preserved: `.codex/skills -> ../.claude/skills`; `.gemini/skills -> ../.claude/skills`. #2488 must not duplicate provider skill trees.

### Standards
| Standard | Status | Source |
|---|---|---|
| Mandatory issue planning gate | required | `AGENTS.md`, `docs/plans/README.md`, `docs/plans/_template-issue-plan.md` |
| TDD before implementation | required | `AGENTS.md` |
| Weekly skills audit policy | active / relevant | `config/skills/weekly-audit-policy.yaml`, `docs/standards/weekly-skills-audit-policy.md` |
| Document intelligence entry point | checked / low direct relevance | `docs/document-intelligence/README.md` — navigation/provenance context; no additional skill-curation constraints found. |
| Existing scheduled-task contract | active / relevant | `scripts/cron/skills-curation.sh`, `docs/ops/scheduled-tasks.md` |

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
- EXISTS: `scripts/cron/skills-curation.sh` — lines 41-47 build the command array and append `--output-dir` when `SKILLS_AUDIT_OUTPUT_ROOT` is set; lines 51-55 print that command in dry-run mode.
- EXISTS: `tests/skills/test_weekly_skills_audit.py` — tests cover inventory/classification/output but not tracked-vs-filesystem loss-risk reporting.
- EXISTS: `config/skills/weekly-audit-policy.yaml` — classification buckets and carry-forward rules remain authoritative for existing duplicate/collision findings.

**Live inventory proof** (command embedded per the plan evidence contract, 2026-04-25):
```bash
uv run --no-project python - <<'PY'
from pathlib import Path
import subprocess
root = Path('.').resolve()
skills = root / '.claude/skills'
tracked = [p for p in subprocess.check_output(['git','ls-files','.claude/skills'], text=True).splitlines() if p.endswith('/SKILL.md')]
fs = [str(p.relative_to(root)) for p in skills.rglob('SKILL.md')]
def active(p):
    return not any(f'/{x}/' in p for x in ('_archive','_archived'))
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
| `.claude/skills/business_admin/personal-tax-filing-packet/SKILL.md` | `pending_full_file_scan_and_user_authorization` | Local personal/tax workflow evidence only; do not promote unless full-file scan is clean/redacted and user explicitly authorizes tracking a formerly `personal-*` ignored skill in this public-by-default repo. |
| `.claude/skills/digitalmodel/blender-worktree-test-hardening/SKILL.md` | `pending_full_scan` | Captures a recurring digitalmodel worktree/Blender test-hardening failure mode; promote/consolidate/archive/delete only after live scan and ignored-path evidence. |
| `.claude/skills/digitalmodel/digitalmodel-worktree-test-execution-with-shared-venv/SKILL.md` | `pending_full_scan` | Valuable shared-venv workaround candidate; may overlap with Blender-specific skill, so implementation decides promote-separate vs consolidate with rationale and ignored-path evidence. |
| `.claude/skills/digitalmodel/library-evaluation-integration/SKILL.md` | `pending_full_scan` | Reusable scientific-library evaluation candidate; promote/consolidate/archive/delete only after live scan and ignored-path evidence. |
| `.claude/skills/digitalmodel/orcaflex-reporting-fixture-proof-pattern/SKILL.md` | `pending_full_scan` | Reusable OrcaFlex reporting fixture/snapshot candidate; promote/consolidate/archive/delete only after live scan and ignored-path evidence. |
| `.claude/skills/memory/hermes-memory-bridge/SKILL.md` | `pending_full_scan` | Durable memory-bridge candidate; promote/redact/archive/delete only after live scan, accuracy check, and ignored-path evidence. |

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
| Plan review — Claude | `scripts/review/results/2026-04-25-plan-2488-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-25-plan-2488-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-25-plan-2488-gemini.md` |

---

## Deliverable

A deterministic extension to the weekly skills housekeeping workflow that surfaces active filesystem-only skills as loss-risk findings, plus a one-time disposition of every active filesystem-only skill discovered at implementation time so valuable skills are preserved and junk/transient artifacts are explicitly classified.

---

## Pseudocode

```text
function build_skill_inventory_with_git(skills_dir, repo_root, tracked_paths=None, git_list_fn=None, symlink_resolver=None):
    if tracked_paths is provided, use it (test seam for tmp_path fixtures)
    else call git_list_fn or default git ls-files for repo-relative skills_dir ending /SKILL.md; never hard-code .claude/skills when --skills-dir points elsewhere
    filesystem_skill_paths = all SKILL.md under skills_dir
    active_filter(path): exact path segments _archive and _archived are non-active for #2488 loss-risk counts, matching the issue definition; report legacy `_diverged` exclusion separately for compatibility metrics
    _core and _internal remain in-scope for filesystem-only loss-risk reporting; do not reuse INFORMATIONAL_DIRS to suppress them
    audit_inventory_filter(path): keep existing EXCLUDED_DIRS behavior for duplicate/collision pipeline; do not add _archived to EXCLUDED_DIRS unless a separate review approves changing legacy audit semantics
    return counts and path sets:
        tracked_total, tracked_active
        filesystem_total, filesystem_active
        filesystem_only_total, filesystem_only_active
        missing_tracked_total, missing_tracked_active
        filesystem_only_archived_total
        legacy_diverged_compatibility_total
        codex_skills_link, gemini_skills_link
    JSON schema:
        inventory_summary.counts = {tracked_total, tracked_active, filesystem_total, filesystem_active, filesystem_only_total, filesystem_only_active, missing_tracked_total, missing_tracked_active, filesystem_only_archived_total, legacy_diverged_compatibility_total}
        inventory_summary.paths = {filesystem_only_active: [{path, informational}], missing_tracked_active: [{path, informational}], filesystem_only_archived: [{path, informational}]}
        inventory_summary.mirrors = {codex_skills_link, gemini_skills_link}

function classify_filesystem_only_skill(path):
    read full file for scan-sensitive skills; read frontmatter and first content section for initial routing
    inspect current file content and frontmatter first
    inspect git history using deterministic fallback keys (frontmatter name and leaf slug), because a filesystem-only path itself may have no git history; git-history lookup failures are non-fatal warnings in weekly_report and manual_closeout evidence, not cron failures
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
    use signal vocabulary/ranking from config/skills/weekly-audit-policy.yaml for filesystem_only_active
    append inventory_summary to JSON artifact
    append Markdown section "Filesystem-only skill files"
    mark unresolved filesystem_only_active_count > 0 as high-signal maintenance finding
    unresolved findings are reportable, not a weekly-cron hard failure
    preserve local-only/no-network behavior and write recurring outputs only under the configured output_dir/logs/maintenance/skills-curation/ tree

function validate_and_render_dispositions(disposition_yaml, mode):
    mode is explicit CLI: `--mode {weekly_report,manual_closeout}` defaulting to `weekly_report`; optional `--disposition-ledger` and `--disposition-report` are honored only for manual_closeout
    weekly_report: load ledger, classify unresolved paths, never write tracked docs, never fail solely because a new filesystem-only skill lacks disposition
    manual_closeout: require one entry per active filesystem-only skill discovered at implementation time; fail on missing/invalid entries; render docs/reports/2026-04-25-skills-disposition-2488.md
    require fields: path, disposition, reason, reviewed_at, reviewer, reviewed_file_sha256, final_status, final_path, scan_attestation, force_add_attestation_when_ignored
    define reviewed_file_sha256 = sha256 of the exact SKILL.md file bytes at review time; for terminal move/archive/delete actions record the pre-action sha256 plus final_status/final_path
    allowed dispositions: promote_commit, consolidate_then_commit, redact_then_commit, archive_intentionally, ignore_generated_transient, delete_if_junk
    scan_attestation schema: {tool_or_method, scope: full_file|frontmatter|content_overlap, scanned_at, finding_count, finding_summary, reviewer}; force_add_attestation schema when ignored: {gitignore_rule, gitignore_line, git_add_force_required, git_add_force_invoked_at, final_git_ls_files_contains_path}
    terminal-state rules:
        promote_commit/redact_then_commit: resolved when final_path exists in tracked active skills and disposition records whether the final path required `git add -f`; consolidate_then_commit: resolved when final_path exists in tracked active skills AND original path is absent from active filesystem-only inventory
        archive_intentionally: resolved only when original path is absent from active filesystem-only set and final_path is under an archive segment or tracked archive path
        delete_if_junk: resolved only when original path is absent and final_status is deleted_with_reason
        ignore_generated_transient: resolved only when a matching durable policy/ignore rationale exists in the ledger/YAML policy
    future weekly audit runs read the YAML ledger and mark terminal resolved entries resolved; reviewed_file_sha256 matching on non-terminal unchanged filesystem-only entries marks them reviewed but still visible as unresolved local filesystem-only inventory; terminal entries are governed by final_status/final_path rules and are the only states that remove unresolved loss-risk

implementation_flow():
    RED: add tests for inventory_summary and filesystem_only_active reporting
    GREEN: implement minimal tracked-vs-filesystem inventory helper and output section
    RED/GREEN: add fixture tests for symlink mirror reporting and _archived exclusion
    RED/GREEN: add disposition ledger plus explicit manual-closeout report mode for every active filesystem-only skill discovered at implementation time
    verify no unrelated local dirt is staged
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/skills/weekly_skills_audit.py` | Add tracked-vs-filesystem inventory summary, filesystem-only active skill reporting, disposition-ledger loading/validation/rendering helpers, and mirror/symlink status reporting. Keep legacy duplicate/collision `EXCLUDED_DIRS` behavior unchanged; use a separate active loss-risk filter. |
| Modify | `tests/skills/test_weekly_skills_audit.py` | Add TDD coverage for tracked-vs-filesystem inventory via injectable tracked manifest/git adapter seam, active filesystem-only findings, missing tracked active files, active loss-risk filtering, disposition ledger/report schema, and symlink status serialization. |
| Modify | `config/skills/weekly-audit-policy.yaml` | Add `signals.filesystem_only_active` (severity/ranking/reporting mode) and `modes.weekly_report/manual_closeout` contract. |
| Create | `config/skills/filesystem-only-skill-dispositions.yaml` | Machine-readable disposition ledger for active filesystem-only skills; gives future audit runs a durable resolved/ignored/consolidated source of truth without overloading duplicate-skill buckets. |
| Modify | `docs/standards/weekly-skills-audit-policy.md` | Document new inventory summary schema, `filesystem_only_active` signal, `weekly_report` vs `manual_closeout`, disposition vocabulary, and scan_attestation schema. |
| Modify | `docs/ops/scheduled-tasks.md` | Document the `weekly_report` default mode, explicit `manual_closeout` invocation, tracked disposition ledger/report, and the fact that recurring cron remains local-only/report-only. |
| Create | `docs/reports/2026-04-25-skills-disposition-2488.md` | Durable, tracked disposition report for every active filesystem-only skill discovered at implementation-time. Use this tracked docs path because `.gitignore` ignores `logs/*`, including `logs/maintenance/...`. |
| Maybe add/track | active filesystem-only `SKILL.md` paths discovered at implementation time | Promote only those classified as valuable active skills; do not mass-add all 72 filesystem-only files. If a promoted path is ignored by `.gitignore`, use explicit `git add -f <path>` only after ledger scan/disposition evidence is recorded; do not broadly relax `.gitignore` for `digitalmodel/`, `personal-*`, or `memory/`. |
| Verify / maybe document | `.gitignore` | Do not change by default; record the current ignore rule for any promoted path in the disposition ledger and use targeted `git add -f` for approved promotions. Modify only if tests prove a narrow negation rule is safer than force-add; narrow negations for approved `.claude/skills/.../SKILL.md` paths are allowed, but broad unignores for `digitalmodel/`, `personal-*`, or `memory/` are not. |
| Update | `docs/plans/README.md` | Add or update the #2488 row; status should be `plan-review` when the approval gate is posted. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_inventory_summary_distinguishes_tracked_and_filesystem_skills` | canonical counts are explicit and testable without a real git repo | fixture skills + injected tracked manifest/git adapter | JSON summary includes tracked/filesystem totals and active counts |
| `test_inventory_summary_schema_separates_counts_paths_and_mirrors` | JSON shape is deterministic | fixture with filesystem-only and missing-tracked paths | `inventory_summary.counts` has numbers, `inventory_summary.paths` has arrays, `inventory_summary.mirrors` has symlink targets |
| `test_inventory_summary_reports_filesystem_only_active_skills` | loss-risk skills are visible | fixture active `SKILL.md` absent from tracked manifest | `filesystem_only_active` contains path and count > 0 |
| `test_inventory_summary_reports_missing_tracked_active_skills` | actual tracked skill loss would be detected | tracked manifest contains absent active path | `missing_tracked_active` contains path and count > 0 |
| `test_inventory_summary_excludes_archive_archived_and_reports_diverged_compatibility_count` | active filter matches #2488 loss-risk semantics and preserves segment-name pruning | fixture `_archive`, `_archived`, `_diverged`, normal paths, plus `_core`/`_internal` paths | `_archive`/`_archived` are excluded from #2488 loss-risk counts; `_diverged` remains included in #2488 active counts and is also reported in a separate legacy-compatibility count; `_core`/`_internal` filesystem-only skills still count as active loss-risk; substring-only names do not over-match |
| `test_inventory_summary_records_provider_skill_mirror_symlinks` | mirror status remains explicit | resolver-injection seam supplies `.codex/skills` and `.gemini/skills` link targets | JSON records links to `../.claude/skills` without platform-dependent symlink setup |
| `test_weekly_markdown_surfaces_filesystem_only_active_skills` | operator report is high-signal | audit result with active filesystem-only path | Markdown includes `Filesystem-only active skills` section and path |
| `test_filesystem_only_archived_skills_do_not_escalate_active_loss_risk` | archived local files do not create false active alarms | untracked `_archive` and `_archived` SKILL.md files | active loss-risk count remains 0; archived count is reported separately |
| `test_filesystem_only_core_and_internal_skills_are_not_suppressed` | control-plane/internal namespaces are still protected against untracked loss | untracked `_core` and `_internal` SKILL.md files | active filesystem-only count includes these paths |
| `test_disposition_ledger_accepts_only_known_disposition_values` | dispositions are machine-checkable | invalid disposition string | manual closeout validation fails |
| `test_weekly_mode_reports_unresolved_without_hard_failure` | recurring cron remains report-only | active filesystem-only skill without ledger entry | weekly result records high-signal finding and exits successfully |
| `test_git_inventory_failure_is_reported_not_cron_fatal` | weekly cron remains deterministic on Git errors | git_list_fn raises or skills_dir is outside a repo | weekly result records inventory warning and exits successfully |
| `test_policy_yaml_defines_filesystem_only_active_signal_and_modes` | YAML is authoritative | policy fixture | parser exposes `signals.filesystem_only_active` and `modes.weekly_report/manual_closeout` |
| `test_default_cli_mode_is_weekly_report_for_cron_wrapper` | wrapper invariance is protected | argparse/default CLI invocation with only --output-dir | mode defaults to `weekly_report` and does not write tracked docs |
| `test_cron_wrapper_dry_run_command_parses_with_default_mode` | wrapper command remains compatible with argparse | `bash scripts/cron/skills-curation.sh --dry-run` output | printed command parses without requiring `--mode` |
| `test_sparse_checkout_or_partial_git_inventory_is_warned_not_trusted` | successful-but-partial git inventory does not create false loss findings | git adapter reports sparse checkout or unexpectedly low tracked count | weekly report emits inventory warning and does not assert missing-tracked loss without explicit confirmation |
| `test_manual_closeout_mode_requires_complete_terminal_dispositions` | closeout gate is strict | active filesystem-only skill missing ledger entry or terminal state | manual closeout validation fails |
| `test_disposition_report_written_to_tracked_docs_path_with_stable_schema` | one-time closeout report is generated where Git can track it | valid disposition ledger | `docs/reports/2026-04-25-skills-disposition-2488.md` contains path/disposition/reason/reviewed_file_sha256 table |
| `test_nonterminal_reviewed_entries_remain_visible_until_terminal_resolution` | reviewed unchanged filesystem-only skills are not hidden as resolved | inventory + matching non-terminal disposition ledger with reviewed_file_sha256 | path is marked reviewed but remains visible/unresolved; only terminal final_status removes unresolved loss-risk |
| `test_promote_commit_disposition_requires_tracked_active_result` | promotion actually removes loss risk | disposition `promote_commit` for a filesystem-only skill | manual closeout validation fails until final_path is present in tracked active skill files |
| `test_promote_ignored_skill_requires_force_add_attestation` | ignored-path promotions are intentional | gitignored filesystem-only skill with promote/redact disposition | manual closeout validation requires `force_add_attestation_when_ignored` with ignore rule/line and either final `git ls-files` evidence or narrow negation evidence |
| `test_archived_loss_filter_does_not_create_new_duplicate_findings` | `_archived` loss-risk exclusion does not worsen legacy duplicate noise | `_archived` duplicate fixture | no new duplicate/collision finding is introduced by the inventory extension |
| `test_scan_attestation_required_for_promote_commit_and_personal_or_memory_skills` | conditional secret/content scans are contractual | promote/redact/consolidate disposition missing structured scan attestation | manual closeout validation fails with actionable error |
| `test_deleted_or_archived_terminal_states_do_not_reopen_when_original_path_absent` | delete/archive lifecycles are deterministic | ledger entry with final_status deleted/archived and original path absent | weekly audit treats entry as resolved, not reopened |
| `test_existing_weekly_audit_behavior_remains_backward_compatible` | duplicate/collision baseline behavior not broken | existing fixture tests | existing tests still pass |

---

## Acceptance Criteria

- [ ] RED tests are added before implementation for tracked-vs-filesystem inventory and filesystem-only active skill reporting.
- [ ] Weekly audit JSON includes `inventory_summary.counts`, `inventory_summary.paths`, and `inventory_summary.mirrors`; counts are numeric, paths are arrays of `{path, informational}` objects, mirror fields are symlink/status strings. Stable field names include `missing_tracked_active` and `filesystem_only_active`.
- [ ] `config/skills/weekly-audit-policy.yaml` defines concrete `signals.filesystem_only_active` and `modes.weekly_report/manual_closeout` keys, and tests prove the parser consumes those keys rather than hard-coding severity in Python.
- [ ] Weekly Markdown output includes a high-signal section listing active filesystem-only skills when any exist.
- [ ] Active loss-risk filtering for #2488 excludes exact path segments `_archive` and `_archived`; `_diverged` remains included in #2488 active counts and is additionally reported as a separate legacy-compatibility count; `_core` and `_internal` filesystem-only skills remain reportable as active loss-risk; legacy duplicate/collision behavior is not worsened by #2488; implementation must add a regression test that `_archived` active-loss exclusion does not create new duplicate/collision findings, and if current legacy behavior already reports `_archived` collisions, document that as pre-existing rather than changing `EXCLUDED_DIRS`.
- [ ] `.codex/skills` and `.gemini/skills` remain symlink mirrors; no provider duplicate skill trees are created.
- [ ] Every active filesystem-only skill discovered at the implementation-time manual-closeout pass is individually dispositioned in `config/skills/filesystem-only-skill-dispositions.yaml` with disposition, reason, reviewer/date, reviewed_file_sha256, final_status/final_path, and structured scan_attestation where applicable; the current known count is six local files, but success is not hard-coded to six if live state changes.
- [ ] Valuable skills are committed/promoted in canonical `.claude/skills/...` paths; every `promote_commit`, `redact_then_commit`, or `consolidate_then_commit` ledger entry is verified to appear in tracked active skill files after reconciliation; if a path is gitignored, the ledger records the exact ignore rule and the implementation uses either targeted `git add -f` or a narrow `.gitignore` negation for the approved skill path only after scan/disposition approval; non-active references are intentionally archived, deleted with reason, or documented as ignored/transient; nothing is mass-added blindly.
- [ ] Manual closeout validation confirms both `missing_tracked_active = 0` and `unresolved_filesystem_only_active = 0` after reconciliation, using terminal-state rules: promoted/redacted/consolidated entries tracked active at final_path; archived/deleted entries absent from active filesystem-only inventory with recorded final_status; ignored entries backed by durable policy rationale.
- [ ] Existing weekly audit behavior remains backward-compatible: pre-existing duplicate/collision tests still pass, and new tests are added for the inventory/disposition extension.
- [ ] `docs/reports/2026-04-25-skills-disposition-2488.md` is generated once during implementation closeout at the tracked docs path with stable Markdown schema and matches the YAML disposition ledger; the recurring weekly cron does not rewrite tracked docs.
- [ ] `scripts/cron/skills-curation.sh` remains unchanged unless a test proves wrapper changes are necessary; the audit script CLI defaults to `--mode weekly_report`, and the tracked closeout report is generated only through explicit `--mode manual_closeout --disposition-report docs/reports/2026-04-25-skills-disposition-2488.md`.
- [ ] No unrelated local dirt is staged or committed.
- [ ] Plan review artifacts are posted before implementation begins.
- [ ] The implementation records a pre-change `_archived` duplicate/collision baseline in the closeout report or fixture so regression tests cannot claim “pre-existing” without evidence.
- [ ] Sparse-checkout/partial `git ls-files` states are detected or warned, and cannot generate authoritative missing-tracked loss findings without confirmation.
- [ ] Any promotion of `personal-tax-filing-packet` requires explicit user authorization in the disposition ledger in addition to scan attestation.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Pending plan-review fanout. |
| Codex | PENDING | Pending plan-review fanout. |
| Gemini | PENDING | Pending plan-review fanout. |

**Overall result:** PENDING — do not move to `status:plan-review` until this section is updated.

Revisions made based on review:
- Pending.

---

## Risks and Open Questions

- **Risk:** live counts can drift between planning and implementation. Mitigation: implementation must compute live counts at runtime and record the timestamp/source rather than hard-coding counts; the current verified baseline is tracked total `3028`, tracked active `922`, filesystem total `3100`, filesystem active `928`, filesystem-only total `72`, filesystem-only active `6`. The planning-time six are local filesystem evidence and must be recomputed before closeout.
- **Risk:** `logs/maintenance/...` is transient/ignored. Mitigation: recurring generated weekly audit artifacts remain under `logs/maintenance/...`; durable disposition state lives in `config/skills/filesystem-only-skill-dispositions.yaml`; the tracked docs report is manual closeout only.
- **Risk:** committing untracked active skills without content review could preserve low-quality, generated, PII, or secret-bearing artifacts. Mitigation: require per-skill disposition, structured scan attestation, final_status/final_path, and rationale before any `git add`.
- **Risk:** adding filesystem-only findings to the same duplicate/collision classification pipeline could create noisy false positives. Mitigation: use a separate inventory signal governed by concrete `signals.filesystem_only_active` policy keys in `config/skills/weekly-audit-policy.yaml`.
- **Risk:** changing `EXCLUDED_DIRS` would alter legacy duplicate/collision audit semantics. Mitigation: do not extend `EXCLUDED_DIRS`; implement a separate active loss-risk filter that excludes exact path segments `_archive` and `_archived` for #2488 loss-risk counts only; `_diverged` remains included in #2488 active counts and is also reported as a legacy compatibility count.
- **Decision:** durable disposition state lives in `config/skills/filesystem-only-skill-dispositions.yaml`; signal vocabulary/ranking lives in `config/skills/weekly-audit-policy.yaml`; the human-readable one-time implementation triage report path is `docs/reports/2026-04-25-skills-disposition-2488.md`; recurring scheduled audit artifacts remain under `logs/maintenance/` only and must not mutate tracked docs.
- **Decision:** `scripts/cron/skills-curation.sh` should remain unchanged unless implementation tests prove otherwise; wrapper invariance is part of the implementation acceptance criteria.
- **Decision:** future ignored skills under broad ignore prefixes remain visible through the weekly filesystem-only signal; for approved promoted skills, implementation may use targeted `git add -f` or narrow `.gitignore` negations, but must not broadly unignore private/vendor/generated namespaces.

---

## Complexity: T3

**T3** — moderate multi-file maintenance/audit enhancement with tests, one existing script, likely one existing test module, optional docs/policy updates, and a controlled disposition pass over locally discovered skill files, explicit ignored-path tracking evidence, and operator-facing docs. It does not require broad ecosystem rewrite or multi-repo architecture changes.
