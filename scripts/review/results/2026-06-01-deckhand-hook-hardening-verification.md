# Hook hardening — verification (2026-06-01)

> Reviewer: Claude (main-session). Subject: hardened `src/deckhand/hook.py`. Follows adversarial review `2026-06-01-deckhand-hook-adversarial-codex.md` (CHANGES-REQUESTED, ~60 bypasses).

## VERDICT: APPROVE (hardened, fail-closed-first)

Suite **139/139 green** (was 53; +86 bypass-regression tests). Independently re-run + spot-verified by classification and end-to-end `inspect()`:

| Input (permissive config: operator authorized, repo allowlisted) | Result |
|---|---|
| `git push --force origin main` | DENY (destructive) |
| `git push --mirror origin` | DENY (fail-closed destructive) |
| `git push origin :old` (refspec delete) | DENY (branch_delete) |
| `gh api repos/o/r -X DELETE` | DENY (fail-closed destructive) |
| `git push $F origin main` (`$` expansion) | DENY (suspicious) |
| `./git push --force` (path-shadowed) | DENY (suspicious) |
| `git commit -m x` / `git push origin main` / `git status` | ALLOW (engine-gated) |

## Design posture (confirmed)
- **Fail-closed-first:** git/gh-ish commands with shell features beyond a safe grammar (`$`, backtick, newline, `&`, subshell/group, redirection, line-continuation, alias/function defs, path/suffix/dashed tool names) → `unparseable_suspicious` → hard DENY in `inspect()` before the engine. Over-denying is the intended bias.
- **Generic `destructive` class** (mirror/prune/update-ref/stash/reflog/filter-branch/rebase/gc/worktree/remote/submodule/checkout-restore-switch/rm/notes/replace/aborts, and mutation-capable `gh api`/`gh` admin surfaces) is **hard-denied in `inspect()`**, independent of the engine's named-ops list.
- **Named ops** (force_push, branch_delete, tag_delete, repo_delete, release_delete, reset_hard, git_clean) route through `engine.decide` and are denied via `policy.destructive_ops`.
- **Python gate** is AST-based (subprocess/os imports incl. dynamic, `shell=True`, exec/system/popen, constant-folded git/gh argv); `SyntaxError` → fail-closed gate.

## Boundary reminder
This layer is hardened defense-in-depth. The **per-scope fine-grained PAT (no delete/admin, repo-restricted) remains the load-bearing boundary** for anything the classifier cannot enumerate (e.g. unknown `gh` write subcommands default to `write` and rely on the engine + PAT).
