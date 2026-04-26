# Plan for #2488: reconcile untracked active skill files before loss

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2488
> **Historical review artifacts (superseded; not approval-gate evidence):** scripts/review/results/20260425T125029Z-plan-2488-claude.md | scripts/review/results/20260425T125029Z-plan-2488-codex.md | scripts/review/results/20260425T125029Z-plan-2488-gemini.md | scripts/review/results/20260425T125029Z-plan-2488-disagreement.md
> **Approval-gate review artifacts:** TBD after fresh post-revision review; this is a pre-implementation governance step, not a #2488 deliverable. The reviewer/operator may manually copy the latest non-empty fanout/fallback stdout into timestamped immutable artifacts and note the reviewed commit/SHA256 in the artifact header or companion comment; no repository script change is required by this plan.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/weekly_skills_audit.py` — deterministic weekly skill audit entrypoint already exists from #2281/#2486. It scans `.claude/skills`, excludes `_archive` and `_diverged`, classifies duplicate canonical names / leaf collisions / wrapper pairs, applies baseline and waiver logic, and emits JSON + Markdown artifacts. Gap: it does not currently model tracked-vs-filesystem inventory or filesystem-only active skills as a first-class high-signal finding.
- Found: `scripts/cron/skills-curation.sh` — existing cron wrapper runs `uv run --no-project python scripts/skills/weekly_skills_audit.py` and supports `SKILLS_AUDIT_OUTPUT_ROOT` for redirectable test output. #2488 must preserve this local-only deterministic wrapper and avoid adding network posting.
- Found: `tests/skills/test_weekly_skills_audit.py` — existing pytest coverage for inventory scope, classification buckets, output schema, baseline delta, waiver handling, read-only behavior, and `TestScheduleIntegration.test_validate_schedule_still_passes_with_skills_curation_task` for `config/scheduled-tasks/schedule-tasks.yaml`. Gap: no coverage currently asserts that active filesystem-only `SKILL.md` files are detected/reported distinctly from tracked active skills.
- Found: `tests/cron/test_skills_curation.py` — existing wrapper regression coverage for `--dry-run`, `--help`, `SKILLS_AUDIT_OUTPUT_ROOT` forwarding, and stale `WORKSPACE_HUB` handling; #2488 must preserve these invariants while keeping one-time disposition closeout outside the cron path.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — authoritative scheduled-task source includes `id: skills-curation`, Monday 04:00 schedule, wrapper command, and description currently saying duplicate/leaf/wrapper audit and “Read-only in v1. Issue #2281.” #2488 should update the YAML description only if the recurring task contract text changes; the command remains the wrapper.
- Found: `.gitignore` — verifies the parent-directory rules that make the six active filesystem-only paths require care before promotion: `digitalmodel/`, `personal-*`, and `memory/`; final implementation must cite the live rule evidence in the disposition report before any targeted `git add -f`.
- Found: current live inventory re-check on 2026-04-25 from repo root: tracked total `3028`, tracked active `922` when excluding `_archive` and `_archived`, filesystem total `3100`, filesystem active `928`, untracked/filesystem-only total `72`, untracked/filesystem-only active `6`, missing tracked active from filesystem `0`. This matches the issue-body conclusion and is preserved in tracked planning evidence `docs/reports/issue-2488-planning-inventory-snapshot.json`: no tracked active skills are missing, but six active filesystem-only skills are at loss risk. Note: excluding only `_archive` and `_diverged` yields tracked active `928`; adding `_archived` excludes the six tracked `email/_archived` skills and yields the stricter active baseline `922`: `.claude/skills/email/_archived/gmail-data-extraction/SKILL.md`, `.claude/skills/email/_archived/gmail-email-to-repo-extraction/SKILL.md`, `.claude/skills/email/_archived/gmail-extract-and-clean/SKILL.md`, `.claude/skills/email/_archived/gmail-extract-archive/SKILL.md`, `.claude/skills/email/_archived/gmail-touchbase/SKILL.md`, `.claude/skills/email/_archived/gmail-unsubscribe/SKILL.md`.
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
- `docs/ops/scheduled-tasks.md` — operator-facing scheduled-task table already lists Monday 04:00 `skills-curation`; #2488 should update narrowly because recurring output semantics add filesystem-only active loss-risk inventory; preserve the existing local-only/artifact-location contract.

