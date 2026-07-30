# Entry prompt — reconcile ace-win-1 ecosystem and equality evidence

You are operating on **ace-win-1**, the licensed Windows workstation. Drive this
machine as far as safely possible toward repo-ecosystem hygiene and machine-equality
equivalence, using the workspace's canonical reconciliation skill. Commit and push
only verified, task-scoped reconciliation artifacts after the legal scan passes.

## Privacy and authorization boundary

- Refer to this workstation only as `ace-win-1`. Do not print, record, or commit its
  current raw OS hostname; it collides with a private client identifier.
- Set `$env:RECONCILE_MACHINE = 'ace-win-1'`, `$env:EQ_MACHINE = 'ace-win-1'`,
  and `$env:EQ_HOST_OVERRIDE = 'ace-win-1'` for the session. Keep the existing
  user-level reconcile override if present. These variables serve different scripts;
  one does not substitute for the others.
- Do not add a raw-hostname mapping to tracked code or config.
- Do not prune linked worktrees, drop stashes, delete branches, or stash dirty sibling
  repos unless ownership is proven and the user separately approves the exact action.
- Preserve unrelated parallel work. Never sweep it into the reconciliation commit.
- Existing issue/plan gates remain load-bearing. If repo code needs a fix, file or use
  a GitHub issue, plan it, run adversarial plan review, and wait for explicit user
  approval before implementation. Never self-label `status:plan-approved`.

## Required startup

1. Locate the live checkout (historically `D:\ws\workspace-hub`) and enter it.
2. Read `config/agents/codex/MEMORY.runtime.md` and the complete skill files:
   - `.claude/skills/workspace-hub/ecosystem-equivalence-reconcile/SKILL.md`
   - `.claude/skills/workspace-hub/session-curation/SKILL.md`
   - `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`
3. Check parallel work before mutation:

   ```powershell
   git status --short --branch
   git worktree list --porcelain
   Get-ChildItem .. -Directory | ForEach-Object {
       if (Test-Path (Join-Path $_.FullName '.git')) {
           git -C $_.FullName status --short --branch
       }
   }
   ```

4. If `workspace-hub` is clean, fast-forward only. If it is dirty, inspect and
   preserve the work; do not assume it belongs to this task.

## Reconciliation sequence

Run report-first, then apply only the skill's auto-safe subset:

```powershell
$env:RECONCILE_MACHINE = 'ace-win-1'
$env:EQ_MACHINE = 'ace-win-1'
$env:EQ_HOST_OVERRIDE = 'ace-win-1'
bash scripts/readiness/reconcile-ecosystem.sh
bash scripts/readiness/reconcile-ecosystem.sh --apply
```

Review every `NEEDS-APPROVAL` and `OPERATOR-ONLY` item individually. A clean or recent
linked worktree is expected parallel state, not cleanup residue.

### Agent runtime

```powershell
bash scripts/agents/build-soul-runtime.sh
bash scripts/enforcement/check-soul-runtime-drift.sh
bash scripts/agents/install-soul-runtime.sh
```

On this Windows box, `core.symlinks=false` is intentional because native symlink
creation is unavailable. Git Bash may report `LINK` while materializing a regular
file. Verify content and `LinkType`; do not set `core.symlinks=true` or claim a real
symlink without evidence.

### Windows scheduled tasks

Run the installer from an elevated PowerShell window:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\setup-scheduler-tasks.ps1
Get-ScheduledTask -TaskPath '\Claude\' |
    Sort-Object TaskName |
    Select-Object TaskName, State, Actions
```

Expect seven `Ready` tasks when the installer can resolve the public machine label:
`ContextManagementDaily`, `EqualityReport`,
`HarnessUpdate`, `MemoryBridgeSync`, `NightlyReadiness`, `RepoSync`, and
`WorkstationVersionCheck`.

If the installer rejects the private hostname, stop. Do not patch in that hostname.
It may already have registered the first six tasks before rejecting `EqualityReport`,
so verify rather than rerunning blindly. Route a PII-safe `-Machine`/environment
override through a GitHub issue and the normal plan/TDD/review/user-approval gate.

### Session curation and freshness

The current Windows wrapper needs UTF-8 forced because its engine prints a Unicode
delta character under a cp1252 console. On ace-win-1, do not run the full wrapper until
its final collector accepts the PII-safe machine override. Run the leak-safe curation
components explicitly:

```powershell
$env:PYTHONUTF8 = '1'
$env:EQ_MACHINE = 'ace-win-1'
$env:EQ_HOST_OVERRIDE = 'ace-win-1'
uv run --no-project --with pyyaml python scripts/curation/curate_session_memory.py
uv run --no-project --with pyyaml python scripts/skills/generate_skills_index.py
uv run --no-project --with pyyaml python scripts/curation/audit_skill_currency.py
uv run --no-project --with pyyaml python scripts/curation/detect_skill_drift.py
uv run --no-project --with pyyaml python scripts/curation/audit_memory_freshness.py
bash scripts/skills/resync-skill-links.sh --machine ace-win-1
```

If the collector reports that `origin/main` advanced, fetch and inspect overlap, then
use `git pull --rebase --autostash origin main` only when the local changes are known
generated curation artifacts. Rerun curation after the checkout is current.

### Equality collection and publication

Do not use the Bash equality publisher on Windows: `publish-equality.sh` requires
`flock`, which Git Bash does not provide and can falsely report another publisher in
flight. Use the Windows-native path only after confirming the identity/privacy guard:

```powershell
$env:PYTHONUTF8 = '1'
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\readiness\collect-equality.ps1 -Machine ace-win-1
```

Before staging or publishing, inspect `.claude/state/equality-ace-win-1.yaml` and run
the legal scan. The `host:` field must not contain the private OS hostname. If it does,
stop and preserve the file locally; do not hand-edit and publish a recurring leak.
The existing `refresh-equality-matrix.ps1 -Machine ace-win-1` route is not trustworthy
until its parameter is verified end-to-end against `equality-report.ps1`.

Windows scheduler evidence has a known measurement gap: the canonical Bash collector
skips scheduler enumeration when `OS=windows`, so it emits `job_count: 0` even when the
seven native tasks are verified `Ready`. Treat Task Scheduler output as machine truth;
do not repeatedly reinstall tasks to chase that cell. Any collector fix requires its
own issue, approved plan, TDD, and adversarial code review.

## Commit and push

Inventory the diff and stage only ace-win-1 reconciliation evidence plus this handover
if it legitimately changed. Exclude unrelated repo/session state. Run:

```powershell
bash scripts/legal/legal-sanity-scan.sh --diff-only
git diff --check
git diff --cached --name-only
```

Use a conventional, path-scoped commit. Pull/rebase with autostash only after checking
remote overlap. Push, then verify `git status --short --branch` and the remote commit.
On a rejected push, inspect `git reflog` before any retry because auto-sync may have
pushed or moved `main` silently.

## Closeout

Run the reconciler once more in report-only mode and then the mandatory pre-completion
cleanup audit. Report:

1. current state and exact commands/results;
2. commit and push SHA, or why no commit was needed;
3. preserved active worktrees/dirty sibling state;
4. remaining real blockers, separated from Windows collector false negatives;
5. the next checkpoint for any issue-gated code fix.

Do not claim full equivalence while `OPERATOR-ONLY`, PII-blocked, or empirically
unmeasured cells remain.
