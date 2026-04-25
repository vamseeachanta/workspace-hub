# Plan for #2488: reconcile untracked active skill files before loss

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2488
> **Review artifacts:** scripts/review/results/2026-04-25-plan-2488-claude.md | scripts/review/results/2026-04-25-plan-2488-codex.md | scripts/review/results/2026-04-25-plan-2488-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/weekly_skills_audit.py` — deterministic weekly skill audit entrypoint already exists from #2281/#2486. It scans `.claude/skills`, excludes `_archive` and `_diverged`, classifies duplicate canonical names / leaf collisions / wrapper pairs, applies baseline and waiver logic, and emits JSON + Markdown artifacts. Gap: it does not currently model tracked-vs-filesystem inventory or filesystem-only active skills as a first-class high-signal finding.
- Found: `scripts/cron/skills-curation.sh` — existing cron wrapper runs `uv run --no-project python scripts/skills/weekly_skills_audit.py` and supports `SKILLS_AUDIT_OUTPUT_ROOT` for redirectable test output. #2488 must preserve this local-only deterministic wrapper and avoid adding network posting.
- Found: `tests/skills/test_weekly_skills_audit.py` — existing pytest coverage for inventory scope, classification buckets, output schema, baseline delta, waiver handling, and read-only behavior. Gap: no coverage currently asserts that active filesystem-only `SKILL.md` files are detected/reported distinctly from tracked active skills.
- Found: current live inventory re-check on 2026-04-25 from repo root: tracked total `3028`, tracked active `922` when excluding `_archive`, `_archived`, and `_diverged`, filesystem total `3100`, filesystem active `928`, untracked/filesystem-only total `72`, untracked/filesystem-only active `6`, missing tracked active from filesystem `0`. This matches the issue-body conclusion: no tracked active skills are missing, but six active filesystem-only skills are at loss risk. Note: excluding only `_archive` and `_diverged` yields tracked active `928`; adding `_archived` excludes the six tracked `email/_archived` skills and yields the stricter active baseline `922`.
- Found: mirror state remains canonical and must be preserved: `.codex/skills -> ../.claude/skills`; `.gemini/skills -> ../.claude/skills`. #2488 must not duplicate provider skill trees.

### Standards
| Standard | Status | Source |
|---|---|---|
| Mandatory issue planning gate | required | `AGENTS.md`, `docs/plans/README.md`, `docs/plans/_template-issue-plan.md` |
| TDD before implementation | required | `AGENTS.md` |
| Weekly skills audit policy | active / relevant | `config/skills/weekly-audit-policy.yaml`, `docs/standards/weekly-skills-audit-policy.md` |
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
- EXISTS: `scripts/cron/skills-curation.sh` — lines 41-47 construct `uv run --no-project python "$AUDIT_SCRIPT"` and forward `SKILLS_AUDIT_OUTPUT_ROOT` to `--output-dir`.
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
    return not any(f'/{x}/' in p for x in ('_archive','_archived','_diverged'))
print('tracked_total', len(tracked))
print('tracked_active', sum(active(p) for p in tracked))
print('fs_total', len(fs))
print('fs_active', sum(active(p) for p in fs))
print('filesystem_only_total', len(set(fs) - set(tracked)))
print('filesystem_only_active', sum(active(p) for p in set(fs) - set(tracked)))
print('missing_active_tracked_from_fs', sum(active(p) and p not in set(fs) for p in tracked))
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
tracked_active 922  # strict active filter excludes _archive, _archived, _diverged
fs_total 3100
fs_active 928       # strict active filter excludes _archive, _archived, _diverged
filesystem_only_total 72
filesystem_only_active 6
missing_active_tracked_from_fs 0
UNTRACKED_ACTIVE .claude/skills/business_admin/personal-tax-filing-packet/SKILL.md
UNTRACKED_ACTIVE .claude/skills/digitalmodel/blender-worktree-test-hardening/SKILL.md
UNTRACKED_ACTIVE .claude/skills/digitalmodel/digitalmodel-worktree-test-execution-with-shared-venv/SKILL.md
UNTRACKED_ACTIVE .claude/skills/digitalmodel/library-evaluation-integration/SKILL.md
UNTRACKED_ACTIVE .claude/skills/digitalmodel/orcaflex-reporting-fixture-proof-pattern/SKILL.md
UNTRACKED_ACTIVE .claude/skills/memory/hermes-memory-bridge/SKILL.md
codex_link ../.claude/skills
gemini_link ../.claude/skills
```

