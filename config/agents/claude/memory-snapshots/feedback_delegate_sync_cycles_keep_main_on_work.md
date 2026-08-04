---
name: feedback_delegate_sync_cycles_keep_main_on_work
description: "Main session does analysis and decisions; sync/wait cycles (merge babysitting, check polling, agent progress, telemetry) go to subagents or background watchers"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 19c1569d-4a9e-4d87-bd34-50c2605be4d1
  modified: 2026-08-03T03:16:49.830Z
---

Owner directive, 2026-08-02: *"check and maintain telemetry so you take care of the workflow sync cycles using subagents and we can focus on actual work using main agent."*

**Why:** in one long session the main context was repeatedly spent on *waiting* rather than *deciding* — polling `gh pr checks`, babysitting merges, re-checking agent output sizes, re-running `git status` against a stalling FUSE mount. Every one of those is a sync cycle with no judgement in it, and each consumed main-session context that the actual engineering needed. Context parity = compute parity; burning it on polling is the same waste as burning tokens.

**The split:**

| Main session | Delegate / background |
|---|---|
| Reading findings, deciding, correcting the plan | Merge babysitting (`merge-when-clean.sh --merge`) |
| Verifying subagent citations before relaying | Polling PR checks for CLEAN |
| Writing plans, applying review findings | Waiting on agent reports (`Monitor`) |
| Anything needing a judgement call | Telemetry collection, status sweeps, repo-sync |
| Talking to the user | Re-running measurements on a quiet box |

**How to apply:**
- **Never foreground a wait.** If about to poll, switch to `Monitor` with an until-loop or `Bash run_in_background`. This is already the `model-routing.md` corollary 5 rule; this directive extends it from merges to *every* sync cycle.
- **Monitors must watch for death, not just success.** A watcher that only greps for the good outcome stays silent through a crashloop, and silence reads as progress. Include the terminal-failure signals.
- **Dispatch discovery to Codex subagents**, keep synthesis in main. Token-heavy reading, suite runs, and inventory sweeps are subagent work.
- **Serialise timing measurements.** Learned the hard way the same day: a wall-clock-measurement agent was dispatched alongside two suite-running agents on one box, and its numbers were invalid — 22 concurrent pytest processes. Parallelise static discovery; run timing alone on an idle machine.
- **Telemetry to maintain**: open PRs and their gate status, running agents and whether they died, dirty-tree/branch state per repo, and box load before dispatching anything that measures time.

**Caveat that still applies:** [[feedback_subagent_write_phantom]] — verify a subagent's claimed writes with `ls` before believing them; and verify cited file:line before relaying a finding, because a real defect at a wrong line is still a wrong report.

Related: [[feedback_delegate_token_heavy_to_codex]], [[feedback_parallel_agents_shared_mutable_tool_path]], [[feedback_absence_of_signal_reads_as_success]], [[feedback_verify_subagent_line_citations_not_just_claims]].
