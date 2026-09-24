---
name: crossprovider gemini auto-sync-phase-sequencing-parallel-submodule-co
description: Auto-sync phase sequencing: parallel submodule commits before hub push
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, git, bash-scripting, multi-repo]
---

Two-phase workflow: Phase 1 executes parallel per-repo `git add -A && git commit` in subshells, writing results to temp files; Phase 2 runs after all subshell waits complete, then syncs workspace-hub. This ensures submodule commits land before hub references them. Use temp result files with pipe-delimited status (repo|staged|committed|pushed|result) for aggregation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