### Gaps identified
- No first-class audit field/report currently distinguishes tracked skill files, filesystem skill files, active filesystem-only skill files, archived filesystem-only skill files, mirror/symlink state, and missing tracked active files in one canonical inventory summary.
- No regression test currently fixtures a skill tree plus a simulated tracked-file manifest to prove active filesystem-only `SKILL.md` files are surfaced as high-signal maintenance findings.
- The six currently known active filesystem-only skills have not been individually dispositioned as `promote/commit`, `archive`, `ignore/generated/transient`, or `delete`. Implementation must disposition every active filesystem-only skill discovered at runtime, not just these six if live state drifts.
- No durable disposition report exists yet for the current 72 filesystem-only `SKILL.md` files. #2488 prioritizes active loss-risk files; archived-only filesystem-only files should be reported informationally and explicitly accepted as non-active loss risk unless separately promoted by follow-up.

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
| `.claude/skills/business_admin/personal-tax-filing-packet/SKILL.md` | `default_do_not_promote_without_explicit_later_authorization` | Local personal/tax workflow evidence only; ignored by `.gitignore` `personal-*` rule. #2488 approval does not authorize promotion; implementation must archive/ignore/delete with rationale unless the user gives separate explicit tracking authorization during implementation after full-file scan/redaction. |
| `.claude/skills/digitalmodel/blender-worktree-test-hardening/SKILL.md` | `pending_full_scan` | Captures a recurring digitalmodel worktree/Blender test-hardening failure mode; promote/consolidate/archive/delete only after live scan and ignored-path evidence (`.gitignore` `digitalmodel/` rule). |
| `.claude/skills/digitalmodel/digitalmodel-worktree-test-execution-with-shared-venv/SKILL.md` | `pending_full_scan` | Valuable shared-venv workaround candidate; may overlap with Blender-specific skill, so implementation decides promote-separate vs consolidate with rationale and ignored-path evidence (`.gitignore` `digitalmodel/` rule). |
| `.claude/skills/digitalmodel/library-evaluation-integration/SKILL.md` | `pending_full_scan` | Reusable scientific-library evaluation candidate; promote/consolidate/archive/delete only after live scan and ignored-path evidence (`.gitignore` `digitalmodel/` rule). |
| `.claude/skills/digitalmodel/orcaflex-reporting-fixture-proof-pattern/SKILL.md` | `pending_full_scan` | Reusable OrcaFlex reporting fixture/snapshot candidate; promote/consolidate/archive/delete only after live scan and ignored-path evidence (`.gitignore` `digitalmodel/` rule). |
| `.claude/skills/memory/hermes-memory-bridge/SKILL.md` | `pending_full_scan` | Durable memory-bridge candidate; ignored by `.gitignore` `memory/` rule; promote/redact/archive/delete only after live scan, accuracy check, and ignored-path evidence. |

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
| Durable disposition report | `docs/reports/issue-2488-skills-disposition.md` |
| Mutable fanout output — Claude (diagnostic only; not approval evidence) | `scripts/review/results/2026-04-25-plan-2488-claude.md` |
| Mutable fanout output — Codex (diagnostic only; not approval evidence) | `scripts/review/results/2026-04-25-plan-2488-codex.md` |
| Mutable fanout output — Gemini (not approval evidence if empty/overwritten) | `scripts/review/results/2026-04-25-plan-2488-gemini.md` |
| Mutable fanout output — disagreement/synthesis (diagnostic only; provider artifacts are authoritative on conflict) | `scripts/review/results/2026-04-25-plan-2488-disagreement.md` |
| Historical superseded review evidence — Claude (not gate evidence) | `scripts/review/results/20260425T125029Z-plan-2488-claude.md` |
| Historical superseded review evidence — Codex (not gate evidence) | `scripts/review/results/20260425T125029Z-plan-2488-codex.md` |
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
    else call git_list_fn or default git ls-files for repo-relative skills_dir ending /SKILL.md; never hard-code .claude/skills when --skills-dir points elsewhere; run `detect_git_inventory_trust()` that checks git command exit code, zero tracked results while filesystem skills exist, and `git config --bool core.sparseCheckout` + `git sparse-checkout list` coverage for skills_dir. The recurring weekly audit must not depend on the #2488 planning snapshot; the snapshot is only for one-time closeout drift reporting.
    filesystem_skill_paths = all SKILL.md under skills_dir using a non-pruning walk; do not reuse the existing duplicate/collision `build_inventory` walk for inventory totals because it prunes `_archive` and `_diverged` while not pruning `_archived`, so neither the legacy walk nor the strict #2488 active filter alone is sufficient
    active_filter(path): use `PurePosixPath(path).parts`/`Path.parts` exact segment equality; load archive aliases from `category_alias_families.archive.aliases` (`_archive`, `_archived` today) and exclude those exact segments for #2488 `tracked_active`, `filesystem_active`, and active-loss-risk counts. `_diverged` is diagnostic compatibility evidence only for #2488 and is not shipped as a stable recurring summary-count field unless a future issue adds a consumer.
    _core and _internal remain in-scope for filesystem-only loss-risk reporting; do not reuse INFORMATIONAL_DIRS to suppress them
    audit_inventory_filter(path): keep existing EXCLUDED_DIRS behavior for duplicate/collision pipeline; do not add _archived to EXCLUDED_DIRS unless a separate review approves changing legacy audit semantics
    return counts and path sets:
        tracked_total, tracked_active
        filesystem_total, filesystem_active
        filesystem_only_total, filesystem_only_active
        missing_tracked_total, missing_tracked_active
        filesystem_only_archived_total
        codex_skills_link, gemini_skills_link
    JSON schema:
        inventory_summary.counts = {tracked_total, tracked_active, filesystem_total, filesystem_active, filesystem_only_total, filesystem_only_active, missing_tracked_total, missing_tracked_active, filesystem_only_archived_total}
        inventory_summary.paths = {filesystem_only_active: [{path, informational}], missing_tracked_active: [{path, informational}], filesystem_only_archived: [{path, informational}]}; every path object in these arrays must include exactly `path` and `informational`. Issue-specific drift for the six #2488 paths is one-time closeout report content, not recurring weekly-audit schema
        inventory_summary.mirrors = {codex_skills_link, gemini_skills_link}

function classify_filesystem_only_skill(path):
    read full file for scan-sensitive skills; read frontmatter and first content section for initial routing
    inspect current file content and frontmatter first
    inspect git history using deterministic fallback keys (frontmatter name and leaf slug), because a filesystem-only path itself may have no git history; git-history lookup failures are non-fatal warnings in weekly_report evidence; the one-time disposition closeout re-runs live git/filesystem inventory before writing the report
    search canonical active skills for same frontmatter name, same leaf slug, or documented replacement
    assign disposition:
        promote_commit if valuable, unique, reusable, clean after scan, and either not ignored or approved for targeted `git add -f` with the matching ignore rule recorded
        consolidate_then_commit if valuable but overlapping with an existing skill; final_path points to the consolidated tracked skill
        redact_then_commit if valuable but full-file scan finds redactable PII/secrets/local-only details; require targeted `git add -f` evidence if final path remains ignored
        archive_intentionally if useful reference but not active routing material
        ignore_generated_transient only if tool-generated or machine-local with durable policy rationale and explicit accepted-risk status; this classifies rather than eliminates the active filesystem-only loss risk
        delete_if_junk only when provably useless and safe; closeout must remove the file and record terminal status
    require a rationale, scan/redaction note when applicable, and terminal-state rule for every disposition

