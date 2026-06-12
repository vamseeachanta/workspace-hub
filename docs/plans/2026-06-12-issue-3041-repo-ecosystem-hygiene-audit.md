# Plan for #3041: daily read-only repo ecosystem hygiene audit

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-06-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3041
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** single-lane implementation after approval; parallel-readonly for planning/review evidence only
> **Review artifacts:** external gate evidence generated under `scripts/review/results/` by `plan-review-fanout.sh`; exact paths will be cited in the GitHub issue comment after a no-MAJOR run.

---

## Resource Intelligence Summary

### Existing Repo Code

- Found: `config/scheduled-tasks/schedule-tasks.yaml` defines `cron-health` at `45 5 * * *` and `repository-sync` every 4 hours. `repository-sync` is a mutating task by description: "Pull from remotes, push derived state; every 4 hours."
- Found: `scripts/monitoring/cron-health-check.sh` reads `config/scheduled-tasks/schedule-tasks.yaml`, resolves each task's `log:` pattern, flags stale/missing/erroring logs, and writes JSON under `.claude/state/cron-health/`.
- Found: `scripts/monitoring/cron-health-check.sh` currently uses a fixed 25-hour daily freshness threshold. For a 05:35 daily task checked at 05:45, one missed day can be only about 24h10m old and therefore not stale; this plan will add a per-task stale threshold for `repo-ecosystem-hygiene`.
- Found: `scripts/cron/setup-cron.sh` is the canonical crontab installer. It reads `config/scheduled-tasks/schedule-tasks.yaml`, supports `--dry-run`, and disables unsafe `--replace`.
- Found: `scripts/cron/setup-cron.sh` filters tasks by the live `hostname -s`; cross-alias dry-run evidence must be gathered on the target host, while host-independent coverage belongs in `validate-schedule.py`.
- Found: `scripts/cron/setup-cron.sh` installs `task.command` only, while `cron-health` scans `task.log`; the new scheduled task must make its command redirect to the same path family declared in `log:`.
- Found: `scripts/repository_sync-auto` mutates repo state in live mode: `git add -u`, `git commit`, `git pull --ff-only`, and `git push`.
- Found: `repository-sync` log freshness is not a reliable input for this audit because `schedule-tasks.yaml` advertises `logs/repository-sync-*.log` while the cron wrapper may redirect to `logs/quality/cron-wrapper.log` through `$LOG`. This audit will not infer repository-sync freshness in v1; cron-health remains responsible for scheduled-task log freshness.
- Found: `scripts/cron/daily-cleanup.sh` already audits the repo ecosystem, but it also mutates state in live mode: `git worktree prune`, local branch deletion, fast-forward merge/push/delete, stale lock removal, and cleanup-trash deletion. This plan will not reuse `daily-cleanup.sh --dry-run` because some probes in that script bypass the `run()` dry-run wrapper and can still perform network or cleanup operations.
- Found: `daily-cleanup` is not a `schedule-tasks.yaml` task, so cron-health cannot report a `daily-cleanup` task status. The audit will link it as non-scheduled issue/runbook context (`#2752`, `#2652`) rather than pretending cron-health owns it.
- Found: no durable local daily-cleanup state artifact is available; `daily-cleanup.sh` writes a temp report and posts to #2652 with the marker `_Posted by daily-cleanup.sh — workspace-hub#2752_`. V1 will use a read-only `gh` query against #2652 comments as the concrete daily-cleanup health signal.
- Found: the current `daily-cleanup.sh` path model checks sibling repos under `$WORKSPACE_ROOT/$repo`, while this machine's registry defines sibling checkouts under `tier1_repo_root`. A fresh #2652 marker is therefore a freshness signal only; V1 must report `daily-cleanup` as `UNKNOWN`/`known_path_model_mismatch` until that routine is fixed or a semantically valid local state artifact exists.
- Found: `daily-today` is the scheduled daily productivity/report task (`logs/daily/cron.log`), so cron-health can report that task status for the #2652 daily-readiness/reporting link.
- Found: `scripts/cron/daily-cleanup.sh` defines expected local root infrastructure names (`.pnpm-store`, `.Trash-1000`, `.cleanup-lock`, `.cleanup-trash`, `.daily-cleanup-lock`); the new audit will combine those with registry `infrastructure_dirs` for first-level residue allowlisting.
- Found: live `/mnt/local-analysis` currently has recurring non-registry root entries. The first implementation will allowlist only registry `infrastructure_dirs` plus deterministic local runtime names/patterns (`.agents`, `.claude`, `.codex`, `.planning`, session-summary files, and preserved/codex-review evidence files). Historical registry entries such as `acma-projects` are classified by the historical handler first; other first-level non-git root entries, including current names such as `2802-pilot-evidence` and `acma-projects-freeze-work`, remain WARN with finding `registry_disposition_required` until the registry gives them an explicit disposition.
- Found: `scripts/lib/tier1-repos.sh` reads `config/tier1-python-repos.txt` as the single source of truth for tier-1 Python tooling jobs only. The new audit will not use that list for repo presence scope because it explicitly excludes non-Python required repos such as `llm-wiki`.
- Found: `config/workstations/registry.yaml` is the source of truth for live workstation repo layout. `dev-primary` / `ace-linux-1` uses `tier1_repo_root: /mnt/local-analysis`, `workspace_root: /mnt/local-analysis/workspace-hub`, `repo_layout: sibling`, and `tier1_baseline.required: [workspace-hub, digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold]`.
- Gap: no `scripts/cron/repo-ecosystem-hygiene-audit.sh` and no `.claude/state/repo-ecosystem-hygiene/` local state/report directory exist.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue planning gate | active | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Scheduled task source of truth | active | `scripts/cron/setup-cron.sh`, `config/scheduled-tasks/schedule-tasks.yaml`, `docs/ops/scheduled-tasks.md` |
| Cron health evidence path | active | `scripts/monitoring/cron-health-check.sh` |
| Control-plane contract | active | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Path handling | active | `.claude/rules/coding-style.md` |
| Pre-completion cleanup audit | active | `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md` |

### LLM Wiki Pages Consulted

- N/A - this issue does not touch wiki content or domain knowledge pages.

### Documents Consulted

- GitHub issue #3041 - requests a daily read-only production-host audit that catches staleness before manual cleanup becomes expensive.
- GitHub issue #2572 - persistent recurring `/repo-sync` watcher. Its latest comments repeatedly identify the same standing environment gap: the cloud/container routine cannot access `/mnt/local-analysis/` or sibling repos.
- GitHub issue #2752 - closed issue that delivered the existing Hermes `daily-cleanup` cron with mutating safe-disposition behavior.
- GitHub issue #2652 - existing daily repo readiness tracker and report sink.
- `docs/ops/scheduled-tasks.md` - documents `config/scheduled-tasks/schedule-tasks.yaml` as source of truth, `scripts/cron/setup-cron.sh` as installer, and `scripts/cron/validate-schedule.py` as validator.
- `config/workstations/registry.yaml` - defines current-machine checkout layout and required/optional/non-tier1 repo classes; this outranks the Python-tooling-only `config/tier1-python-repos.txt` for repo presence audit scope.
- `config/workstations/registry.yaml` - defines placement/severity policies: required absence is `error`; optional/non-tier1 absence, dirty, ahead, and behind drift are `warning`; unknown sibling git is `warning`.
- `.claude/skills/workspace-hub/repo-sync/SKILL.md` - documents repo-sync recovery and branch/worktree safety constraints, including no force-push/reset and careful handling of dirty/diverged repos.
- `.claude/skills/workspace-hub/worktree-branch-sync-hygiene/SKILL.md` - documents worktree/branch cleanup hazards and the need to separate remote landed state from local checkout cleanliness.

### Gaps Identified

- A read-only daily audit script must be built from scratch.
- A stable local-only Markdown + JSON report shape must be defined for repo ecosystem hygiene.
- Generated daily Markdown/JSON reports must stay local-only and ignored because the cron task is explicitly non-mutating and must not dirty or auto-commit tracked `docs/reports` files. This is a deliberate narrowing of the issue's example report paths, not an omission.
- `config/scheduled-tasks/schedule-tasks.yaml` must add a log-backed task entry before `cron-health` so stale/missing/error execution states are visible; repo hygiene WARN/ERROR findings remain in the audit artifacts and evidence line.
- Tests must prove read-only behavior with an explicit command allowlist wrapper and a secondary mutating-token guard.
- A small operator skill or runbook update must explain how to interpret findings and route remediation without turning the audit into an auto-cleaner.