<!-- Verification: distinct sources >= 3. Current count: 8 -->

### Tentative disposition table for the known active filesystem-only skills

These are plan-review dispositions for the six currently known active filesystem-only skills. Implementation must recompute the live list and apply the same decision rules to every active filesystem-only skill found at that time.

| Path | Tentative disposition | Rationale |
|---|---|---|
| `.claude/skills/business_admin/personal-tax-filing-packet/SKILL.md` | `promote_commit` after secret/content scan | Reusable tax-filing workflow skill with no raw taxpayer data in inspected frontmatter/first section; belongs in `business_admin`. |
| `.claude/skills/digitalmodel/blender-worktree-test-hardening/SKILL.md` | `promote_commit` after content overlap check | Captures a recurring digitalmodel worktree/Blender test-hardening failure mode and concrete recovery commands. |
| `.claude/skills/digitalmodel/digitalmodel-worktree-test-execution-with-shared-venv/SKILL.md` | `promote_commit` or consolidate with Blender worktree skill if overlap is judged excessive | Valuable shared-venv workaround for digitalmodel worktrees; may overlap with the Blender-specific skill, so implementation should decide preserve-separate vs consolidate, with rationale. |
| `.claude/skills/digitalmodel/library-evaluation-integration/SKILL.md` | `promote_commit` after content overlap check | Reusable scientific-library evaluation/integration-test pattern for digitalmodel. |
| `.claude/skills/digitalmodel/orcaflex-reporting-fixture-proof-pattern/SKILL.md` | `promote_commit` after content overlap check | Reusable OrcaFlex reporting fixture/snapshot proof pattern aligned with active digitalmodel work. |
| `.claude/skills/memory/hermes-memory-bridge/SKILL.md` | `promote_commit` after secret/content scan and bridge-state accuracy check | Durable cross-machine memory-bridge architecture/workflow; should be tracked if still accurate. |

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
    else call git_list_fn or default git ls-files under .claude/skills ending /SKILL.md
    filesystem_skill_paths = all SKILL.md under .claude/skills
    active_filter(path): preserve segment-name pruning; treat any path segment exactly equal to _archive, _archived, _diverged, _core, or _internal as non-operational for loss-risk counts
    audit_inventory_filter(path): keep existing EXCLUDED_DIRS behavior for duplicate/collision pipeline; do not add _archived to EXCLUDED_DIRS unless a separate review approves changing legacy audit semantics
    return counts and path sets:
        tracked_total, tracked_active
        filesystem_total, filesystem_active
        filesystem_only_total, filesystem_only_active
        missing_tracked_total, missing_tracked_active
        filesystem_only_archived_total, filesystem_only_informational_total
        codex_skills_link, gemini_skills_link

function classify_filesystem_only_skill(path):
    read frontmatter and first content section
    inspect git history using deterministic keys: repo-relative path first, then frontmatter name, then leaf slug
    search canonical active skills for same frontmatter name, same leaf slug, or documented replacement
    assign disposition:
        promote_commit if valuable, unique, reusable, and not generated junk
        archive_intentionally if useful reference but not active routing material
        ignore_generated_transient if tool-generated or machine-local with policy rationale
        delete_if_junk only when provably useless and safe
    require a reason for every disposition

function run_weekly_audit_extension():
    run existing weekly audit duplicate/collision logic with unchanged EXCLUDED_DIRS semantics
    compute separate inventory_summary using the stricter operational-active filter
    load config/skills/filesystem-only-skill-dispositions.yaml if present
    append inventory_summary to JSON artifact
    append Markdown section "Filesystem-only skill files"
    mark undispositioned filesystem_only_active_count > 0 as high-signal maintenance finding
    list archived-only/informational filesystem-only files as informational, not active loss-risk
    preserve local-only/no-network behavior

function validate_and_render_dispositions(disposition_yaml):
    require one entry per active filesystem-only skill discovered at implementation time
    require fields: path, disposition, reason, reviewed_at, reviewed_inventory_sha256
    allowed dispositions: promote_commit, archive_intentionally, ignore_generated_transient, delete_if_junk, consolidate_then_commit
    write durable Markdown report to docs/reports/2026-04-25-skills-disposition-2488.md
    future audit runs read the YAML ledger and mark matching reviewed_inventory_sha256/path entries as dispositioned

