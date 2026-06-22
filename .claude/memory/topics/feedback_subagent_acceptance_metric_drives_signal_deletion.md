> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_subagent_acceptance_metric_drives_signal_deletion.md

---
name: feedback_subagent_acceptance_metric_drives_signal_deletion
description: "A \"make grep/metric empty\" acceptance criterion pushes fan-out subagents to delete signal, not just the target; brief them on what to PRESERVE and always orchestrator-verify their edits"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 97f5bdec-e4ac-46ef-9621-afbf4c40dc6c
---

During the 2026-06-09/10 OGManufacturing retirement (#3012/#3019/#3023/#3027), delegating mechanical multi-file cleanups to subagents worked well for *throughput* but **three separate times** a subagent over-removed because its acceptance criterion was "make `git grep <repo>` return nothing":

1. #3019: a subagent's plan + my own `grep -viE 'test'` filter both MISSED `run-all-tests.sh` (gate-relevant, would re-break pushes) and `test_new_module.sh` (its test case covered the removed code → would fail). Caught by orchestrator verification.
2. #3023: a subagent left a SECOND hardcoded repo list in `run-all-tests.sh`'s `--coverage` heredoc — "sourced the SSoT" was true for the named array but not the whole file.
3. #3027: chasing "grep config/ clean," a subagent deleted an entire `drilling` knowledge-domain block (OGM was just its host repo), rewrote historical plan *prose* in a GENERATED dashboard (`provider-kanban.json`), and left a report YAML with stale rollup counters. I reverted all three (reclassified REMOVE→KEEP).

**Why:** a coverage/grep metric cannot distinguish the *target* (stale entries in active lists) from *signal* (audit trails like `registry.yaml`, report data, domain structure, generated artifacts, historical memory/prose). The orchestrator holds the intent the metric can't encode. Subagents optimize the literal criterion.

**How to apply:**
- Brief fan-out subagents on what to **PRESERVE**, not just what to remove. Name the KEEP set explicitly (generated files, audit trails, report data, historical prose) and tell them to FLAG-don't-edit anything ambiguous.
- Prefer "remove from these specific *list definitions*" over "make grep return nothing."
- ALWAYS orchestrator-verify subagent edits with `git diff` (not just their self-report — see [[feedback_subagent_write_phantom]]); for cleanups, eyeball each file's diff for over-removal before committing.
- Don't hand-edit GENERATED artifacts (they regenerate from source) or files whose generator was deliberately left unchanged — revert and let regen handle them, or leave + document.
- Reclassifying a plan's per-file disposition during implementation (REMOVE→KEEP with rationale) is correct and should be documented in the commit/PR, not silently forced to match the original plan. Relates to [[feedback_check_issue_state_before_implementing_on_detached_head]].