### Evidence

**Issue statuses** (verified 2026-06-12T11:43:00Z via `gh issue view`):

- `#3041` - OPEN - `feat(automation): daily read-only repo ecosystem hygiene audit` - labels include `status:needs-plan` and `lane:claude`.
- `#2572` - OPEN - `Routine: /repo-sync + /mnt/local-analysis cleanup audit (every 2 days)`.
- `#2752` - CLOSED - `feat(automation): nightly 23:00 cleanup cron across workspace-hub + tier-1 repos`.
- `#2652` - OPEN - `Daily repo readiness tracker`.

**File existence** (verified 2026-06-12T11:44:00Z via `ls -la`):

```text
ls: cannot access 'scripts/cron/repo-ecosystem-hygiene-audit.sh': No such file or directory
ls: cannot access '.claude/state/repo-ecosystem-hygiene': No such file or directory
```

**Line excerpts**:

`config/scheduled-tasks/schedule-tasks.yaml:500-558`:

```text
500  - id: cron-health
502    schedule: "45 5 * * *"
506    command: >-
507      cd $WORKSPACE_HUB &&
508      bash scripts/monitoring/cron-health-check.sh
510    log: logs/quality/cron-health-*.log
512    description: Daily 05:45 UTC health check of all cron jobs; reads schedule-tasks.yaml, flags stale/missing/erroring runs, writes JSON report to .claude/state/cron-health/.
545  - id: repository-sync
547    schedule: "0 */4 * * *"
551    command: >-
552      cd $WORKSPACE_HUB &&
553      bash scripts/cron-repository-sync.sh
555    log: logs/repository-sync-*.log
557    description: Pull from remotes, push derived state; every 4 hours.
```

`scripts/repository_sync-auto:134-157`:

```text
134  if _quick_status_dirty; then
136      git add -u 2>/dev/null
139      if git commit -m "chore(sync): auto-sync $date_str" 2>/dev/null; then
148  if ! _safe_ff_only_pull; then
156  elif push_out=$(git push 2>&1); then
```

`scripts/cron/daily-cleanup.sh:124-183` and `249-264`:

```text
124  # --- 1. Orphan worktree prune ---
126      PRUNE_OUT=$(git_q worktree prune --expire=7.days --verbose 2>&1)
132  # --- 2. Merged-branch delete (safe pattern only) ---
142            if run "delete merged branch $repo/$branch" git_q branch -d "$branch" 2>/dev/null; then
153  # --- 3. Auto-merge feature branches matching safe patterns ---
181      if run "ff-merge $repo/$branch ($ahead commits) into main" \
182         bash -c "git_q checkout main && git_q merge --ff-only '$branch' && git_q push origin main && git_q branch -d '$branch' && git_q push origin --delete '$branch'"; then
249  # === 8. Stale lock/trash dir GC ===
255      run "remove stale cleanup-lock (age=${LOCK_AGE}s)" rm -f "$CLEANUP_LOCK"
263      run "remove $OLD_COUNT cleanup-trash dirs older than 7d" find "$CLEANUP_TRASH" -maxdepth 1 -mindepth 1 -mtime +7 -type d -exec rm -rf {} +
```

`scripts/monitoring/cron-health-check.sh:51-90`:

```text
51  # Parse schedule YAML
63  for task in data.get('tasks', []):
68      log_pattern = task.get('log', '')
82  ERROR_PATTERNS=(
84      "(^|[[:space:]])ERROR:"
85      "fatal:"
86      "ModuleNotFoundError"
87      "Permission denied"
88      "Traceback"
89      "command not found"
90      "No such file or directory"
```

`scripts/lib/tier1-repos.sh:1-4`:

```text
1  #!/usr/bin/env bash
2  # Single source of truth reader for the tier-1 Python repo list (#3023).
3  # Source this file to populate the TIER1_PYTHON_REPOS array from
4  # config/tier1-python-repos.txt — do NOT hardcode the repo list anywhere else.
```

`config/workstations/registry.yaml:12-14` and `65-74`:

```text
12      workspace_root: /mnt/local-analysis/workspace-hub
13      tier1_repo_root: /mnt/local-analysis
14      repo_layout: sibling
65      tier1_baseline:
70        repo_root: /mnt/local-analysis
71        workspace_root: /mnt/local-analysis/workspace-hub
72        layout: sibling
73        required: [workspace-hub, digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold]
74        optional: [aceengineer-website, aceengineer-strategy]
```

**Live layout probe** (verified 2026-06-12T11:49:00Z):

```text
$ ls -ld /mnt/local-analysis /mnt/local-analysis/workspace-hub /mnt/local-analysis/digitalmodel /mnt/local-analysis/workspace-hub/digitalmodel
ls: cannot access '/mnt/local-analysis/workspace-hub/digitalmodel': No such file or directory
drwxrwxrwx ... /mnt/local-analysis
drwxrwxrwx ... /mnt/local-analysis/digitalmodel
drwxrwxrwx ... /mnt/local-analysis/workspace-hub
```

`docs/ops/scheduled-tasks.md:1-5`:

```text
1  # Scheduled Tasks Inventory
3  > Source of truth: `config/scheduled-tasks/schedule-tasks.yaml`
4  > Installer: `scripts/cron/setup-cron.sh`
5  > Validator: `scripts/cron/validate-schedule.py`
```

**Reproduction proofs**:

N/A - governance/automation issue; no runtime failure is alleged. The plan verifies current scheduler and script state instead.