implementation_flow():
    RED: add tests for inventory_summary and filesystem_only_active reporting
    GREEN: implement minimal tracked-vs-filesystem inventory helper and output section
    RED/GREEN: add fixture tests for symlink mirror reporting and _archived exclusion
    RED/GREEN: add disposition ledger/report generation for every active filesystem-only skill discovered at implementation time
    verify no unrelated local dirt is staged
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/skills/weekly_skills_audit.py` | Add tracked-vs-filesystem inventory summary, filesystem-only active skill reporting, disposition-ledger loading/validation/rendering helpers, and mirror/symlink status reporting. Keep legacy duplicate/collision `EXCLUDED_DIRS` behavior unchanged; use a separate operational-active filter for loss-risk counts. |
| Modify | `tests/skills/test_weekly_skills_audit.py` | Add TDD coverage for tracked-vs-filesystem inventory via injectable tracked manifest/git adapter seam, active filesystem-only findings, missing tracked active files, operational-active filtering, disposition ledger/report schema, and symlink status serialization. |
| Create | `config/skills/filesystem-only-skill-dispositions.yaml` | Machine-readable disposition ledger for active filesystem-only skills; gives future audit runs a durable resolved/ignored/consolidated source of truth without overloading duplicate-skill buckets. |
| Maybe modify | `docs/standards/weekly-skills-audit-policy.md` | Document new inventory summary fields and disposition vocabulary if not fully self-documented in the YAML ledger/report. |
| Maybe modify | `docs/ops/scheduled-tasks.md` | Update only if the weekly artifact contract or operator-facing output path changes. |
| Create | `docs/reports/2026-04-25-skills-disposition-2488.md` | Durable, tracked disposition report for every active filesystem-only skill discovered at implementation-time. Use this tracked docs path because `.gitignore` ignores `logs/*`, including `logs/maintenance/...`. |
| Maybe add/track | active filesystem-only `SKILL.md` paths discovered at implementation time | Promote only those classified as valuable active skills; do not mass-add all 72 filesystem-only files. |
| Update | `docs/plans/README.md` | Add this plan to the plan index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_inventory_summary_distinguishes_tracked_and_filesystem_skills` | canonical counts are explicit and testable without a real git repo | fixture skills + injected tracked manifest/git adapter | JSON summary includes tracked/filesystem totals and active counts |
| `test_inventory_summary_reports_filesystem_only_active_skills` | loss-risk skills are visible | fixture active `SKILL.md` absent from tracked manifest | `filesystem_only_active` contains path and count > 0 |
| `test_inventory_summary_reports_missing_tracked_active_skills` | actual tracked skill loss would be detected | tracked manifest contains absent active path | `missing_tracked_active` contains path and count > 0 |
| `test_inventory_summary_excludes_archive_archived_diverged_core_and_internal_from_operational_loss_risk` | operational-active filter matches loss-risk semantics and preserves segment-name pruning | fixture `_archive`, `_archived`, `_diverged`, `_core`, `_internal`, normal paths | only normal path counts as operational active; substring-only names do not over-match |
| `test_inventory_summary_records_provider_skill_mirror_symlinks` | mirror status remains explicit | resolver-injection seam supplies `.codex/skills` and `.gemini/skills` link targets | JSON records links to `../.claude/skills` without platform-dependent symlink setup |
| `test_weekly_markdown_surfaces_filesystem_only_active_skills` | operator report is high-signal | audit result with active filesystem-only path | Markdown includes `Filesystem-only active skills` section and path |
| `test_filesystem_only_archived_or_informational_skills_do_not_escalate_active_loss_risk` | archived/informational local files do not create false active alarms | untracked `_archive`, `_archived`, `_core`, `_internal` SKILL.md files | operational active loss-risk count remains 0; archived/informational counts are reported separately |
| `test_disposition_ledger_requires_entry_and_reason_per_active_filesystem_only_skill` | one-time triage cannot silently skip a skill | active filesystem-only fixture with one missing ledger entry/reason | validation fails with actionable error |
| `test_disposition_ledger_accepts_only_known_disposition_values` | dispositions are machine-checkable | invalid disposition string | validation fails |
| `test_disposition_report_written_to_tracked_docs_path_with_stable_schema` | durable report is generated where Git can track it | valid disposition ledger | `docs/reports/2026-04-25-skills-disposition-2488.md` contains path/disposition/reason/inventory hash table |
| `test_disposition_ledger_suppresses_previously_reviewed_matching_paths` | weekly audit does not re-flag resolved active filesystem-only skills forever | inventory + matching disposition ledger with reviewed_inventory_sha256 | matching paths marked dispositioned/resolved; changed hash/path reopens review |
| `test_existing_weekly_audit_behavior_remains_backward_compatible` | duplicate/collision baseline behavior not broken | existing fixture tests | existing tests still pass |

---

## Acceptance Criteria

- [ ] RED tests are added before implementation for tracked-vs-filesystem inventory and filesystem-only active skill reporting.
- [ ] Weekly audit JSON includes an `inventory_summary` stable object with tracked, filesystem, filesystem-only, missing-tracked, operational-active, archived, informational, and symlink/mirror counts, using consistent field names: `missing_tracked_active` and `filesystem_only_active`.
- [ ] Weekly Markdown output includes a high-signal section listing active filesystem-only skills when any exist.
- [ ] Operational loss-risk filtering excludes exact path segments `_archive`, `_archived`, `_diverged`, `_core`, and `_internal`; the legacy duplicate/collision audit keeps existing `EXCLUDED_DIRS` semantics unless separately reviewed.
- [ ] `.codex/skills` and `.gemini/skills` remain symlink mirrors; no provider duplicate skill trees are created.
- [ ] Every active filesystem-only skill discovered at the implementation-time audit pass is individually dispositioned in `config/skills/filesystem-only-skill-dispositions.yaml` with disposition, reason, reviewer/date, and inventory hash; the current known count is six, but success is not hard-coded to six if live state changes.
- [ ] Valuable skills are committed/promoted in canonical `.claude/skills/...` paths; non-active references are intentionally archived or documented as ignored/transient; nothing is mass-added blindly.
- [ ] Validation confirms `missing_tracked_active = 0` after reconciliation.
- [ ] Existing weekly audit behavior remains backward-compatible: pre-existing duplicate/collision tests still pass, and new tests are added for the inventory/disposition extension.
- [ ] `docs/reports/2026-04-25-skills-disposition-2488.md` is generated at the tracked docs path with stable Markdown schema and matches the YAML disposition ledger.
- [ ] `scripts/cron/skills-curation.sh` remains unchanged unless a test proves wrapper changes are necessary; the new report/ledger behavior is implemented inside the audit script and docs/config artifacts.
- [ ] No unrelated local dirt is staged or committed.
- [ ] Plan review artifacts are posted before implementation begins.

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

- **Risk:** live counts can drift between planning and implementation. Mitigation: implementation must compute live counts at runtime and record the timestamp/source rather than hard-coding counts; the current verified baseline is tracked total `3028`, tracked active `922`, filesystem total `3100`, filesystem active `928`, filesystem-only total `72`, filesystem-only active `6`.
- **Risk:** `logs/maintenance/...` is transient/ignored. Mitigation: the durable disposition ledger must be `docs/reports/2026-04-25-skills-disposition-2488.md`; generated weekly audit artifacts may still live under `logs/maintenance/...` as transient outputs.
- **Risk:** committing untracked active skills without content review could preserve low-quality or generated artifacts. Mitigation: require per-skill disposition + rationale before any `git add`.
- **Risk:** adding filesystem-only findings to the same duplicate/collision classification pipeline could create noisy false positives. Mitigation: prefer an operational inventory section unless policy changes require a new bucket.
- **Risk:** changing `EXCLUDED_DIRS` would alter legacy duplicate/collision audit semantics. Mitigation: do not extend `EXCLUDED_DIRS`; implement a separate operational-active filter for loss-risk counts that excludes exact path segments `_archive`, `_archived`, `_diverged`, `_core`, and `_internal`.
- **Decision:** durable disposition state lives in `config/skills/filesystem-only-skill-dispositions.yaml`; the human-readable one-time triage report path is `docs/reports/2026-04-25-skills-disposition-2488.md`; `logs/maintenance/` remains only for generated transient audit artifacts.
- **Decision:** `scripts/cron/skills-curation.sh` should remain unchanged unless implementation tests prove otherwise; wrapper invariance is part of the implementation acceptance criteria.

---

## Complexity: T2

**T2** — bounded multi-file maintenance/audit enhancement with tests, one existing script, likely one existing test module, optional docs/policy updates, and a controlled disposition pass over six local skill files. It does not require broad ecosystem rewrite or multi-repo architecture changes.
