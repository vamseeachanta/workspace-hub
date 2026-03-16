---
name: workspace-repo-sync-path-issues
description: 'Sub-skill of workspace-repo-sync: Path Issues (+6).'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# Path Issues (+6)

## Path Issues


- Trailing spaces in remote filenames prevent checkout — use `git config core.protectNTFS false` or skip those files
- Long paths: enable `git config --global core.longpaths true`
- Symlinks require admin — use `git config core.symlinks false` as fallback

## Line Endings


- Shell scripts must use LF, not CRLF — verify with `file script.sh`
- Fix: `dos2unix script.sh` or `git config core.autocrlf input`

## MINGW Root Path


- `while [ "$(pwd)" != / ]` loops never terminate on MINGW (root is `/d/`, not `/`)
- Use `WORKSPACE_HUB` env var for path resolution, not runtime `pwd` traversal
- Project key derivation: `pwd` → `/d/workspace-hub/digitalmodel` → `D--workspace-hub-digitalmodel`

## Stash Handling


- Always stash uncommitted changes before pull: `git stash push -m "pre-sync"`
- After pull, `git stash pop` — if conflicts occur, report to user, don't auto-resolve
- Check stash list: `git stash list` to avoid orphaned stashes accumulating

## Force-Pushed Refs


- When submodule remote was force-pushed: `git fetch origin && git reset --hard origin/main`
- Detect divergence: `git rev-list --count HEAD..origin/main` (behind) and `..HEAD` (ahead)
- Never rebase diverged branches — always merge or hard-reset after user confirmation

## Unregistered Submodules


- Check `.gitmodules` before assuming a directory is a submodule
- `git submodule status` shows registered vs unregistered

## .gitignore Conflicts


- When remote adds files matching local .gitignore: `git add -f <file>` to force-track