function run_weekly_audit_extension():
    run existing weekly audit duplicate/collision logic with unchanged EXCLUDED_DIRS semantics
    compute separate inventory_summary using the active loss-risk filter
    use existing v2 policy/ranking from config/skills/weekly-audit-policy.yaml for filesystem_only_active by extending the existing policy loader, `_finding_defaults()`, `_baseline_finding_sources()`, `_all_active_findings()`, `run_audit()` `summary_counts`, and `_write_markdown_artifact()` family rendering path instead of hard-coding a second policy surface; the policy file documents the `weekly_summary_sections` entry with `id: filesystem_only_inventory`; `ranking_policy.section_order` is extended with `filesystem_only_inventory` immediately after `changed_findings`; a structural test asserts the weekly summary id, ranking id, and `v2.rules` family/rule key agree via an explicit mapping table in docs. Pin the naming contract: family key `filesystem_inventory_findings` derived from policy family `filesystem-inventory`; literal flat YAML key under `v2.rules` is `"filesystem-inventory.filesystem-only-active": {...}` (not nested YAML), so `_finding_defaults()` can resolve it using the current family.rule_id convention; classification `filesystem-only-active`; finding objects must contain classification, finding_key, severity, confidence, paths, recommended_action, summary, headline. `finding_key` for filesystem inventory findings is deterministic: `filesystem-inventory.filesystem-only-active:<repo-relative-posix-path>` for path-specific findings; paths stored in JSON/report artifacts are repo-relative POSIX paths beginning with `.claude/skills/...` so they match the issue body and planning snapshot.  Register `filesystem_inventory_findings` in `_baseline_finding_sources()` alongside current baseline keys (`findings`, `suppressed_findings`, `content_quality_findings`, `grouping_findings`, `size_findings`, `usage_findings`); add only `filesystem_inventory_findings` to `_all_active_findings()` / `active_all_findings`, preserving the current invariant that `suppressed_findings` is excluded from active rollups; add `filesystem_inventory_total: len(filesystem_inventory_findings)` to `summary_counts`; emit top-level JSON array `filesystem_inventory_findings`.
    append inventory_summary to JSON artifact
    append Markdown section "Filesystem-only skill files" listing every filesystem_only_active path regardless of one-time disposition state; this section bypasses `_split_informational_findings()` suppression so `_core`/`_internal` paths appear with `informational: true` rather than disappearing into `suppressed_findings`; insert `filesystem_only_inventory` immediately after `Changed Findings`, matching `ranking_policy.section_order`; existing legacy v2-family literal sections remain outside the ranking-policy order until future policy work moves them; update docs/standards/weekly-skills-audit-policy.md to document the added section, weekly summary key, ranking-policy entry, and mapping to the rule key

    Markdown rendering order is explicit and intentionally not a general reorder feature for #2488: before = New → Changed → Content Quality → Grouping → Oversized → Usage → Follow-up → Unresolved → Suppressed → Errors; after = New → Changed → Filesystem-only → Content Quality → Grouping → Oversized → Usage → Follow-up → Unresolved → Suppressed → Errors.
    mark unresolved filesystem_only_active_count > 0 as high-signal maintenance finding
    unresolved findings are reportable, not a weekly-cron hard failure
    preserve local-only/no-network behavior and write recurring outputs only under the configured output_dir/logs/maintenance/skills-curation/ tree

one-time #2488 disposition closeout:
    implementation re-runs live inventory from the working tree; do not use replayed inventory JSON for closeout authority
    write `docs/reports/issue-2488-skills-disposition.md` with one row per implementation-time active filesystem-only skill plus a separate `issue_body_drift` subsection for any of the original six issue-body paths that vanished before closeout
    disposition values: promote_commit, consolidate_then_commit, redact_then_commit, archive_intentionally, ignore_generated_transient, delete_if_junk
    report columns: path, disposition, rationale, scan/redaction note, final_status, final_path, tracked_after_closeout, personal_authorization_note when applicable
    valuable ignored skills promoted into `.claude/skills/...` must be verified with `git ls-files -- <final_path>` after targeted `git add -f`; personal-* promotions require explicit user authorization, otherwise choose archive/delete/ignore with rationale
    recurring weekly audit must continue to list active filesystem-only files while they remain on disk; it does not consume issue-specific closeout state.