<!-- Verification: 12 distinct sources consulted. Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-12-issue-3041-repo-ecosystem-hygiene-audit.md` |
| Audit script | `scripts/cron/repo-ecosystem-hygiene-audit.sh` |
| Unit/contract tests | `scripts/cron/tests/test_repo_ecosystem_hygiene_audit.py` |
| Schedule validation test extension | `scripts/cron/tests/test_validate_schedule.py` |
| Latest local report | `.claude/state/repo-ecosystem-hygiene/latest.md` |
| Dated local report | `.claude/state/repo-ecosystem-hygiene/YYYY-MM-DD.md` |
| JSON local state output | `.claude/state/repo-ecosystem-hygiene/YYYY-MM-DD.json` |
| Schedule entry | `config/scheduled-tasks/schedule-tasks.yaml` |
| Operator docs | `docs/ops/scheduled-tasks.md` |
| Operator skill | `.claude/skills/workspace-hub/repo-ecosystem-hygiene/SKILL.md` |
| Plan review gate evidence | External files under `scripts/review/results/` cited in the GitHub issue comment; intentionally not hard-coded here to avoid self-referential zero-byte reads while fanout is running |

---

## Deliverable

A daily, read-only repo ecosystem hygiene audit will run on the production-host checkout, write ignored local Markdown/JSON drift artifacts and cron logs, and surface its scheduled-task execution freshness/missing/error state through the existing cron-health framework without mutating any repository or filesystem cleanup state. Repo hygiene WARN/ERROR findings will remain in the audit artifacts and one-line evidence record rather than being reclassified as cron-health failures.

---

## Pseudocode

```text
function main():
    resolve REPO_ROOT from the script location, not from git:
        scripts/cron/repo-ecosystem-hygiene-audit.sh -> repo root is two directories up
    load config/workstations/registry.yaml
    resolve current machine from hostname and hostname_aliases
    require current machine to be dev-primary/ace-linux-1 for v1 scheduled deployment
    fail closed with configuration_error if resolved machine lacks tier1_baseline
    resolve ECOSYSTEM_ROOT from REPO_ECOSYSTEM_ROOT env, else machine.tier1_repo_root from registry
    fail closed with configuration_error if neither source provides an ecosystem root
    resolve WORKSPACE_ROOT from WORKSPACE_HUB env, else machine.workspace_root, else REPO_ROOT
    require repo_layout=sibling for this implementation; report configuration_error otherwise
    resolve today in UTC
    resolve OUTPUT_DIR from REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR env, else REPO_ROOT/.claude/state/repo-ecosystem-hygiene
    resolve PROBE_TIMEOUT_SEC from REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC, default 10
    resolve REPO_TIMEOUT_SEC from REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC, default 45
    resolve TOTAL_RUNTIME_DEADLINE_SEC from REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC, default 480
    create report/state output directory only through fs_write("mkdir-output-dir")
    configured repos =
        tier1_baseline.required
        + tier1_baseline.optional
        + tier1_baseline.non_tier1_machine_access_current
        de-duplicated in stable order
    historical registry entries =
        tier1_baseline.historically_moved_not_currently_present
        preserve source_issue, source_comment, prior_claim, latest_probe, and warning fields
        report WARN using each entry's registry warning value, not an invented finding name
        if live path state no longer matches latest_probe, add latest_probe_mismatch=true without changing the registry warning finding
    compare machine.repos against those governed buckets:
        if a machine repo is absent from required/optional/non_tier1_machine_access_current, record registry_policy_gap WARN and classify it as known_unclassified until registry is updated
    classify each configured repo as required | optional | machine_access | unknown_config
    for each repo:
        repo_path = WORKSPACE_ROOT for workspace-hub else ECOSYSTEM_ROOT/repo
        if repo_path does not contain .git:
            if repo class is required:
                record repo status ERROR with finding missing_required_checkout
            else:
                record repo status WARN with finding missing_checkout
            continue
        collect bounded, read-only git probes through git_readonly() under the per-repo and total runtime deadlines:
            branch = git_readonly("branch-current")
            default_branch = git_readonly("default-branch")
            dirty_count = count git_readonly("status-short")
            upstream = git_readonly("upstream-ref") if present
            ahead/behind = git_readonly("ahead-behind") if upstream present
            worktree_count = git_readonly("worktree-list") count
            local_worktree_detail = parse git_readonly("worktree-list"):
                count linked worktrees
                count prunable/broken entries when reported by git
                count orphan paths whose worktree path no longer exists
                for each linked non-primary worktree HEAD sha, call git_readonly("commit-date-by-sha", sha)
                mark worktree stale if linked worktree HEAD commit age >= 14 days and path is not the primary repo path
            remote_worktree_like_ref_count = git_readonly("remote-worktree-like-refs") count:
                local refs/remotes entries matching worktree/worktree-agent/codex/agent naming patterns
            local branch inventory = git_readonly("local-branches")
            report non-default branch inventory in JSON/Markdown even when branches are not stale:
                count/list local branches where branch != default_branch
                include current flag and last commit age where available
                mark current branch != default_branch as WARN current_non_default_branch
                mark non-current, non-stale, non-default branches as INFO branch_inventory
            stash_count = git_readonly("stash-list") count
            stale local branch indicators:
                branch is not current/default and latest commit age >= 14 days
            stale stash indicators:
                stash entry age >= 14 days
        derive repo status using registry placement policies:
            OK if current branch equals default branch, clean, 0/0 divergence, no extra stale worktrees/stashes
            WARN if current branch is not default, dirty tracked or untracked repo-local files, ahead/behind divergence, stale branches/stashes/worktrees, optional/non-tier1 missing checkout, or optional/non-tier1 missing upstream
            ERROR if required upstream is missing, git command failures, missing required checkout, or missing workspace/config root
    scan ECOSYSTEM_ROOT first-level entries:
        allow configured repo names, registry infrastructure_dirs, and documented local system dirs from daily-cleanup.sh
        skip names already handled by configured repo buckets or historically_moved_not_currently_present so each path has one canonical classification
        record configured siblings by class
        record only registry/runtime-allowlisted non-git baseline names as INFO known_unclassified, not delete candidates
        record current/new unknown sibling git repos as WARN registry_disposition_required, not delete candidates
        record new unknown non-git first-level residue as WARN, not delete candidates
    read newest .claude/state/cron-health/*.json if available:
        require newest cron-health report mtime <= 36 hours old before copying task statuses
        copy task status for daily-today into health_links when present
        represent repository-sync as UNKNOWN schedule_metadata_mismatch until its task command/log glob contract is repaired; include #2572
        attach issue refs: repository-sync -> #2572, daily-cleanup -> #2752, daily-today/daily readiness/report sink -> #2652
    read daily-cleanup health through gh_readonly("daily-cleanup-issue-signal"):
        make at most two bounded REST reads: first comments request uses `gh api --include ...comments?per_page=1` to discover the last page from the Link header, then fetch only `...comments?per_page=30&page=<last_page>`
        never use `gh api --paginate` for this signal
        scan that bounded newest-comment window backward for the latest daily-cleanup.sh marker
        record marker freshness separately from semantic health
        status UNKNOWN with finding known_path_model_mismatch while daily-cleanup.sh still checks sibling repos under WORKSPACE_ROOT/repo
        status WARN/UNKNOWN if marker is missing from the bounded window, stale, or gh query unavailable
        include source_issue #2652 and design_issue #2752
        if cron-health state is missing or stale, record health_links status UNKNOWN/WARN
    do not infer repository-sync freshness directly from raw repository-sync logs because the existing scheduled-task log path is ambiguous; leave scheduled-task freshness calculation to cron-health
    write local-only JSON state under OUTPUT_DIR atomically via same-directory temp file then mv
    write local-only dated Markdown report under OUTPUT_DIR atomically via same-directory temp file then mv
    update local-only latest Markdown report under OUTPUT_DIR atomically via same-directory temp file then mv
    print one evidence line:
        task=repo-ecosystem-hygiene status=<OK|WARN|ERROR> artifact=<latest report> state=<json> ts=<iso8601>
    default cron mode exits 0 if the audit completes and writes artifacts, even when findings status is WARN/ERROR
    on audit execution failure, malformed configuration, or unwritable outputs:
        print exactly one cron-health-detectable line: "ERROR: repo-ecosystem-hygiene execution_failed code=<code> reason=<sanitized_reason>"
        exit nonzero

function git_readonly(operation):
    case operation in explicit allowlist:
        branch-current -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git branch --show-current
        status-short -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 --untracked-files=all
        upstream-ref -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git rev-parse --abbrev-ref --symbolic-full-name @{u}
        ahead-behind -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git rev-list --left-right --count HEAD...@{u}
        worktree-list -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git worktree list --porcelain
        commit-date-by-sha -> validate sha with ^[0-9a-f]{7,40}$, then timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git show -s --format=%cI <sha>
        default-branch -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git symbolic-ref --short refs/remotes/origin/HEAD, strip leading origin/, falling back to main/master only when origin/HEAD is absent and the fallback branch exists locally
        remote-worktree-like-refs -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git for-each-ref --format=... refs/remotes
        local-branches -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git for-each-ref --format=... refs/heads
        stash-list -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git stash list --date=iso-strict --format=%gd%x1f%ci%x1f%s
        recent-local-log -> timeout PROBE_TIMEOUT_SEC with GIT_OPTIONAL_LOCKS=0 git log with bounded local options
    reject every other operation before invoking git
    never invoke git through eval, bash -c, a variable subcommand, or assembled shell strings
    capture stdout/stderr separately
    return structured fields: exit_code, stdout, sanitized_error_summary

function gh_readonly(operation):
    case operation in explicit allowlist:
        daily-cleanup-issue-signal -> timeout PROBE_TIMEOUT_SEC with bounded gh api read of issue #2652 comments: first request uses `gh api --include ...comments?per_page=1` and parses the Link header for `rel="last"`; second request fetches only `...comments?per_page=30&page=<last_page>`; never use `--paginate`
    reject every other operation before invoking gh
    never invoke gh issue comment/edit/close, gh pr merge, gh api mutations, or assembled gh command strings
    capture stdout/stderr separately
    return structured fields: exit_code, stdout, sanitized_error_summary

function fs_write(operation, target):
    resolve target under OUTPUT_DIR
    reject target if it escapes OUTPUT_DIR after realpath/normalization
    case operation in explicit allowlist:
        mkdir-output-dir -> mkdir -p OUTPUT_DIR
        write-temp-output -> write only OUTPUT_DIR/.tmp-* files
        replace-output -> mv only from OUTPUT_DIR/.tmp-* to OUTPUT_DIR/*.md or OUTPUT_DIR/*.json
    reject every other filesystem write operation

function readonly_guard_tests():
    read script text
    require all live git invocations to occur inside git_readonly() allowlist cases
    require every live git/gh probe to run through timeout with PROBE_TIMEOUT_SEC
    require filesystem writes to occur only through fs_write() allowlist cases under OUTPUT_DIR
    fail if script contains eval, bash -c with git, git "$subcommand", or dynamically assembled git command strings
    fail if mutating live command tokens appear:
        "git add", "git commit", "git push", "git pull", "git merge", "git rebase",
        "git reset", bare or mutating "git stash" forms except exact timestamped "git stash list --date=iso-strict --format=%gd%x1f%ci%x1f%s", "git checkout", "git switch", "git branch -d",
        "git worktree prune", "git clean", "gh issue comment", "gh issue edit", "gh issue close", "gh pr merge",
        "rm -f", "rm -rf", "rm -r", "rm -fr", "rmdir", "unlink", "find ... -delete", "find ... -exec rm", "xargs rm"
    allow read-only subcommands with exact patterns:
        "git stash list --date=iso-strict --format=%gd%x1f%ci%x1f%s"
        "git branch --show-current"
        "git worktree list"
        "git status"
        "git rev-parse"
        "git rev-list"
        "git for-each-ref"
        "git log" for local metadata only
    allow output writes only through exact mkdir/mv/temp-file patterns constrained to OUTPUT_DIR
    allow mutating strings only inside comments/test allowlist sentinels if needed

function sanitize_for_cron_log(raw_stderr):
    never write raw git/gh stderr to cron stdout/stderr or scheduled-task logs for expected probe failures
    map known failures to neutral codes such as git_upstream_missing, git_probe_failed, git_not_repo
    strip or replace cron-health trigger strings: "ERROR:", "fatal:", "Traceback", "Permission denied", "command not found", "No such file or directory"
    preserve detailed raw stderr only in ignored JSON under a `raw_error_redacted` field if needed for local diagnosis
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/cron/repo-ecosystem-hygiene-audit.sh` | read-only audit implementation |
| Modify | `scripts/cron/setup-cron.sh` | default `UV_CACHE_DIR` to a repo-local path before internal `uv run` calls when unset |
| Create | `scripts/cron/tests/test_repo_ecosystem_hygiene_audit.py` | TDD coverage for report shape, read-only command guard, fixture behavior |
| Modify | `scripts/cron/tests/test_validate_schedule.py` | assert the new scheduled task exists, accepts registry hostname aliases such as `vamsee-linux1`, declares valid runtime requirements, and has a stable log path |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | add `repo-ecosystem-hygiene` daily task before `cron-health` |
| Modify | `config/workstations/registry.yaml` | add `timeout` to dev-primary capabilities if the scheduled task requires the coreutils timeout command |
| Modify | `scripts/monitoring/cron-health-check.sh` | support per-task stale thresholds from scheduled-task metadata |
| Modify | `scripts/monitoring/tests/test_cron_health_check.sh` | prove the 05:35 daily task becomes stale before the next 05:45 cron-health run if one run is missed |
| Modify | `docs/ops/scheduled-tasks.md` | document the new scheduled audit and operator command |
| Create | `.claude/skills/workspace-hub/repo-ecosystem-hygiene/SKILL.md` | operator skill for interpreting reports and routing remediation |
| Generated local-only | `.claude/state/repo-ecosystem-hygiene/latest.md` | latest human-readable report generated by each run; intentionally ignored by git |
| Generated local-only | `.claude/state/repo-ecosystem-hygiene/YYYY-MM-DD.md` | dated report generated by each run; intentionally ignored by git |
| Generated local-only | `.claude/state/repo-ecosystem-hygiene/YYYY-MM-DD.json` | machine-readable state generated by each run; intentionally ignored by git |
| Not generated by cron | `docs/reports/repo-ecosystem-hygiene*.md` | intentionally excluded from unattended generation to preserve the non-mutating/no-dirty-worktree contract |
| Update | `docs/plans/README.md` | add this plan to the planning index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_script_syntax_ok` | audit script is valid bash | `bash -n scripts/cron/repo-ecosystem-hygiene-audit.sh` | exit 0 |
| `test_readonly_guard_requires_git_allowlist_wrapper` | all git probes go through a fixed read-only operation map | script text | live `git` invocations appear only inside `git_readonly()` allowlist cases; no `eval`, `bash -c` with git, `git "$subcommand"`, or assembled git command strings |
| `test_readonly_guard_requires_gh_allowlist_wrapper` | GitHub signal reads cannot mutate issues/PRs | script text | live `gh` invocations appear only inside `gh_readonly()` allowlist cases; no `gh issue comment/edit/close`, `gh pr merge`, mutation `gh api`, or assembled gh command strings |
| `test_git_probes_disable_optional_locks` | read-only probes do not refresh/write git index metadata | script text | every allowlisted git probe is invoked with `GIT_OPTIONAL_LOCKS=0` |
| `test_git_and_gh_probes_are_timeout_bounded` | unattended cron run cannot hang on one slow repo/API call | script text plus wrapper fixture that sleeps past timeout | every live git/gh probe runs through `timeout`; slow probe records sanitized timeout finding and the audit continues until the per-repo or total deadline is reached |
| `test_total_runtime_deadline_stops_before_cron_health_window` | 05:35 audit cannot overlap the 05:45 cron-health run indefinitely | fixture with many slow repos and low `REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC` | audit stops new repo probes after the total deadline, writes partial results with `incomplete_due_to_deadline`, exits 0 if artifacts were written, and finishes before the configured deadline plus one probe timeout |
| `test_output_writes_confined_to_output_dir` | required mkdir/temp/mv writes are allowed but cannot touch repo/sibling content | temp `REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR` plus path traversal attempts | only `mkdir -p OUTPUT_DIR`, temp writes under OUTPUT_DIR, and `mv` from OUTPUT_DIR temp files to OUTPUT_DIR final files are allowed; escaping paths fail closed |
| `test_repo_root_resolves_without_git` | root discovery does not bypass the git allowlist | script text and fixture script path | `REPO_ROOT` is derived from script location; no root-resolution `git` invocation exists |
| `test_readonly_guard_rejects_mutating_git_tokens` | secondary static guard rejects live mutating commands | script text | no `git add/commit/push/pull/merge/rebase/reset/checkout/switch`, mutating stash forms, branch delete, worktree prune, `rm -rf`, or `find -delete` outside comments/allowlisted test text |
| `test_readonly_guard_allows_timestamped_stash_list_only` | stash inventory remains possible without allowing stash mutation | script text | timestamped `git stash list --date=iso-strict --format=%gd%x1f%ci%x1f%s` is allowed; bare `git stash`, `git stash pop`, `git stash push`, and `git stash drop` are rejected |
| `test_stash_parser_avoids_bash_nul_loss` | stash parsing does not rely on NUL bytes in Bash variables | fixture stash output using unit-separator `%x1f` delimiter and stash subject containing spaces/shell punctuation | parser preserves stash ref/date/subject fields without Bash `ignored null byte` warnings |
| `test_registry_sibling_layout_paths` | sibling layout uses `/mnt/local-analysis/<repo>`, not nested `workspace-hub/<repo>` | temp registry with `repo_layout: sibling` and fixture dirs | `digitalmodel` path resolves to `<root>/digitalmodel`; nested path is not used |
| `test_v1_fails_closed_without_tier1_baseline` | v1 does not silently run on machines lacking governed repo buckets | fixture registry for non-dev-primary machine without `tier1_baseline` | exits nonzero with `configuration_error`; no repo health report claims are emitted |
| `test_configured_repo_universe_includes_non_python_required_repos` | audit uses workstation registry, not only Python repo list | fixture registry with required `llm-wiki` and Python list without it | repo universe includes `llm-wiki` and classifies it as required |
| `test_repo_universe_uses_governed_registry_buckets` | machine-access scope uses placement-policy buckets, not raw roster | fixture registry with raw `repos` entry absent from required/optional/non-tier1 bucket | audited universe comes from required+optional+non_tier1; absent raw roster entry is `registry_policy_gap`/`known_unclassified` WARN |
| `test_historical_registry_entries_follow_historical_policy` | historical relocation policy is not dropped or renamed | fixture `historically_moved_not_currently_present` entry with `latest_probe: absent` and `warning: historical_state_changed_since_prior_comment`, first absent then present | both cases preserve source issue/comment/prior/latest metadata and report `WARN` with finding copied from entry `warning`; present-again case also sets `latest_probe_mismatch: true` |
| `test_historical_registry_precedence_over_unknown_residue` | historical entries are not double-reported as unknown residue | fixture with live first-level path `acma-projects` and registry historical metadata for that name | output has one canonical `acma-projects` finding from historical metadata and no duplicate `registry_disposition_required` residue finding |
| `test_missing_optional_repo_is_warn_not_crash` | missing optional configured repo is reported, not treated as clean | temp ecosystem with missing optional repo | JSON includes `status: WARN` and repo finding `missing_checkout` without shell `No such file or directory` text in log |
| `test_missing_required_repo_reports_error` | missing required configured repo is high-severity drift | temp ecosystem with missing required repo such as `llm-wiki` | JSON includes repo `status: ERROR`, finding `missing_required_checkout`, and overall status `ERROR` |
| `test_missing_machine_access_repo_reports_warn` | machine-access repos are surfaced without blocking required baseline health | temp registry with machine-only repo missing | JSON includes repo `status: WARN` and finding `missing_checkout` |
| `test_unknown_sibling_git_repo_reports_warn` | live unconfigured sibling repos are surfaced without deletion advice | temp ecosystem with registry repo plus extra `.git` sibling | JSON and Markdown include unknown sibling repo as `WARN` with class `unknown_config` |
| `test_unknown_non_git_sibling_residue_reports_warn` | sibling-of-canonical residue scope includes non-git files/dirs | temp ecosystem with unconfigured first-level file and directory | JSON and Markdown include each as `WARN` with finding `unknown_sibling_residue`; no delete advice |
| `test_known_infrastructure_dirs_are_allowlisted` | expected local root infrastructure does not false-warn as residue | fixture entries from registry `infrastructure_dirs` plus `.pnpm-store`, `.Trash-1000`, `.cleanup-lock`, `.cleanup-trash`, `.daily-cleanup-lock` | no unknown-residue finding for allowlisted names |
| `test_live_non_git_residue_requires_registry_disposition` | recurring first-level non-git root entries do not disappear into an informal baseline | fixture entries `.agents`, `.claude`, `.codex`, `.planning`, session-summary/evidence filename patterns, historical `acma-projects`, plus unmatched `2802-pilot-evidence` and `acma-projects-freeze-work` | deterministic runtime patterns are `INFO`/`known_unclassified`; historical names use historical metadata; unmatched current names are `WARN`/`registry_disposition_required` until registry disposition exists |
| `test_unregistered_git_siblings_require_registry_disposition` | current unregistered git checkouts remain actionable drift | fixture git siblings `deckhand`, `llm-wiki-fdas`, `raw-to-knowledge-playbook`, and `worldenergydata-wiki` outside governed registry buckets | each is `WARN` with finding `registry_disposition_required`; no delete advice |
| `test_clean_repo_reports_ok` | clean repo with upstream 0/0 reports OK | temp git repo with origin/upstream fixture | repo row `status: OK`, dirty `0`, ahead `0`, behind `0` |
| `test_default_branch_detected_without_network` | default-branch logic does not hardcode `main` | temp git repo with local `refs/remotes/origin/HEAD` pointing to `origin/trunk` | default branch strips remote prefix and resolves to `trunk`; current `trunk` is OK; no network command is used |
| `test_dirty_repo_reports_warn_without_mutation` | registry dirty policy is warning and files are left untouched | temp git repo with modified tracked file and untracked repo-local file | repo status `WARN`; dirty count includes both tracked and untracked entries; file content unchanged; no new commits |
| `test_non_default_branch_inventory_reports_even_when_not_stale` | issue-required non-main branch reporting is independent of stale-branch warnings | temp git repo with default branch plus a 2-day-old feature branch and current default branch | JSON/Markdown include non-default branch count/list as INFO branch inventory; repo can remain OK if no other drift exists |
| `test_current_non_default_branch_reports_warn` | active checkout on a non-default branch is visible even if branch is fresh | temp git repo with current branch `feature/x` and default branch `main` | repo status `WARN` with finding `current_non_default_branch`; branch inventory includes `feature/x` |
| `test_required_missing_upstream_reports_error` | registry upstream policy for required repos is error | required repo fixture with no upstream | repo status `ERROR`, finding `missing_required_upstream` |
| `test_ahead_behind_reports_warn_by_registry_policy` | registry ahead/behind policies are warnings | required repo fixture with ahead/behind counts | repo status `WARN`, findings include ahead/behind counts |
| `test_git_failure_stderr_sanitized_for_cron_health` | failing git probes cannot self-poison cron-health logs | fixture git probe returning stderr with `fatal:` or `No such file or directory` | stdout/log omit cron-health trigger strings; JSON stores sanitized failure code and repo status `ERROR` |
| `test_gh_failure_stderr_sanitized_for_cron_health` | unavailable/auth-failed GitHub signal does not poison cron-health logs | fixture `gh` failure stderr with `Permission denied`, `command not found`, or `Traceback` | stdout/log omit cron-health trigger strings; health link is `WARN`/`UNKNOWN` with sanitized failure code |
| `test_stale_branch_and_stash_thresholds_report_warn` | stale branch/stash indicators use explicit age thresholds | temp git repo with one 13-day and one 14-day branch/stash fixture | only entries age >= 14 days create `WARN` findings; active/current/default branches are excluded |
| `test_worktree_detail_reports_stale_broken_orphan_counts` | worktree scope includes count plus stale/broken/orphan detail where detectable | fixture `git worktree list --porcelain` with linked, prunable, and missing-path entries plus per-HEAD `git show -s --format=%cI` results | JSON includes `local_worktree_count`, `broken_worktree_count`, `orphan_worktree_count`, `stale_worktree_count`; stale cutoff is 14 days; missing/invalid HEAD date lookup records an unknown-age detail instead of guessing stale |
| `test_remote_worktree_like_refs_are_counted_without_network` | remote worktree signal is limited to local remote refs | fixture refs/remotes entries matching worktree/codex/agent naming patterns | JSON includes `remote_worktree_like_ref_count`; no fetch/pull/network command is used |
| `test_warn_log_avoids_cron_health_error_patterns` | ordinary drift log will not self-poison cron-health | generated WARN/missing-checkout log text | no `ERROR:`, `fatal:`, `Traceback`, `Permission denied`, `command not found`, or `No such file or directory` tokens |
| `test_cron_mode_exits_zero_for_completed_audit_with_findings` | cron-health tracks execution health, while repo-hygiene severity remains in artifacts | fixture run with WARN/ERROR repo findings but writable outputs | exit 0; stdout evidence line includes `status=WARN` or `status=ERROR`; JSON preserves per-repo findings; no expected finding emits cron-health trigger tokens |
| `test_execution_failure_emits_cron_health_error_marker` | true audit execution failures are visible to cron-health despite sanitized ordinary findings | malformed config or unwritable output fixture | exits nonzero and log includes exactly one `ERROR: repo-ecosystem-hygiene execution_failed ...` line |
| `test_report_outputs_written_atomically` | local Markdown latest, dated report, and JSON state are generated atomically under the configured output directory | temp `REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR` plus failing-write fixture | implementation writes same-directory temp files then `mv`s into place under the override directory; final artifacts exist and parse; no partial final file remains after simulated failure; default path is not touched |
| `test_evidence_line_emitted` | script prints cron-health-friendly evidence line | fixture run | stdout contains `task=repo-ecosystem-hygiene status=` with artifact/state paths |
| `test_schedule_task_entry_exists` | YAML registers the task before cron-health | `config/scheduled-tasks/schedule-tasks.yaml` | task id exists, schedule is exactly `35 5 * * *`, machines include `dev-primary`/`ace-linux-1`, log is `logs/quality/repo-ecosystem-hygiene-*.log` |
| `test_schedule_task_includes_hostname_aliases` | installer raw hostname filtering cannot skip alias hosts | fixture registry with `hostname_aliases: [vamsee-linux1]` | task `machines` includes canonical machine id, hostname, and aliases: `dev-primary`, `ace-linux-1`, `vamsee-linux1` |
| `test_validate_schedule_accepts_registry_hostname_aliases` | existing schedule-machine validation does not reject registry aliases | `scripts/cron/tests/test_validate_schedule.py` with `schedule-tasks.yaml` entry containing `vamsee-linux1` | validator test derives allowed machine names from registry machine ids, hostnames, and aliases or explicitly includes the registry alias; no hardcoded stale list rejects `vamsee-linux1` |
| `test_schedule_task_declares_runtime_requires` | scheduler metadata declares parser/runtime dependencies | `config/scheduled-tasks/schedule-tasks.yaml` task entry | `requires` includes `bash`, `python3`, `uv`, `git`, `gh`, and `timeout` |
| `test_timeout_capability_registered_for_dev_primary` | `validate-schedule.py` will not reject the new runtime requirement | `config/workstations/registry.yaml` dev-primary capabilities and new task `requires` | `timeout` is present in the resolved dev-primary capability set before the scheduled task requires it |
| `test_schedule_command_redirects_to_declared_log_family` | cron-health can see the actual scheduled output | `config/scheduled-tasks/schedule-tasks.yaml` task entry | command sets `PATH=$HOME/.local/bin:$HOME/.npm-global/bin:$PATH`, then appends stdout/stderr to `logs/quality/repo-ecosystem-hygiene-$(date +\%Y\%m\%d).log`, matching the declared `log:` glob |
| `test_schedule_task_declares_short_stale_threshold` | a missed 05:35 daily run is visible at the next 05:45 cron-health check | `config/scheduled-tasks/schedule-tasks.yaml` task entry | task metadata includes `stale_after_hours: 23` or equivalent per-task threshold |
| `test_cron_health_respects_task_specific_stale_threshold` | cron-health does not silently miss a one-day outage for this task | cron-health fixture with repo-ecosystem-hygiene last log age 24h10m and per-task threshold 23h | task is reported `STALE`; default daily tasks without override keep existing threshold behavior |
| `test_schedule_validator_passes_with_hygiene_task` | canonical schedule validator accepts the task independent of host | `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python scripts/cron/validate-schedule.py` | exit 0 |
| `test_validate_schedule_nested_uv_uses_repo_cache` | schedule tests do not write uv cache outside the repo when spawning the validator | `scripts/cron/tests/test_validate_schedule.py` subprocess call to `uv run --no-project python scripts/cron/validate-schedule.py` | subprocess environment sets or preserves `UV_CACHE_DIR=.claude/state/uv-cache` before invoking `uv` |
| `test_health_links_use_cron_health_state_and_issue_refs` | linkage is concrete without inventing false health from known mismatches | fixture `.claude/state/cron-health/YYYY-MM-DD.json` containing `daily-today`; fixture #2652 comments with daily-cleanup marker | report includes cron-health status for `daily-today`, repository-sync as `UNKNOWN`/`schedule_metadata_mismatch` with ref `#2572`, daily-cleanup status from latest #2652 marker, refs `#2752`/`#2652`, and no direct repository-sync raw log-age inference |
| `test_stale_cron_health_state_does_not_copy_statuses` | health links do not present stale cron-health as current | newest cron-health JSON mtime older than 36 hours | `health_links` status is `UNKNOWN/WARN` with stale source age; task statuses are not copied as current |
| `test_daily_cleanup_issue_signal_freshness` | daily-cleanup has concrete non-mutating, bounded freshness evidence without pretending semantic health | fixture #2652 last-page comments with daily-cleanup marker ages 35h and 37h while `daily-cleanup.sh` still has the known path-model mismatch | 35h marker reports marker freshness only and overall `daily-cleanup` health `UNKNOWN`/`known_path_model_mismatch`; 37h/missing/gh-unavailable reports WARN/UNKNOWN with issue refs |
| `test_daily_cleanup_issue_signal_is_bounded` | cron run does not fetch the full #2652 history | gh wrapper fixture with hundreds of older comments and marker inside/outside latest 30 comments | implementation makes at most two `gh api` reads; marker inside latest 30 is evaluated; marker outside the bounded window returns WARN/UNKNOWN `marker_not_in_recent_window` |
| `test_daily_cleanup_issue_signal_uses_link_header` | bounded latest-page discovery is implementable with `gh api` | gh wrapper fixture for first response with `--include` headers and `Link: ... rel="last"` | first call includes `--include` and `per_page=1`; second call fetches `per_page=30&page=<last_page>`; `--paginate` is rejected |
| `test_generated_reports_stay_local_only` | unattended cron does not dirty tracked report paths | fixture run with output override and clean git worktree | generated Markdown/JSON are under output dir only; no `docs/reports/repo-ecosystem-hygiene*.md` file is written by the cron script |
| `test_operator_skill_documents_non_mutating_policy` | skill/runbook preserves the safety boundary | `.claude/skills/workspace-hub/repo-ecosystem-hygiene/SKILL.md` | includes read-only policy and routes remediation to existing repo-sync/worktree hygiene skills |

---

## Acceptance Criteria

- [ ] `scripts/cron/repo-ecosystem-hygiene-audit.sh` exists, is executable, and passes `bash -n`.
- [ ] The script is read-only by construction: all git probes use the fixed `git_readonly()` allowlist with `GIT_OPTIONAL_LOCKS=0`, and tests fail if mutating git/filesystem cleanup commands are introduced.
- [ ] Required filesystem writes are explicitly scoped: only `mkdir`, temp-file writes, and `mv` inside `REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR` or the default `.claude/state/repo-ecosystem-hygiene` output directory are allowed.
- [ ] Every git/gh probe is timeout-bounded, and the run has a total runtime deadline that stops new repo probes before the later `cron-health` window.
- [ ] The script uses `REPO_ECOSYSTEM_ROOT` override or `machine.tier1_repo_root` from `config/workstations/registry.yaml`; it fails closed if neither is present and does not hardcode `/mnt/local-analysis` in script logic.
- [ ] The script resolves the live sibling checkout layout from `config/workstations/registry.yaml` and does not assume nested `workspace-hub/<repo>` checkouts.
- [ ] The script reports all required, optional, and non-tier1 machine-access repos from `config/workstations/registry.yaml`, including non-Python required repos such as `llm-wiki`, and surfaces raw roster entries outside governed buckets as registry policy gaps.
- [ ] The script reports `historically_moved_not_currently_present` registry entries according to historical policies, preserving each entry's source issue/comment, `latest_probe`, and `warning` field as the finding name.
- [ ] V1 scheduled deployment is scoped to `dev-primary`/`ace-linux-1` and fails closed on machines without `tier1_baseline`.
- [ ] The script reports all configured/live repos it actually enumerates and distinguishes `OK`, `WARN`, `ERROR`, and `missing_checkout`; severity follows `config/workstations/registry.yaml` placement policies, with required absence/upstream as `ERROR` and optional/non-tier1 absence, dirty, ahead, and behind drift as `WARN`.
- [ ] Dirty status includes both tracked changes and untracked repo-local files through `git status --porcelain=v1 --untracked-files=all`; first-level sibling residue remains reported separately under the ecosystem-root scan.
- [ ] The report includes non-default local branch inventory even when branches are not stale; stale branches and current non-default checkouts remain separate WARN findings.
- [ ] The script detects each repo's default branch from local `origin/HEAD` without network access and does not hardcode `main`.
- [ ] The script reports local worktree count plus stale, broken, and orphan worktree counts where detectable, derives stale linked-worktree age from validated HEAD sha commit dates without network access, and reports remote worktree-like local remote refs without network access.
- [ ] The script reports current/new unknown first-level sibling git repos as `WARN`/`registry_disposition_required` without deletion advice, reports unknown first-level non-git residue under `/mnt/local-analysis` as `WARN`, and keeps only deterministic runtime patterns and registry infrastructure dirs visible as `INFO`/`known_unclassified`.
- [ ] The script writes ignored local Markdown and JSON outputs suitable for trend tracking without dirtying the git worktree by default, supports `REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR` for hermetic tests, and does not generate tracked `docs/reports/repo-ecosystem-hygiene*.md` files from unattended cron.
- [ ] The script emits a one-line evidence record for completed audits, never writes raw failing git/gh stderr or expected repo-hygiene findings to scheduled-task logs using cron-health trigger tokens, and emits an explicit `ERROR: repo-ecosystem-hygiene execution_failed ...` marker for true execution failures so `cron-health` can detect execution failures.
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` includes the new daily task at exact schedule `35 5 * * *`, before `cron-health`, with `machines` covering `dev-primary`, `ace-linux-1`, and hostname alias `vamsee-linux1`, `requires: [bash, python3, uv, git, gh, timeout]`, a stable `log:` glob, a PATH prefix for `$HOME/.local/bin` and `$HOME/.npm-global/bin`, a command redirect that writes to the same log path family, and per-task stale threshold metadata that lets the 05:45 `cron-health` check flag a missed 05:35 run by the next day.
- [ ] `scripts/monitoring/cron-health-check.sh` honors the task-specific stale threshold while preserving existing default threshold behavior for tasks without an override.
- [ ] The report includes cron-health-sourced status for real scheduled task ID `daily-today` where available, marks `repository-sync` as `UNKNOWN`/`schedule_metadata_mismatch` until its existing command/log mismatch is fixed, and includes bounded read-only #2652 latest-comment-window freshness for `daily-cleanup` while reporting `daily-cleanup` semantic health as `UNKNOWN`/`known_path_model_mismatch` until that routine's sibling path model is fixed, with issue refs to #2572, #2752, and #2652.
- [ ] `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python scripts/cron/validate-schedule.py` passes, and `UV_CACHE_DIR=.claude/state/uv-cache bash scripts/cron/setup-cron.sh --dry-run` shows the new task when run on the deployed target host whose `hostname -s` is listed in task `machines` (current target evidence: `ace-linux-1`). `scripts/cron/setup-cron.sh` also defaults `UV_CACHE_DIR` to the repo-local cache when unset.
- [ ] `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project pytest scripts/cron/tests/test_validate_schedule.py scripts/cron/tests/test_repo_ecosystem_hygiene_audit.py -q` passes, and nested `uv` subprocesses in schedule tests preserve the same repo-local cache.
- [ ] `docs/ops/scheduled-tasks.md` documents the task.
- [ ] `.claude/skills/workspace-hub/repo-ecosystem-hygiene/SKILL.md` documents report interpretation and explicitly routes remediation to manual/approved workflows.
- [ ] `bash scripts/legal/legal-sanity-scan.sh` passes or any pre-existing failure is documented with exact output.
- [ ] Implementation remains blocked until this plan has adversarial review artifacts and user approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | CLI failed before returning a usable review |
| Codex r1 | MAJOR | Wrong nested repo path model; audited repo set omitted required non-Python repos; read-only guard contradicted `git stash list`; cron-health WARN log compatibility missing; host-dependent dry-run test |
| Codex r2 | MAJOR | Stale Python-list scope sentence; review-artifact evidence stale while Codex output was still zero bytes; token-only read-only guard too weak; `.claude/state` JSON incorrectly implied to be repo-tracked |
| Codex r3 | MAJOR | Git probes lacked `GIT_OPTIONAL_LOCKS=0`; schedule was still open-ended; dry-run acceptance incorrectly implied both hostname identities could be verified from one machine |
| Codex r4 | MAJOR | Root resolution used an unallowlisted git call; missing-checkout severity was not defined by repo class |
| Codex r5 | MAJOR | Scheduled command/log glob parity missing; unknown non-git sibling residue omitted; dirty/ahead/behind severity contradicted registry policy; repository-sync/daily-cleanup health linkage missing |
| Codex r6 | MAJOR | `daily-cleanup` and daily-readiness were incorrectly modeled as cron-health task statuses; known local infrastructure dir allowlist source was unspecified |
| Codex r7 | MAJOR | Cron-health state stale threshold missing; repo universe used raw `machine.repos`; stale branch/stash thresholds missing; schedule requires underdeclared; atomic writes untested; production root baseline too noisy |
| Codex r8 | MAJOR | Worktree scope under-specified; daily-cleanup health lacked concrete signal/deferral; non-dev-primary registry contract not fail-closed; default branch detection missing |
| Codex r9 | MAJOR | `daily-cleanup` health was still a static unavailable marker rather than a concrete signal |
| Codex r10 | MAJOR | Execution failures were invisible to cron-health after sanitization; `gh` failures lacked stderr sanitization; cron PATH for `uv`/`gh` underdeclared |
| Codex r11 | MAJOR | Default branch resolution did not strip `origin/`; stale stash age needed timestamped stash output |
| Codex r12 | MAJOR | repository-sync status still copied from known-bad cron-health log contract; unregistered git siblings downgraded to INFO; validator needed repo-local UV cache override |
| Codex r13 | MAJOR | Filesystem mutation guard missed `rm -f`/`find -exec rm`; historical registry policy bucket omitted; hostname aliases not covered by schedule machines |
| Codex r14 | MAJOR | Script path fallback hardcoded `/mnt/local-analysis`; historical absence was INFO despite registry warning policy |
| Codex r15 | MAJOR | Dirty status omitted untracked repo-local files; stale worktree age lacked a per-HEAD date probe; daily-cleanup issue signal queried all #2652 comments |
| Codex r16 | MAJOR | Cron-health claim overstated repo-hygiene visibility; historical warning field was renamed; output directory override was undefined |
| Codex r17 | MAJOR | Fresh daily-cleanup marker masked known path-model mismatch; git/gh probes lacked timeouts; non-git baseline hid current residue; output writes were not confined |
| Codex r18 | MAJOR | `timeout` was required without registry capability coverage; existing schedule-machine tests would reject hostname alias `vamsee-linux1` |
| Codex r19 | MAJOR | Non-default branch inventory was not required unless branches were stale; plan/review artifacts were still local-only untracked during review |
| Codex r20 | MAJOR | Fixed cron-health daily stale threshold could miss one-day outage; stale risk text contradicted bounded `gh api`; local-only reports needed explicit rationale |
| Codex r21 | MAJOR | Historical entry `acma-projects` conflicted with unknown-residue classification; pytest/nested validator `uv` paths lacked repo-local cache coverage |
| Codex r22 | MAJOR | `setup-cron.sh --dry-run` lacked repo-local UV cache; stash parser used Bash-unsafe NUL delimiter; bounded #2652 query lacked `gh api --include` Link-header contract |
| Codex r23 | MINOR | No blockers. Minor risks: local-only report export rationale, repository-sync repair follow-up, and #2652 newest-30 comment window could degrade to UNKNOWN under high comment volume |
| Gemini | UNAVAILABLE | CLI/API failure before returning a usable review |

**Current gate state:** plan-review passed with no MAJOR findings. Codex r23 returned MINOR; Claude and Gemini were unavailable. Implementation remains blocked until explicit user approval and `status:plan-approved`.

Revisions made based on review:
- Corrected the path model to use registry-driven sibling checkouts.
- Changed the repo universe from Python-tooling-only repos to workstation-registry required/optional/current-machine repos.
- Added an explicit read-only allowlist for `git stash list` and other read-only git probes.
- Added a cron-health compatibility test to ensure expected WARN drift does not emit generic error strings.
- Replaced the host-dependent `setup-cron.sh --dry-run` unit test with schedule-validator coverage, keeping dry-run as an ace-linux-1 manual acceptance check.
- Removed the stale Python-list scope sentence; registry remains the sole repo presence source of truth.
- Replaced token-only read-only protection with a fixed `git_readonly()` allowlist wrapper plus secondary static mutating-token tests.
- Clarified that daily Markdown/JSON outputs are ignored local state under `.claude/state/repo-ecosystem-hygiene/`, so cron does not dirty tracked docs by default.
- Removed exact review-artifact paths from the plan body to avoid Codex reading its own still-running zero-byte output during fanout; the GitHub issue comment will cite the committed review artifacts.
- Removed repository-sync log-age inference from v1 because the current scheduled-task log path and wrapper `$LOG` path disagree.
- Added explicit git stderr sanitization and unknown-sibling repo tests.
- Required `GIT_OPTIONAL_LOCKS=0` for every allowlisted git probe.
- Fixed the schedule to exact cron expression `35 5 * * *`.
- Scoped `setup-cron.sh --dry-run` acceptance to target-host manual evidence because the installer filters by live `hostname -s`.
- Changed repo root discovery to use script-relative paths rather than git.
- Defined missing-checkout severity by repo class and added tests for required, optional, and machine-access missing repos.
- Added schedule command/log-family parity requirements so cron-health scans the file the task actually writes.
- Added first-level non-git sibling residue reporting.
- Reconciled dirty/ahead/behind/upstream severity with registry placement policies.
- Added cron-health-state-based health links for real task ID `daily-today`, explicit `UNKNOWN`/`schedule_metadata_mismatch` reporting for `repository-sync`, plus issue/runbook links for `daily-cleanup` and #2652.
- Corrected health-link modeling: cron-health status is copied only when its schedule/log contract is trustworthy; `repository-sync` is not copied until its mismatch is fixed, and `daily-cleanup` uses the #2652 marker signal.
- Added known local infrastructure dir allowlisting from registry plus `daily-cleanup.sh`.
- Added a 36-hour freshness threshold for cron-health state before copying task statuses.
- Changed the repo universe to governed registry buckets (`required`, `optional`, `non_tier1_machine_access_current`) and report raw-roster gaps separately.
- Fixed stale branch/stash threshold at 14 days.
- Required schedule metadata to declare `bash`, `python3`, `uv`, `git`, `gh`, and `timeout`.
- Strengthened atomic-write tests to require temp-file plus `mv` behavior.
- Replaced the informal known-unclassified production root baseline with deterministic runtime-pattern and registry-infrastructure allowlisting only.
- Added concrete local/remote-like worktree detection fields and tests, including stale/broken/orphan counts.
- Replaced static daily-cleanup unavailable marker with a read-only #2652 comment freshness signal keyed to the `daily-cleanup.sh` marker.
- Scoped v1 scheduled deployment to `dev-primary`/`ace-linux-1` and added fail-closed tests for missing `tier1_baseline`.
- Added local default-branch detection through `refs/remotes/origin/HEAD` with no network access.
- Added a `gh_readonly()` allowlist wrapper and schedule `gh` requirement for the daily-cleanup issue-comment signal.
- Added a cron-health-detectable execution-failure marker while keeping expected probe failures sanitized.
- Added gh stderr sanitization and tests for unavailable/auth/PATH failures.
- Required the scheduled command to set a PATH prefix for `uv` and `gh`.
- Corrected default branch normalization to strip the `origin/` prefix.
- Changed stash inventory to timestamped `git stash list --date=iso-strict --format=...` so 14-day stale-stash tests are implementable.
- Marked repository-sync health as `UNKNOWN`/`schedule_metadata_mismatch` instead of copying the known-bad cron-health status.
- Changed current unregistered git siblings from INFO to WARN/`registry_disposition_required`; only deterministic runtime patterns remain INFO.
- Added repo-local `UV_CACHE_DIR=.claude/state/uv-cache` to validation commands.
- Expanded the mutation guard to reject `rm -f`, `find ... -exec rm`, `xargs rm`, `git clean`, and related cleanup forms.
- Added historical registry policy handling and tests.
- Required the scheduled task machines list to include hostname aliases used by the installer.
- Removed the hardcoded `/mnt/local-analysis` script fallback; production root must come from the environment override or workstation registry.
- Corrected historical registry entries to WARN using each entry's registry `warning` field.
- Expanded dirty status to include tracked and untracked repo-local files while keeping ecosystem-root residue as a separate scan.
- Defined stale linked-worktree age through a validated per-HEAD commit-date lookup.
- Bounded the daily-cleanup #2652 signal to at most two `gh api` reads and the newest 30 comments.
- Narrowed the cron-health contract to scheduled-task execution health; repo hygiene WARN/ERROR remains in artifacts and the evidence line.
- Changed historical handling to copy each registry entry's `warning` field as the finding instead of inventing a new finding name.
- Defined `REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR` as the hermetic test/output override.
- Changed `daily-cleanup` from freshness-as-health to `UNKNOWN`/`known_path_model_mismatch` while its sibling path model is known-bad.
- Added per-probe, per-repo, and total runtime deadlines so the unattended audit cannot run through the later cron-health window.
- Removed the informal non-git baseline for unmatched current root entries; they now WARN until registry disposition exists.
- Added `fs_write()` confinement for the required output-directory `mkdir`, temp-file writes, and atomic `mv`.
- Added `config/workstations/registry.yaml` to the implementation surface so `timeout` can be registered before the schedule requires it.
- Added explicit coverage for existing schedule-machine tests so registry hostname aliases such as `vamsee-linux1` are accepted.
- Added non-default local branch inventory as a report requirement independent of stale-branch warnings.
- Added a per-task cron-health stale threshold so a missed 05:35 run is visible at the next 05:45 health check.
- Documented that generated reports stay local-only to preserve the unattended cron no-dirty-worktree contract.
- Added historical-entry precedence so live historical names such as `acma-projects` are not double-reported as unknown residue.
- Required repo-local `UV_CACHE_DIR` for pytest and nested validator subprocesses.
- Added `setup-cron.sh` repo-local UV cache handling and acceptance coverage.
- Replaced Bash-unsafe NUL stash delimiters with unit-separator parsing requirements.
- Specified `gh api --include` Link-header parsing for bounded latest-page #2652 comment reads and banned `--paginate` for that signal.

---

## Risks and Open Questions

- **Risk:** If the audit exits nonzero on ordinary drift, `cron-health` may report expected repo hygiene drift as a failing cron job. The cron path will exit 0 for a completed audit with findings and carry `OK/WARN/ERROR` only in the evidence line, Markdown report, and JSON state; nonzero exits are reserved for audit execution failures.
- **Risk:** `cron-health` scans log tails for generic error strings such as `ERROR:` and `fatal:`. The audit log must avoid colon-form severity words for expected repo findings; use machine-readable `status=ERROR` or report headings without a trailing colon.
- **Risk:** Raw git stderr can include cron-health trigger strings such as `fatal:` and `No such file or directory`. The implementation will capture stderr, map failures to sanitized codes, and keep cron stdout/logs free of those trigger strings.
- **Risk:** `repository-sync` has a current log-path ambiguity between its schedule `log:` glob and wrapper `$LOG` expansion. This audit will not report repository-sync freshness in v1; cron-health continues to own scheduled-task log freshness until a separate issue resolves that mismatch.
- **Risk:** Scanning stale branches across many repos can be slow or trigger extra network access if broad GitHub queries are used. The first implementation will avoid `gh pr list` and other broad/unbounded GitHub API calls; the only approved v1 GitHub call is the bounded `gh_readonly("daily-cleanup-issue-signal")` read for #2652 comments.
- **Risk:** `/mnt/local-analysis` is a live production-host path, but tests need hermetic fixtures. The implementation will use `REPO_ECOSYSTEM_ROOT` and `REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR` overrides in tests.
- **Risk:** A static token guard alone can miss dynamic shell dispatch. The implementation will route git probes through a fixed `git_readonly()` operation map and add a static guard only as a secondary backstop.
- **Decision:** The scheduled task will run at `35 5 * * *` UTC, before `cron-health` at `05:45 UTC`, away from `repository-sync` top-of-4-hour slots, and before `daily-today` at `06:00 UTC`.
- **Clarification:** "Read-only" means no mutation of repos, remotes, branches, stashes, worktrees, locks, or cleanup-trash. The scheduled script may write its own ignored local audit artifacts under `.claude/state/repo-ecosystem-hygiene/` and append-only cron logs; tracked docs explain the workflow but are not rewritten by daily cron.

---

## Complexity: T2

**T2** - This will add one cron script, tests, scheduled-task wiring, reports/state outputs, and a small operator skill. The change is safety-sensitive because unattended automation must remain read-only, but it is not cross-repo implementation work.
