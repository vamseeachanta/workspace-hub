---
name: feedback_infrastructure_work_must_not_crowd_out_delivery
description: "Owner feedback: infrastructure/gate/tooling work became the majority of a session and displaced actual engineering — file findings, don't chase them"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 19c1569d-4a9e-4d87-bd34-50c2605be4d1
  modified: 2026-08-03T08:35:41.836Z
---

Owner, 2026-08-03: *"this non productive work is becoming majority work all the time. Let us open an issue and figure this out later."*

**What happened.** A session that began with dynacard engineering defects (dm#1952 — fabricated fillage, a one-sided classifier, unpropagated load) delivered those early, then spent the remaining bulk of its time on: a pre-push gate, an installer extension point, uv CI caching, a pytest startup tax, a hidden-test-file audit, and a filesystem benchmark. Eight PRs merged, nearly all scaffolding.

Each step was individually justified — a review gate really had been silently advisory, a push gate really couldn't pass, `git describe --dirty` really does take 38 s. **That is exactly the trap.** Infrastructure findings are self-justifying and each one surfaces the next, so the chain never terminates on its own. Nobody has to make a bad decision for the session to end up 80% meta.

**Why it matters:** the owner runs a multi-provider operation on paid quota. Context and tokens spent on tooling are not spent on engineering deliverables, and tooling work has the seductive property of always *feeling* like it unblocks something.

**How to apply:**
- **Default to filing, not fixing.** When infrastructure work surfaces mid-task, write the finding into an issue with its measurement and move on. The measurement is the durable part; the fix can be scheduled. #3787, #3790, #3793 are the right shape — evidence captured, work deferred.
- **Fix inline only when it blocks the actual task.** "Pushes cannot complete" blocked delivery and was worth fixing. "The filesystem is 5× slower" is real, measured, and was *not* blocking — it became a plan draft before anyone asked whether it should be.
- **Watch the ratio explicitly.** If the last several units of work were all tooling, say so and ask before continuing. Do not wait for the owner to notice.
- **A finding chain is not a mandate.** Discovering that a fix exposes a second defect does not authorise pursuing the second. Each hop needs its own justification against the original goal.
- **A cheap measurement is worth taking even when the fix is deferred** — the #3793 benchmark cost two commands and permanently removes the need to re-argue it. Measure, record, stop.

Related: [[feedback_one_task_at_a_time]], [[feedback_delegate_sync_cycles_keep_main_on_work]], [[feedback_epic_wrapup_issues_then_parallel_agents]].
