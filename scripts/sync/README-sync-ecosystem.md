# sync-ecosystem — sync every repo in the ecosystem

Two equivalent drivers that commit/pull/push (or just pull, or just report) across **every git repo
in the ecosystem**, resolving the ecosystem root by detection rather than assuming a fixed layout.

| Host OS | Driver | Why |
|---|---|---|
| Linux / macOS | `scripts/sync/sync-ecosystem.sh` | Native bash; canonical cross-platform path. |
| Windows | `scripts/sync/sync-ecosystem.ps1` | Git Bash launch can hang on some Windows hosts (ace-win-2: stale `D:` / UNC cwd stalls bash startup — see memory `project-windows-bash-launch-hangs`). PowerShell + git CLI is reliable there. The `.sh` also works under Git Bash where bash launches cleanly. |

## Why not `scripts/repository_sync`?

`repository_sync` hardcodes `WORKSPACE_ROOT` to `workspace-hub` and expects each repo at
`workspace-hub/<repo>` (nested layout). On hosts where the repos are **independent clones sibling to
workspace-hub** (e.g. all under the workspace-hub parent dir on ace-win-2), that finds nothing.
`sync-ecosystem` detects which layout is in play:

- **sibling layout** — parent of workspace-hub contains ≥2 git repos (hub + siblings) → root = parent
- **nested layout** — repos live inside workspace-hub → root = workspace-hub

Override detection with `--root <dir>` / `-Root <dir>` or the `WS_ECOSYSTEM_ROOT` env var.

## Modes (identical in both drivers)

| Mode | Per-repo actions | Mutates? |
|---|---|---|
| `full` (default) | `add -u` → commit if staged → `fetch --prune` → `pull --ff-only` → `push` | yes (commits + pushes) |
| `pull` | `fetch --prune` → `pull --ff-only` | no commits/pushes |
| `status` | `fetch --prune` → report branch / ahead / behind / dirty | read-only |

`pull --ff-only` never creates a merge commit; a diverged branch is reported as a **warning**, not a
failure, and that repo is left untouched for manual rebase/merge. Commit message defaults to
`chore(sync): auto-sync <date>` (override with `-m` / `-Message`), matching `repository_sync-auto`.

## Invocation

```bash
# Linux / macOS / Git Bash
bash scripts/sync/sync-ecosystem.sh                 # full sync
bash scripts/sync/sync-ecosystem.sh --mode pull
bash scripts/sync/sync-ecosystem.sh --mode status
bash scripts/sync/sync-ecosystem.sh --dry-run
```

```powershell
# Windows
pwsh -File scripts/sync/sync-ecosystem.ps1                 # full sync
pwsh -File scripts/sync/sync-ecosystem.ps1 -Mode pull
pwsh -File scripts/sync/sync-ecosystem.ps1 -Mode status
pwsh -File scripts/sync/sync-ecosystem.ps1 -DryRun
# If only Windows PowerShell 5.1 is present, swap `pwsh` for `powershell`.
```

## `repository_sync` integration

`scripts/repository_sync` now delegates to `sync-ecosystem.sh` automatically **when it detects a
sibling layout** (the hub has no nested repos, but the hub's parent holds ≥2 git repos). The guard
fires only for the repo-touching, mode-mappable invocations — no args / `sync` / `auto` → `--mode full`,
`pull` → `--mode pull`, `status` → `--mode status` — and is a no-op on the nested (Linux) layout, when
`WS_ECOSYSTEM_ROOT` is set, or for other subcommands. So on this Windows host:

```bash
bash scripts/repository_sync            # detects sibling layout -> exec sync-ecosystem.sh --mode full
bash scripts/repository_sync status     # -> sync-ecosystem.sh --mode status
```

Note the coverage difference once delegated: `repository_sync`'s built-in path is **repos.conf-scoped**,
whereas `sync-ecosystem` is **filesystem-scoped** (every git repo under the detected root). On sibling
layouts the delegated run therefore covers all clones present, not just the repos.conf subset. Non-sync
subcommands (`list`, `commit work`, interactive `menu`, …) are not delegated and still resolve
repos.conf-relative — use the `sync-ecosystem` drivers directly for those on a sibling-layout host.

## Skill-invocation contract

A skill that wants to "sync all repos" should dispatch by OS:

- **Windows** → `pwsh -File scripts/sync/sync-ecosystem.ps1 -Mode <full|pull|status>`
  (fallback `powershell -File ...` when pwsh 7 is absent).
- **Linux/macOS** → `bash scripts/sync/sync-ecosystem.sh --mode <full|pull|status>`.

Detection example: PowerShell available / `$IsWindows` true → use the `.ps1`; otherwise the `.sh`.
Both exit non-zero only when a repo had a hard failure (commit/push), so a skill can gate on exit code.
Both print a final `Done. ok=N warn=N fail=N` line for parsing.
