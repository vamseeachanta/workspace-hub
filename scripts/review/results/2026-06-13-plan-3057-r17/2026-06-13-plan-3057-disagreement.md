# Disagreement report — plan #3057 (2026-06-13)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MINOR |
| codex | MINOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **One of the three core defects (notification-purge duplicate/re-add) has no reproduction proof, violating the plan's own Step 1.5 "reproduce alleged failure" gate.** The Evidence section reproduces env-line preservation (lines 178-184), `render_block` output (194-199), cron-health clearing (206-209), and timeouts (212-217) — but never demonstrates that today's `cron_apply.py --apply`/dry-run actually produces a duplicate `notification-purge` line or trips the rollback guard. This defect drove the most plan churn (r8→r12) yet is asserted from review reasoning, not observed failure. The catalog query at line 231 only proves the task *lacks a script token*; it does not prove the duplicate manifests. Recommend adding a dry-run repro showing either the duplicated managed+loose line in `new_text` or a `status=rolled-back`.
- **Stale/contradictory comment in `config/workstations/harness-state-classes.yaml:126` left unaddressed.** The existing comment states "Appears DUPLICATED in a1's crontab; **the cutover dedups it** — this entry only ensures it classifies preserved." This directly contradicts the plan's premise (the whole r8-r10 thread) that cutover currently does *not* dedup the catalog-owned line and instead re-adds a duplicate. The Files-to-Change row for this file (line 530) says only "annotate/narrow it as catalog-owned (`catalog_task_id: notification-purge`)" and does not call out correcting this misleading comment. Either the comment is wrong (fix it in the same edit) or the duplicate bug doesn't exist (Finding 1). The plan should reconcile the two.
- **The hygiene-timeout completion acceptance is unproven and fully deferred to closeout.** Acceptance criterion (line 610) and Risk (line 743) require the live governed-set audit to finish inside `TOTAL_TIMEOUT_SEC=480` with `incomplete_due_to_deadline=false`, but the only timing evidence is **warm-cache 16.13s** (plan itself flags this at line 266 as "not worst-case proof"); the ~170s cold-cache figure is hand-extrapolated from 2 sampled repos. The 120s buffer below the 600s gap is real but the acceptance depends entirely on a closeout step that, if it fails cold-cache, forces a re-plan rather than a code fix. Acceptable to approve, but the criterion is currently a promise, not a verified fact.
- **The Artifact Map's "No-MAJOR plan reviews: r5" row (line 309) is misleading.** r5 (round 5 of 16) was the single no-MAJOR round; r6 through r16 every subsequently surfaced MAJOR findings, invalidating r5's clean status. Listing r5 under "No-MAJOR" without noting it was superseded by 11 later rounds (the plan body acknowledges this at line 9 and 687, but the Artifact Map row does not) risks a future reader treating r5 as standing approval evidence. Minor labeling cleanup.

### codex

- `docs/plans/2026-06-13-issue-3057-cron-hygiene-hardening.md:307-308` has two `Failed plan reviews` Artifact Map rows with overlapping content; the first omits r16 and the second includes r16. This is stale/duplicated traceability and should be collapsed before promotion so reviewers and the issue comment do not cite ambiguous artifact sets.
- The plan/index is not yet git-tracked even though `docs/plans/README.md:203` points to `docs/plans/2026-06-13-issue-3057-cron-hygiene-hardening.md`: `git ls-files --error-unmatch` reports the plan is unknown to git, and `git status` shows the plan plus r17 artifacts as untracked. This is not a content blocker because `docs/plans/2026-06-13-issue-3057-cron-hygiene-hardening.md:625` requires commit/push before `status:plan-review`, but fresh non-inline Codex review would violate `config/agents/codex/AGENTS.runtime.md:139-143` unless the plan is pushed first.

