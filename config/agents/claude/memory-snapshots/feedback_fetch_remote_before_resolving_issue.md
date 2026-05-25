---
name: fetch-remote-before-resolving-issue
description: "Before implementing a fix for a tracked issue, fetch origin and check whether that issue was already solved and pushed from another machine — local state alone hides it."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 50cc6367-3751-4c5a-900a-58719808a16d
---

Before solving a tracked issue (#NNNN), `git fetch origin` and check whether the issue was **already solved and pushed from another machine**. `git log --all --grep="#NNNN"` and inspect `origin/main` — not just local working state.

**Why:** On 2026-05-23 a full session re-solved issue #2775 (sibling SSoT harness flow) with a `propagate-ecosystem.sh` patch, unaware that a comprehensive, cross-reviewed (Codex r2 + Gemini r2), *tested* solution had been pushed to `origin/main` ~32h earlier on another machine (`scripts/readiness/repair-sibling-sso-flow.py`, `check-sibling-sso-flow.py`, `sync-agent-configs.sh`, full `tests/readiness/` suite). workspace-hub's local main was 6 behind, so the remote solution was invisible until `git fetch` + `git diff HEAD..origin/main`. The duplicate patch had to be dropped wholesale.

**How to apply:** Extends [[feedback_check_parallel_work]] and [[feedback_discovery_first_on_stale_plan_approved]] with a remote dimension: those cover *in-flight local sessions* and *prior local commits*; this covers *already-merged work on origin from a sibling machine*. Trigger whenever a task references an issue number or names a known initiative — fetch first, grep commit messages for the issue ref across `--all`, and read the diff of any behind-commits before writing code. Especially load-bearing on multi-machine setups (ace-linux-1/ace-linux-2) where each machine's local main drifts behind origin and auto-sync can be failing silently (the `queue/.watcher-state/git-pull-failures.count` was at 7).
