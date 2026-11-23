---
name: learned-git-worktree-hook-path-and-real-hook-shape-review
description: Catch hook-installation and governance bugs that only appear in linked git worktrees or against the real generated hook shape, not simplified test fixtures.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Git worktree hook path + real hook shape review

Use when:
- A repo uses linked git worktrees
- Hook installers write to `.git/hooks/...`
- Tests use simplified hook fixtures
- A change appears correct in unit tests but may fail against the actual installed hook
- Reviewing governance/enforcement hook chains in workspace-hub-style repos

## Core lesson
Two classes of bugs were caught only by adversarial review:
1. Worktree hook path bugs: `git rev-parse --git-dir` points to `.git/worktrees/<name>` in linked worktrees, but shared hooks live under `git-common-dir/hooks`.
2. Real-hook-shape bugs: installer regex/patch logic matched synthetic fixtures but failed against the actual indented early-exit structure in the shipped hook.

## Review checklist
1. Verify actual git topology
   - Run:
     - `git rev-parse --git-dir`
     - `git rev-parse --git-common-dir`
     - `git rev-parse --git-path hooks`
   - If the repo is a linked worktree, never assume `REPO_ROOT/.git/hooks` is valid.

2. Audit hook config trust boundaries
   - Do not source a repo-tracked file from a path that is itself writable before approval.
   - Prefer trusted runtime config from the resolved hooks dir, inherited env, or other non-workspace-local source.
   - Specifically check whether a “safe path” can be edited first to disable later enforcement.
   - If a repo-tracked template (for example `scripts/enforcement/enforcement-env.sh`) is also on an allowlist/safe path, treating it as runtime authority creates a trivial self-bypass. Use the installed local hooks copy as authority, not the workspace template.

3. Test against the real installed hook shape
   - Do not rely only on synthetic fixtures.
   - Seed at least one test from the actual current hook text or an equivalent fixture that preserves:
     - indentation
     - early exits
     - stdin buffering
     - real variable names / flow
   - For pre-push hooks, include the real “no tier-1 repo changes” early-exit path if it exists.

4. Check reachability before every exit path
   - Search the live hook for every `exit`.
   - Confirm installer-injected logic runs before all relevant exits, not just the final exit.
   - If a hook buffers stdin/OIDs early, insert governance checks after buffering but before repo-selection early returns.

5. Add negative tests for false confidence
   - Worktree topology test: linked worktree must resolve/install/read trusted hooks correctly.
   - Safe-path bypass test: unapproved workspace-local config must not disable enforcement.
   - Real-shape test: indented early-exit blocks must still be detected and guarded.

## Implementation patterns

### Worktree-safe hook resolution
Prefer:
- `git rev-parse --git-path hooks` when you need the resolved active hooks directory
- `git rev-parse --git-common-dir` when constructing shared-hook paths in linked worktrees
- `git rev-parse --git-dir` only as a fallback, not the primary source of hook paths

Avoid hardcoding:
- `REPO_ROOT/.git/hooks/...`
- `$(git rev-parse --git-dir)/hooks/...` without checking worktrees

Additional lesson:
- Installer scripts must be worktree-safe too, not just runtime hooks. A hook can correctly read trusted config from the common hooks dir while the installer still fails because it writes to `REPO_ROOT/.git/hooks/...` from a linked worktree where `.git` is a file.
- Add at least one regression test that runs the installer from a linked worktree and verifies it updates the shared hooks dir successfully.

### Installer patching pattern
When modifying an existing hook:
1. Identify where stdin/ref buffering happens
2. Insert governance blocks after buffering
3. Insert them before any early exit that would skip intended enforcement
4. Use explicit managed block markers for idempotent replacement
5. Re-test against both synthetic and real-hook-shaped fixtures

## Red flags
- Tests pass, but only with simplified fixtures
- Hook reads a repo-local config file from an allowlisted path
- Installer uses regexes assuming no indentation
- Hook installer writes to `.git/hooks` directly in a worktree-based workflow
- Docs say “verified” while only synthetic tests exist

## Minimal verification commands
- `git rev-parse --git-dir && git rev-parse --git-common-dir && git rev-parse --git-path hooks`
- `uv run pytest <targeted-hook-tests> -q`
- Temp linked-worktree repro proving install/read behavior works end-to-end
- Manual simulation using the actual current hook content where practical

## When to stop
Do not approve if any of these remain true:
- Trusted hook config is unreadable from linked worktrees
- Governance chain is still bypassed by a real early-exit path
- A workspace-local editable file can disable enforcement before approval
- Only synthetic fixtures cover the changed installer path