implementation_flow():
    RED baseline proof: before changing duplicate/collision behavior, add fixture `tests/fixtures/skills/issue-2488-archived-duplicate-baseline.json` capturing the current `_archived` duplicate/collision tuple set and summary counts. This is a regression fixture, not branch-history enforcement; implementation review verifies behavior by comparing pre/post tuple sets, avoiding critical-path commit-ancestry tooling.
    RED: add tests for inventory_summary and filesystem_only_active reporting
    GREEN: implement minimal tracked-vs-filesystem inventory helper and output section
    RED/GREEN: add fixture tests for symlink mirror reporting and _archived exclusion
    RED/GREEN: add one-time #2488 disposition report checks for every active filesystem-only skill discovered at implementation time
    verify no unrelated local dirt is staged
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/skills/weekly_skills_audit.py` | Add tracked-vs-filesystem inventory summary, filesystem-only active skill reporting, and mirror/symlink status reporting. Keep legacy duplicate/collision `EXCLUDED_DIRS` behavior unchanged; use a separate active loss-risk filter. Do not add tracked-doc write behavior to this cron-owned script. |
| Modify | `tests/skills/test_weekly_skills_audit.py` | Add TDD coverage for tracked-vs-filesystem inventory via injectable tracked manifest/git adapter seam, active filesystem-only findings, missing tracked active files, active loss-risk filtering, symlink status serialization, and the existing `TestScheduleIntegration.test_validate_schedule_still_passes_with_skills_curation_task` guard if scheduled YAML description changes. |
| Modify | `tests/cron/test_skills_curation.py` | Add/adjust wrapper dry-run coverage proving the existing cron command remains compatible and only invokes weekly audit behavior. |
| Modify | `config/skills/weekly-audit-policy.yaml` | Append `filesystem_only_active` / `filesystem-only-active` to the existing v2 schema using the literal flat key `v2.rules: {"filesystem-inventory.filesystem-only-active": {...}}` (family.rule_id form consumed by `_finding_defaults()`), and `weekly_summary_sections` entry `id: filesystem_only_inventory` plus `ranking_policy.section_order` entry `filesystem_only_inventory` immediately after `changed_findings`; docs define the explicit mapping from weekly-summary id to rule key. Do not create an undocumented top-level `signals` map. Implementation must route this family through the existing policy loader and active-finding/Markdown rendering path so severity/reporting are policy-driven rather than bespoke constants. One-time #2488 disposition report schema lives in the plan/report, not the cron policy. |
| Modify | `docs/standards/weekly-skills-audit-policy.md` | Under its weekly summary / ranking discussion, document new inventory summary schema and where `filesystem_only_active` / `filesystem_only_inventory` lives in the existing policy schema. |
| Modify | `docs/ops/scheduled-tasks.md` | Document only the recurring `skills-curation` v2 scheduled-task contract: local-only/read-only, report-only, and filesystem-only active loss-risk inventory. Do not make this file a manual CLI reference. |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Update only the `skills-curation` description to exact v2 wording while preserving `label`, `schedule`, `command`, `machines`, `requires`, `log`, and `is_claude_task` byte-for-byte: “Weekly skills curation v2 (Monday 04:00): scans .claude/skills/ for duplicate names, leaf collisions, wrapper pairs, and filesystem-only active skill loss-risk inventory. Emits JSON + Markdown artifacts to logs/maintenance/skills-curation/. Local-only/report-only; no network posting. Issues #2281, #2488.” |
| Create | `scripts/skills/issue_2488_disposition_report.py` | Bounded issue-specific helper that re-runs live inventory and renders the one-time disposition report; not a reusable reconciliation framework, not invoked by cron, and removable/replaceable after #2488 closeout. |
| Create | `docs/reports/issue-2488-skills-disposition.md` | One-time tracked disposition report for every active filesystem-only skill discovered at implementation-time. Filename is issue-bound rather than date-bound so reruns do not masquerade under a stale date; the report body records generated_at, implementation commit, path, disposition, rationale, and final tracking/archive/delete state. Use this tracked docs path because `.gitignore` ignores `logs/*`, including `logs/maintenance/...`. |
| Create | `tests/fixtures/skills/issue-2488-archived-duplicate-baseline.json` | Frozen `_archived` duplicate/collision baseline fixture used by regression tests to assert duplicate/collision `{finding_key, severity, paths}` tuple set plus summary counts are unchanged rather than absolute no-findings. This is behavior-regression evidence, not a commit-ancestry gate. |
| Add when disposition requires tracking | active filesystem-only `SKILL.md` paths discovered at implementation time | Promote only those classified as valuable active skills; do not mass-add all 72 filesystem-only files. If a promoted path is ignored by `.gitignore`, use explicit `git add -f <path>` only after scan/disposition evidence is recorded in the report; do not broadly relax `.gitignore` for `digitalmodel/`, `personal-*`, or `memory/`. |
| Document-only by default | `.gitignore` | Do not change by default; record the current ignore rule for any promoted path in the disposition report and use targeted `git add -f` for approved promotions. For the known parent-directory ignore rules, single-line negations are ineffective; modify `.gitignore` only in a separately reviewed follow-up if a full multi-line re-include cascade is justified. |
| Planning lifecycle only | `docs/plans/README.md` | Add/update the #2488 row during plan-gate work; do not treat this as an implementation file. Status should be `plan-review` when the approval gate is posted. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_inventory_summary_distinguishes_tracked_and_filesystem_skills` | canonical counts are explicit and testable without a real git repo | fixture skills + injected tracked manifest/git adapter | JSON summary includes tracked/filesystem totals and active counts |
| `test_inventory_summary_schema_separates_counts_paths_and_mirrors` | JSON shape is deterministic | fixture with filesystem-only and missing-tracked paths | `inventory_summary.counts` has numbers, `inventory_summary.paths` arrays use stable object keys exactly `{path, informational}` with repo-relative POSIX paths, `inventory_summary.mirrors` has symlink targets |
| `test_inventory_summary_reports_filesystem_only_active_skills` | loss-risk skills are visible | fixture active `SKILL.md` absent from tracked manifest | `filesystem_only_active` contains path and count > 0 |
| `test_inventory_summary_reports_missing_tracked_active_skills` | actual tracked skill loss would be detected | tracked manifest contains absent active path | `missing_tracked_active` contains path and count > 0 |
| `test_inventory_summary_excludes_archive_archived_and_checks_diverged_diagnostic_only` | active filter matches #2488 loss-risk semantics and preserves segment-name pruning | fixture `_archive`, `_archived`, a nonzero `_diverged` SKILL.md plus matching tracked path, normal paths, plus `_core`/`_internal` paths | `_archive`/`_archived` are excluded from #2488 tracked_active/filesystem_active/loss-risk counts; `_diverged` is exercised as diagnostic policy/code compatibility drift without adding a recurring summary count; `_core`/`_internal` filesystem-only skills still count as active loss-risk; substring-only names such as `_archived_old/` and `archive_artifacts/` do not over-match |
| `test_inventory_summary_records_provider_skill_mirror_symlinks` | mirror status remains explicit | resolver-injection seam supplies `.codex/skills` and `.gemini/skills` link targets | JSON records links to `../.claude/skills` without platform-dependent symlink setup |
| `test_provider_skill_mirror_symlinks_real_paths` | real repo mirrors are not accidentally materialized as directories | integration test in repo root | `.codex/skills` and `.gemini/skills` are symlinks resolving to `../.claude/skills` |
| `test_weekly_markdown_surfaces_filesystem_only_active_skills` | operator report is high-signal | audit result with active filesystem-only path | Markdown includes `Filesystem-only skill files` section and path |
| `test_filesystem_only_archived_skills_do_not_escalate_active_loss_risk` | archived local files do not create false active alarms | untracked `_archive` and `_archived` SKILL.md files | active loss-risk count remains 0; archived count is reported separately |
| `test_filesystem_only_core_and_internal_skills_are_not_suppressed` | control-plane/internal namespaces are still protected against untracked loss | untracked `_core` and `_internal` SKILL.md files | active filesystem-only count includes these paths and each path object carries `informational: true` |
| `test_weekly_mode_reports_unresolved_without_hard_failure` | recurring cron remains report-only | active filesystem-only skill | weekly result records high-signal unresolved finding and exits successfully |
| `test_git_inventory_failure_is_reported_not_cron_fatal` | weekly cron remains deterministic on Git errors | git_list_fn raises or skills_dir is outside a repo | weekly result records inventory warning and exits successfully |
| `test_policy_yaml_defines_filesystem_only_active_signal` | YAML is authoritative | policy fixture following existing `weekly_summary_sections` and `v2.rules` shape without adding to legacy `signal_vocabulary` | weekly-audit parser, `_finding_defaults()` using `filesystem-inventory.filesystem-only-active`, `_baseline_finding_sources()`, `_all_active_findings()`, `run_audit()` summary counts, and `_write_markdown_artifact()` canonical-section rendering expose the append-only `filesystem_only_active` signal/rule and `filesystem_only_inventory` section without requiring a new top-level `signals` map or hard-coded severity |
| `test_existing_weekly_audit_cli_flags_remain_backward_compatible` | wrapper invariance is protected | argparse invocation with existing flags only | command parses, remains read-only, and does not write tracked docs |
| `test_schedule_description_exact_v2_string` | scheduled task wording is deterministic | schedule-tasks fixture | `skills-curation` description equals the exact v2 string in this plan while label/schedule/command/machines/requires/log/is_claude_task stay byte-for-byte unchanged |
| `test_schedule_task_only_description_changes_raw_yaml_block` | stronger byte-preservation claim is enforced | pre/post skills-curation YAML block fixture | raw normalized block diff shows only the description scalar changed; schedule, command, machines, requires, log, and is_claude_task are byte-for-byte identical |
| `test_filesystem_only_family_participates_in_baseline_and_summary_counts` | family is not new every week and appears in totals | baseline plus current filesystem-only finding | `_baseline_finding_sources()`, carry-forward/is_new logic, and `run_audit()` summary_counts include `filesystem_inventory_findings` |
| `test_all_active_findings_adds_filesystem_without_suppressed` | active rollup invariant is preserved | result containing `suppressed_findings` plus `filesystem_inventory_findings` | `_all_active_findings()` includes filesystem inventory findings but continues excluding suppressed findings |
| `test_policy_schema_keys_stay_consistent_for_filesystem_inventory` | YAML cross-key drift is blocked | policy with mismatched `v2.rules` and `weekly_summary_sections` identifiers | validation/test fails unless the weekly summary section maps to the filesystem-inventory rule consistently |
| `test_weekly_skills_audit_policy_doc_mentions_filesystem_inventory` | docs criterion is enforceable | `docs/standards/weekly-skills-audit-policy.md` | doc contains heading or bullet for `filesystem_only_inventory` and `filesystem-inventory.filesystem-only-active` under the weekly summary / ranking discussion |
| `test_markdown_refactor_preserves_legacy_literal_sections` | section-order refactor does not drop existing output | audit result containing Content Quality, Grouping / Taxonomy Drift, Oversized / Maintainability, Usage / Staleness, and Follow-up Candidates | those legacy literal sections still render in the explicit canonical before/after order: New → Changed → Filesystem-only → Content Quality → Grouping → Oversized → Usage → Follow-up → Unresolved → Suppressed → Errors |
| `test_sparse_checkout_or_partial_git_inventory_is_warned_not_trusted` | successful-but-partial git inventory does not create false loss findings | git adapter reports sparse checkout or unexpectedly low tracked count | weekly report emits inventory warning and does not assert missing-tracked loss without explicit confirmation |
| `test_disposition_report_written_to_tracked_docs_path_with_stable_schema` | one-time closeout report is generated where Git can track it | valid disposition table | `docs/reports/issue-2488-skills-disposition.md` contains path/disposition/reason/final_status/final_path table |
| `test_issue_2488_disposition_helper_invokes_report_end_to_end` | bounded helper has an executable home without nondeterministic live dependencies | `uv run --no-project python scripts/skills/issue_2488_disposition_report.py --output docs/reports/issue-2488-skills-disposition.md --dry-run-fixture <fixture>` | script exists at that path, exits 0, and renders the report schema from fixture/injected inventory without cron involvement |
| `test_disposition_report_verifies_tracked_after_closeout_with_git_adapter` | promotion/consolidation/redaction safety is enforced | injected `git ls-files -- <final_path>` adapter returning tracked/untracked for final paths | report marks `tracked_after_closeout: true` only when the adapter confirms Git tracking; unchecked report fields are rejected |
| `test_planning_snapshot_matches_issue_body_paths_before_closeout` | snapshot authority is reconciled with issue body | issue body path list and `docs/reports/issue-2488-planning-inventory-snapshot.json` fixture | test fails if the snapshot six differ from issue-body six before closeout uses the snapshot as anchor |
| `test_issue_body_drift_uses_planning_inventory_snapshot` | vanished original six paths remain accountable | `docs/reports/issue-2488-planning-inventory-snapshot.json` with one original path absent from live inventory | disposition report renders an `issue_body_drift` row sourced from the reconciled snapshot |
| `test_archived_duplicate_collision_delta_is_zero_vs_prechange_baseline` | `_archived` loss-risk exclusion does not worsen legacy duplicate noise | frozen pre-change `_archived` duplicate/collision baseline captured before code edits + post-change run | duplicate/collision `{finding_key, severity, paths}` tuple set plus summary counts are unchanged; absolute pre-existing findings may remain documented |
| `test_existing_duplicate_collision_fixture_counts_unchanged` | duplicate/collision baseline behavior not broken | frozen existing fixture before and after inventory extension | duplicate/collision summary counts and finding IDs are unchanged |

---

## Acceptance Criteria

- [ ] RED tests are added before implementation for tracked-vs-filesystem inventory and filesystem-only active skill reporting.
- [ ] Weekly audit JSON includes `inventory_summary.counts`, `inventory_summary.paths`, and `inventory_summary.mirrors`; counts are numeric and include exactly `tracked_total`, `tracked_active`, `filesystem_total`, `filesystem_active`, `filesystem_only_total`, `filesystem_only_active`, `missing_tracked_total`, `missing_tracked_active`, `filesystem_only_archived_total` where `tracked_active` and `filesystem_active` exclude exact `_archive` and `_archived` segments only; path arrays for filesystem/missing/archived use `{path, informational}` objects `_core`/`_internal` paths remain active loss-risk but carry `informational: true`, mirror fields are symlink/status strings. Stable field names include `missing_tracked_active` and `filesystem_only_active`. Active filesystem-only files that remain on disk are listed regardless of any one-time closeout disposition; the recurring audit remains a filesystem inventory, not a hidden-state ledger.
- [ ] `config/skills/weekly-audit-policy.yaml` defines `filesystem_only_active` in the existing append-only v2 policy schema (literal flat YAML key `v2.rules: {"filesystem-inventory.filesystem-only-active": {...}}` plus `weekly_summary_sections` entry `id: filesystem_only_inventory`), and tests prove the weekly-audit parser plus `_finding_defaults()`, `_baseline_finding_sources()`, `_all_active_findings()` (adding filesystem findings while still excluding `suppressed_findings`), `run_audit()` `summary_counts`, Markdown rendering, and cross-key validation for `v2.rules`/`weekly_summary_sections` consume those keys rather than hard-coding severity in Python; do not introduce an undocumented top-level `signals` map.
- [ ] Weekly Markdown output includes `filesystem_only_inventory` / “Filesystem-only skill files” listing active filesystem-only skills when any exist, documented in `docs/standards/weekly-skills-audit-policy.md` under a named filesystem inventory bullet/heading; `_write_markdown_artifact()` uses the canonical order New → Changed → Filesystem-only → existing v2-family literal sections → Unresolved → Suppressed → Errors, while high-signal unresolved findings are rendered through the same active-finding shape used by existing families.
- [ ] Active loss-risk filtering for #2488 uses `Path.parts` exact segment equality and excludes archive aliases loaded from `category_alias_families.archive.aliases` (`_archive` and `_archived` today); `_diverged` is diagnostic policy/code compatibility evidence only and is not added as a stable recurring summary count in #2488; `_core` and `_internal` filesystem-only skills remain reportable as active loss-risk; legacy duplicate/collision behavior is not worsened by #2488; implementation must record an `_archived` duplicate/collision baseline fixture before asserting post-change behavior and assert duplicate/collision delta is zero against the `{finding_key, severity, paths}` tuple set, not just counts; absolute pre-existing findings may remain documented rather than changing `EXCLUDED_DIRS`.
- [ ] `.codex/skills` and `.gemini/skills` remain symlink mirrors; no provider duplicate skill trees are created.
- [ ] Every active filesystem-only skill discovered at implementation-time is individually classified in `docs/reports/issue-2488-skills-disposition.md` with disposition, rationale, scan/redaction note when needed, final_status/final_path, and tracked_after_closeout evidence; for promote/consolidate/redact dispositions, `tracked_after_closeout` is derived from `git ls-files -- <final_path>` (or an injected Git adapter in tests), not manually typed. A separate `issue_body_drift` subsection accounts for any of the original six issue-body paths that vanished before closeout; success is not hard-coded to six if additional live filesystem-only active skills appear.
- [ ] Valuable skills are committed/promoted in canonical `.claude/skills/...` paths; every `promote_commit`, `redact_then_commit`, or `consolidate_then_commit` disposition-report entry is verified to appear in tracked active skill files after reconciliation; if a path is gitignored, the disposition report records the ignore rule and the implementation uses targeted `git add -f` only after scan/disposition approval; non-active references are intentionally archived, deleted with reason, or documented as ignored/transient; nothing is mass-added blindly.
- [ ] Closeout report confirms `missing_tracked_active = 0` and assigns terminal disposition for each active filesystem-only skill: promoted/redacted/consolidated entries are tracked active at final_path, archived/deleted entries are absent from active filesystem-only inventory with recorded final_status, and intentionally ignored/generated/transient files remain visible in recurring weekly inventory rather than being hidden.
- [ ] Existing weekly audit behavior remains backward-compatible: pre-existing duplicate/collision tests still pass, and new tests are added for the inventory/disposition extension.
- [ ] `docs/reports/issue-2488-skills-disposition.md` is generated once during implementation closeout at the tracked docs path with stable Markdown schema; the recurring weekly cron does not rewrite tracked docs.
- [ ] `scripts/cron/skills-curation.sh` remains unchanged unless a test proves wrapper changes are necessary; the existing weekly audit CLI flags (`--skills-dir`, `--output-dir`, `--policy`, `--waivers`, `--render-github-payload`) remain backward-compatible, and `tests/cron/test_skills_curation.py` continues to cover dry-run/help/output-root/stale-workspace behavior.
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` description for `skills-curation` is updated from v1 duplicate/leaf/wrapper-only wording to exact v2 wording “Weekly skills curation v2 (Monday 04:00): scans .claude/skills/ for duplicate names, leaf collisions, wrapper pairs, and filesystem-only active skill loss-risk inventory. Emits JSON + Markdown artifacts to logs/maintenance/skills-curation/. Local-only/report-only; no network posting. Issues #2281, #2488.”; `TestScheduleIntegration.test_validate_schedule_still_passes_with_skills_curation_task` asserts the updated text while preserving label/schedule/command/machines/requires/log/is_claude_task byte-for-byte; implement with a targeted text patch/unified diff, not a YAML round-trip dumper.
- [ ] `docs/ops/scheduled-tasks.md` receives only a narrow skills-curation v2 recurring-contract update: add filesystem-only active inventory to the existing local-only/artifact-location description and do not make it the source of truth for one-time #2488 closeout mechanics.
- [ ] Before posting `status:plan-review`, each approval-gate immutable review artifact (created by copying the latest non-empty date-only fanout or fallback-review stdout into a timestamped `*-plan-2488-*.md` file and prepending `Reviewed-Commit: <sha>` and `Plan-SHA256: <sha256>` metadata in that artifact; if a provider is unavailable, create a timestamped `UNAVAILABLE` artifact with the attempted command, stdout/stderr byte counts, error artifact path when present, and the same metadata; historical superseded artifacts are excluded from this gate) is non-empty, contains a parseable `## Verdict` or `## Verdicts` heading, records the reviewed plan commit or plan SHA256, and has no unresolved MAJOR findings from available reviewers before the gate; UNAVAILABLE provider artifacts are allowed when they record the failure reason and remaining available reviewers have no MAJOR findings, consistent with AI review policy; the Adversarial Review Summary cites the artifact path used as evidence.
- [ ] No unrelated local dirt is staged or committed.
- [ ] Final plan comment containing the plan link, scope, review synthesis, and explicit approval request is posted to [#2488](https://github.com/vamseeachanta/workspace-hub/issues/2488), `status:plan-review` is applied and verified on the issue, and implementation remains blocked until the user explicitly approves and the issue is moved to `status:plan-approved`.
- [ ] Implementation records an `_archived` duplicate/collision baseline fixture in `tests/fixtures/skills/issue-2488-archived-duplicate-baseline.json` and asserts the post-change duplicate/collision `{finding_key, severity, paths}` tuple set plus summary counts are unchanged; this is verified by tests rather than commit-history/branch-range enforcement.
- [ ] Sparse-checkout/partial `git ls-files` states are treated conservatively by `detect_git_inventory_trust()`: weekly audit records an inventory warning and avoids authoritative missing-tracked findings when `git ls-files -z -- <skills_dir>` errors, returns zero while the filesystem has skills, `git config --bool core.sparseCheckout` is true and `git sparse-checkout list` does not cover `skills_dir`, or sparse checkout excludes `skills_dir`. The recurring audit does not compare against `docs/reports/issue-2488-planning-inventory-snapshot.json`; that snapshot is path-authoritative for one-time closeout only, not recurring weekly trust logic.
- [ ] Any promotion of a personal skill, defined as a skill whose leaf directory slug matches `.gitignore`-style `personal-*` (including `personal-tax-filing-packet`), is out of scope for #2488 approval unless the user separately authorizes it during implementation after scan/redaction; absent that separate authorization, the implementation must choose archive/ignore/delete with rationale so no plan-time authorization question blocks the gate.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | Prior immutable `20260425T125029Z` evidence was MAJOR; latest mutable diagnostics are non-gate evidence; as of the previous pushed revision they were MAJOR, and earlier attempts produced empty provider stdout with Codex stderr showing CLI sandbox/tooling failure | Latest diagnostic feedback found scope creep and schema-coherence gaps. This revision removes the separate reconciliation framework, pins recurring schema, adds `.gitignore` and planning-snapshot evidence, names the bounded issue-specific disposition helper, and keeps scheduled-task docs focused on the recurring task before the next immutable approval-evidence copy. |
| Codex | Prior immutable `20260425T125029Z` evidence was MAJOR; latest mutable diagnostics are non-gate evidence; as of the previous pushed revision they were MAJOR, and earlier attempts produced empty provider stdout with Codex stderr showing CLI sandbox/tooling failure | Latest diagnostic feedback found scope creep, recurring-schema contradiction, vanished-path vanished-path closeout ambiguity, and scheduled-task doc drift. This revision narrows #2488 to weekly audit reporting plus a bounded one-time disposition helper/report, with added policy-schema consistency tests, before the next immutable approval-evidence copy. |
| Gemini | UNAVAILABLE in immutable evidence `scripts/review/results/20260425T125029Z-plan-2488-gemini.md` | CLI filesystem scan errors; no substantive verdict. Treated as provider-infra N/A, not plan approval. |

**Overall result:** REVISING — latest 2026-04-26 Claude diagnostic is MINOR and Codex diagnostic is MAJOR. Codex blockers are now narrowed to recurring snapshot dependency, deterministic closeout tests, and Git-tracking verification for promoted paths. This revision removes the weekly snapshot dependency, confines snapshot use to one-time path drift, makes closeout tests fixture/adapter-driven, and adds Git adapter verification for `tracked_after_closeout`. Do not move to `status:plan-review` until a subsequent pushed re-review has no unresolved MAJOR findings and fresh evidence is recorded in the gate comment/artifacts. Gemini UNAVAILABLE is recorded as provider-infra N/A for this pass, not a content approval; unavailable-provider artifacts do not by themselves block the gate when remaining required reviewers have no MAJOR findings and the failure is documented. Canonical mutable fanout files and mutable disagreement summaries are diagnostic only; fresh timestamped immutable provider artifacts are authoritative, and if a disagreement summary conflicts with provider artifacts the provider artifact verdicts win while the conflict itself blocks gate until adjudicated. If a provider dispatch produces empty output or CLI sandbox errors, the planning operator uses this order: (1) rerun reduced Claude+Codex fanout once from pushed HEAD, (2) for Codex, retry with artifact-inline/no-tools or GitHub-connector review mode and save that stdout if available, (3) if still unavailable, create an explicit `UNAVAILABLE` artifact/comment with attempted command, stdout/stderr byte counts, and raw-error path or `empty stdout/stderr` for empty runs. Proceed with remaining-provider evidence only when repo AI review policy allows unavailable reviewers to be recorded rather than blocking. Current mutable review files are diagnostic; final gate requires fresh post-patch evidence after the last plan patch.

Revisions made based on review:
- Replaced stale PENDING review summary with latest provider state.
- Added `config/scheduled-tasks/schedule-tasks.yaml` and `tests/cron/test_skills_curation.py` to resource intelligence/evidence.
- Specified that `filesystem_only_active` extends the existing `weekly-audit-policy.yaml` schema append-only rather than introducing an undocumented top-level `signals` map.
- Made scheduled YAML description update mandatory for v2 text while preserving schedule/command/machines/log path.

---

## Risks and Open Questions

- **Risk:** live counts can drift between planning and implementation. Mitigation: implementation must compute live counts at runtime and record the timestamp/source rather than hard-coding counts; the current verified baseline is tracked total `3028`, tracked active `922`, filesystem total `3100`, filesystem active `928`, filesystem-only total `72`, filesystem-only active `6`. The planning-time six are local filesystem evidence and must be recomputed before closeout.
- **Risk:** `logs/maintenance/...` is transient/ignored. Mitigation: recurring generated weekly audit artifacts remain under `logs/maintenance/...` and operators see filesystem-only listings in local untracked cron output; durable one-time disposition state lives in `docs/reports/issue-2488-skills-disposition.md`; the recurring report remains local-only/read-only.
- **Risk:** committing untracked active skills without content review could preserve low-quality, generated, PII, or secret-bearing artifacts. Mitigation: require per-skill disposition, scan/redaction note when applicable, final_status/final_path, and rationale before any `git add`.
- **Risk:** adding filesystem-only findings to the same duplicate/collision classification pipeline could create noisy false positives. Mitigation: use a separate `filesystem_inventory_findings` family and `filesystem_only_inventory` weekly section governed by append-only entries in the existing `config/skills/weekly-audit-policy.yaml` schema, not a second top-level policy surface.
- **Risk:** changing `EXCLUDED_DIRS` would alter legacy duplicate/collision audit semantics and expose existing policy/code drift (`weekly-audit-policy.yaml` treats `_archive`/`_archived` as aliases while code excludes `_archive`/`_diverged`). Mitigation: do not extend `EXCLUDED_DIRS`; implement a separate `Path.parts` active loss-risk filter that excludes archive aliases loaded from `category_alias_families.archive.aliases` for #2488 loss-risk counts only; keep `_diverged` as diagnostic policy/code compatibility evidence, not a recurring summary-count field; keep the policy/code drift diagnostic local to tests unless a future named follow-up adds a recurring consumer; until then, the #2488 implementation must not change legacy `EXCLUDED_DIRS`.
- **Decision:** v2 rule/weekly-summary ranking lives append-only in the existing `config/skills/weekly-audit-policy.yaml` schema; the one-time implementation triage/disposition report path is `docs/reports/issue-2488-skills-disposition.md`; recurring scheduled audit artifacts remain under `logs/maintenance/` only and must not mutate tracked docs.
- **Decision:** `scripts/cron/skills-curation.sh` should remain unchanged unless implementation tests prove otherwise; wrapper invariance is part of the implementation acceptance criteria.
- **Decision:** future ignored skills under broad ignore prefixes remain visible through the weekly filesystem-only signal; for approved promoted skills, implementation may use targeted `git add -f`, and must not broadly unignore private/vendor/generated namespaces.

---

## Complexity: T3

**T3** — moderate multi-file maintenance/audit enhancement with tests, one existing script, likely one existing test module, docs/policy updates, and a controlled disposition pass over locally discovered skill files, explicit ignored-path tracking evidence, and operator-facing docs. It does not require broad ecosystem rewrite or multi-repo architecture changes.
