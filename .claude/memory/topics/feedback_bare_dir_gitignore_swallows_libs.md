> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-25
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_bare_dir_gitignore_swallows_libs.md

---
name: feedback_bare_dir_gitignore_swallows_libs
description: "Bare directory patterns in workspace-hub .gitignore (lib/, reports/) silently untrack paths tree-wide; verify git tracking before committing a script fix"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3902ef62-677b-4f6e-9a97-a6fc27b6baf5
---

workspace-hub `.gitignore:45` has a bare `lib/` (Python-boilerplate) pattern that ignores **every** `lib/` dir in the tree. It carries `!`-negations re-including specific ones (`scripts/agents/lib/`, `scripts/coordination/routing/lib/`, `scripts/setup/lib/`, `scripts/review/lib/`) but **missed `scripts/ai/assessment/lib/`** — so the entire Codex/Claude/Gemini quota-query library (`utils.sh`, `providers.sh`, `display.sh`) was untracked even though its parent `query-quota.sh` IS tracked → a fresh clone had a broken quota pipeline (sources `lib/*.sh` that never existed in git).

**Why:** same class as [[feedback_digitalmodel_reports_dir_gitignored]] — a bare directory name swallows unintended paths tree-wide. Cost a full investigation when a statusline/quota fix edited on disk showed no `git diff` (file was gitignored, not "no change"). 88 tracked files live under some `lib/` dir and survive only by negation.

**How to apply:** before committing a script fix in workspace-hub, run `git check-ignore -v <path>` (or `git ls-files --error-unmatch <path>`) if `git diff <path>` is empty after editing. If a bare-dir pattern catches it, add a `!`-negation matching the existing convention rather than `git add -f` one file (siblings sourced together must be tracked as a set). Fixed 2026-05-27 in commit `b5e33ca8` (`!scripts/ai/assessment/lib/`). Related sweep-contamination guard: pathspec-form `git commit -- <files>` ([[feedback_multi_agent_commit_serialization]]).
