> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-23
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_bwrap_transient_under_concurrency.md

---
name: codex-bwrap-uid-map-failure-is-transient-under-concurrency
description: "\"bwrap: setting up uid map: Permission denied\" is an intermittent concurrency symptom, not a hard break — retry; cap concurrent codex sandboxes conservatively"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

`codex exec` intermittently fails ALL shell commands with `bwrap: setting up uid map: Permission denied` when **many Codex sandboxes spin up concurrently** (e.g. 3 ingests + a subagent + reviews at once, 2026-05-27). It is **transient**, not a hard limit:

**Diagnosed 2026-05-27:** `user/max_user_namespaces` = 127829 (not exhausted), `kernel.unprivileged_userns_clone` = 1 (enabled), **0 leaked bwrap procs** — yet a batch was fully blocked. A trivial `codex exec` retry seconds later, after concurrent load cleared, **succeeded immediately**. So it's contention/race in userns setup under concurrency, not exhaustion or a reverted AppArmor profile.

**How to apply:**
- On `bwrap: setting up uid map: Permission denied`, **retry the codex exec** (after a short pause / once concurrent load drops) before assuming a sandbox break ([[feedback_codex_sandbox_write_blocked]] / #2804 is the AppArmor-profile case — check `aa-status` only if retry also fails).
- **Cap concurrent Codex conservatively**: ≤3 sandbox-spawning sessions, and do NOT stack reviews/subagents on top of 3 ingests. The user's "one-by-one before 3" cadence is partly why — high fan-out trips bwrap.
- A **batching dispatcher must build in retry-on-transient-bwrap + a concurrency cap**, or batches will spuriously "fail" mid-run (the DNV hardened batch did nothing but reported blocked; re-ran clean single).
- First check on a blocked batch: `pgrep -c bwrap`, `cat /proc/sys/user/max_user_namespaces`, and a trivial retry — distinguishes transient (retry) from real (AppArmor/sysctl).

Related: [[feedback_codex_exec_cwd_is_sandbox_root]], [[feedback_delegate_heavy_work_to_codex_for_tokens]].
