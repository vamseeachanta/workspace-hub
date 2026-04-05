# Plan Review: WRK-312 — post-merge hook for cross-machine hook sync

## Work Item
ID: WRK-312
Title: feat: post-merge hook — auto-sync git hooks on pull for consistent cross-machine experience
Route: A (Simple)
Priority: High

## Problem Statement

Git hooks live in `.git/hooks/` which is not tracked by git. Every session and
workflow improvement committed to the repo (lean pre-commit, Stop hook cleanup)
reaches other machines via `git pull` for scripts and `.claude/settings.json`,
but the actual installed `.git/hooks/*` files remain stale until someone manually
re-runs the installer.

Impact: WRK-308 lean pre-commit (removes 5-min validate-skills.sh) only reaches
ace-linux-2, acma-ansys05, acma-ws014 if someone manually runs install-skill-validator-hook.sh.

## Proposed Solution

### 1. `scripts/hooks/pre-commit` (tracked)
Canonical lean pre-commit content (3 lines, WRK-308 state):
```bash
#!/usr/bin/env bash
set -euo pipefail
# Pre-commit checks — skill validation moved to nightly cron (WRK-308)
```

### 2. `scripts/hooks/post-merge` (tracked)
Runs after every `git pull`:
```bash
#!/usr/bin/env bash
# post-merge: re-apply canonical hooks after every pull (WRK-312)
REPO_ROOT="$(git rev-parse --show-toplevel)"
bash "$REPO_ROOT/scripts/setup/install-all-hooks.sh" --quiet
```

### 3. `scripts/setup/install-all-hooks.sh` (tracked)
Idempotent installer — copies `scripts/hooks/*` to `.git/hooks/`, sets +x:
```bash
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$REPO_ROOT/scripts/hooks"
HOOKS_DST="$REPO_ROOT/.git/hooks"
for hook in "$HOOKS_SRC"/*; do
  name="$(basename "$hook")"
  cp "$hook" "$HOOKS_DST/$name"
  chmod +x "$HOOKS_DST/$name"
  [[ "${1:-}" != "--quiet" ]] && echo "Installed: $name"
done
```

### Bootstrap (one-time per machine)
```bash
bash scripts/setup/install-all-hooks.sh
```

### Self-perpetuating flow after bootstrap
```
git pull → .git/hooks/post-merge fires → install-all-hooks.sh →
  .git/hooks/pre-commit updated ✓
  .git/hooks/post-merge updated ✓ (self-updates)
```

## Files Changed
- `scripts/hooks/pre-commit` — NEW (tracked canonical)
- `scripts/hooks/post-merge` — NEW (triggers re-install on pull)
- `scripts/setup/install-all-hooks.sh` — NEW (idempotent installer)
- `scripts/skills/install-skill-validator-hook.sh` — UPDATE (delegate to install-all-hooks.sh)

## Risks / Review Questions
1. Does `post-merge` fire on `git pull --no-rebase` (merge strategy)? Yes — it fires after any successful merge, including fast-forwards and `git pull`.
2. Does it fire on `git pull --rebase`? No — rebase uses `post-rewrite` instead. Should we add a `post-rewrite` hook too?
3. `scripts/hooks/` will contain executable scripts — any security concern with auto-installing hooks from a tracked directory?
4. Is Route A correct or should this be Route B (medium) given the self-bootstrapping complexity?

## Acceptance Criteria
- [ ] `scripts/hooks/pre-commit` exists with lean WRK-308 content
- [ ] `scripts/hooks/post-merge` exists — calls install-all-hooks.sh
- [ ] `scripts/setup/install-all-hooks.sh` installs both hooks idempotently
- [ ] After bootstrap + `git pull`, `.git/hooks/pre-commit` matches canonical
- [ ] `time git commit --allow-empty -m test` < 1s
- [ ] Bootstrap command documented
- [ ] `install-skill-validator-hook.sh` updated to delegate
