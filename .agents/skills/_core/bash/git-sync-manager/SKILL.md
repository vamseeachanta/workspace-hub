---
name: git-sync-manager
version: 1.0.0
description: Multi-repository git synchronization and fetch-pull-push patterns for
  batch operations across workspaces
author: workspace-hub
category: _core
tags:
- bash
- git
- sync
- multi-repo
- batch
- automation
platforms:
- linux
- macos
see_also:
- git-sync-manager-1-repository-discovery-from-gitignore
- git-sync-manager-2-multi-phase-sync-pattern
- git-sync-manager-3-repository-status-check
- git-sync-manager-5-safe-branch-operations
- git-sync-manager-1-always-check-before-operating
---

# Git Sync Manager

## When to Use This Skill

✅ **Use when:**
- Managing multiple Git repositories from a central location
- Performing batch git operations (pull, commit, push)
- Need consistent sync workflows across many repos
- Automating daily/periodic repository synchronization
- Building repository management CLIs

❌ **Avoid when:**
- Single repository operations
- Complex merge/rebase workflows requiring manual intervention
- Repositories with conflicting changes that need resolution

## Large-Repo / Concurrent-Agent Safety Rules

When syncing very large repos or repos actively handled by Codex/Codex/Gemini workers:

1. **Preflight active writers first**: inspect `ps`/`/proc/<pid>/cwd` for active `Codex`, `codex`, `git checkout`, `git status`, `git commit`, `git merge`, `git rebase`, `git pull`, or `git push` processes. If a worker is operating inside the target repo, do not interrupt it or mutate that repo.
2. **Use no-untracked status by default**: prefer `git -c status.showUntrackedFiles=no status --short --branch --untracked-files=no`; never use `git status -uall` on huge repos unless explicitly justified.
3. **Respect locks**: treat `.git/index.lock`, `.git/HEAD.lock`, `MERGE_HEAD`, `rebase-merge/`, and `rebase-apply/` as stop signs. Do not delete locks automatically during scheduled sync.
4. **Backup before staging**: for dirty tracked changes, write `git diff --binary HEAD` and no-untracked status output under `.git/recovery-backups/` before `git add -u`.
5. **Prefer fast-forward-only pulls**: use `git fetch origin --prune` then `git pull --ff-only`/`git pull --ff-only origin <default-branch>`; do not use scheduled `--rebase --autostash` when concurrent workers may exist.
6. **Sparse checkout**: if a path exists on GitHub but is missing locally, use `git ls-tree origin/<branch> <path>` then `git sparse-checkout add <path>`. Do not run `git sparse-checkout disable` on very large repos without explicit approval; it can materialize hundreds of thousands of files and hold the index lock for a long time.

## Complete Example: Repository Sync CLI

Full implementation combining all patterns:

```bash
#!/bin/bash
# ABOUTME: Complete multi-repository sync manager
# ABOUTME: Provides pull, commit, push, sync, and status operations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(dirname "$SCRIPT_DIR")}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────────
# Repository Discovery
# ─────────────────────────────────────────────────────────────────

declare -a REPOS=()
declare -A CATEGORIES=()

*See sub-skills for full details.*

## Resources

- [Git Reference](https://git-scm.com/docs)
- [Bash Arrays](https://www.gnu.org/software/bash/manual/html_node/Arrays.html)
- [Associative Arrays in Bash](https://www.gnu.org/software/bash/manual/html_node/Arrays.html)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - extracted from workspace-hub repository sync scripts

## Sub-Skills

- [1. Repository Discovery from .gitignore](1-repository-discovery-from-gitignore/SKILL.md)
- [2. Multi-Phase Sync Pattern](2-multi-phase-sync-pattern/SKILL.md)
- [3. Repository Status Check (+1)](3-repository-status-check/SKILL.md)
- [5. Safe Branch Operations](5-safe-branch-operations/SKILL.md)
- [1. Always Check Before Operating (+4)](1-always-check-before-operating/SKILL.md)
