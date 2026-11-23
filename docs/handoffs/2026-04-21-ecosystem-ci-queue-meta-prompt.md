# Meta-session handoff prompt — ecosystem CI queue (6 issues, priority-ordered)

**Purpose:** a single self-contained prompt a fresh Claude Code session can execute to work the 6 ecosystem CI handoff issues produced by session-4 (2026-04-21). Sequences by priority; enforces user-approval gates at each `status:plan-review` checkpoint; supports resumability across multiple sessions if context exhausts.

**Source session:** `docs/handoffs/2026-04-21-inbox-drive-triage-session-4-handoff.md` (commit `564aeac7c`).

---

## How to use

1. Copy the code block below verbatim into a fresh Claude Code session.
2. The session will begin with issue #2442 (HIGH priority: assethold 7-month zero-CI window).
3. At every `status:plan-review` gate, the session STOPS and notifies you. You review the plan + cross-review artifacts, then either set `status:plan-approved` (session continues) or request changes (session iterates).
4. If the session exhausts context mid-queue, it writes a resume-point handoff and hands off to the next session.

---

## The prompt (copy this block verbatim)

```
Work the 6-issue ecosystem CI queue from workspace-hub session-4 handoff.
Parent context: docs/handoffs/2026-04-21-inbox-drive-triage-session-4-handoff.md
Meta-issue: #2424 (decomposed; close or keep as rollup per user preference).

## Queue order (HIGH first, then Medium, then Low)

1. #2442 — assethold (HIGH; 7-month zero-CI window; YAML parse + deprecated actions)
2. #2433 — worldenergydata (Medium; 22+ collection errors; 3-way path choice)
3. #2437 — workspace-hub baseline-check prune (Medium; WRK→GSD orphan)
4. #2441 — digitalmodel pylife missing dep (Medium; 60+ runs red 16 days)
5. #2443 — achantas-data restore CI (Low; markdown-lint + link-check)
6. #2444 — aceengineer-admin add CI (Low; uv + ruff + black + pytest)

## Per-issue workflow (MANDATORY — do not skip steps)

For EACH issue in the queue order above:

A. READ the issue body in full. Each body contains investigation context +
   recommended fix + workflow-compliant session-entry prompt.

B. FOLLOW the issue's own session-entry prompt verbatim:
   - Load issue-planning-mode skill
   - Verify findings still hold in live state
   - Create plan at docs/plans/2026-04-21-issue-<N>-<slug>.md
   - Run bash scripts/review/cross-review.sh <plan> all --type plan
   - Iterate until no MAJOR verdicts
   - Label the issue status:plan-review

C. STOP. Post a comment on the issue with:
   - Plan commit SHA
   - Cross-review verdicts (Claude/Codex/Gemini)
   - Link to the plan file
   Then MESSAGE THE USER: "Plan #<N> ready for approval at
   https://github.com/vamseeachanta/workspace-hub/issues/<N>.
   Waiting on status:plan-approved transition. Will continue to
   next issue after approval."

D. WAIT for user to set status:plan-approved. Do NOT self-approve. Do NOT
   proceed to the next issue in the queue before current issue is approved.
   (Per memory feedback_never_offer_to_self_label_plan_approved — user-in-loop
   gate is load-bearing across session boundaries.)

E. After user approval, execute the plan per its acceptance criteria.

F. After execution, verify acceptance (run CI / monitor next workflow / etc.)
   and comment pass/fail to the issue.

G. Move to next issue in queue; repeat A-F.

## Cross-cutting rules

- Do NOT bundle multiple issues into a single plan document. Each repo gets
  its own plan file. They are independent per #2424's decomposition.
- Do NOT restore scripts/agents/ or scripts/work-queue/ trees in workspace-hub
  — the 2026-03-25 deletion was intentional (WRK→GSD migration).
- Do NOT restore digitalmodel's fatigue module to pre-2026-03-30 state;
  forward-fix only.
- Do NOT clone assethold from a stale samdansk2 fork; use
  gh repo clone vamseeachanta/assethold or fetch fresh.
- Do NOT lint aceengineer-admin root one-shot invoice scripts; scope to
  src/ + tests/ only.
- Do NOT expose PII (client names, tax IDs, employee data) in any CI logs
  or commit messages, especially for aceengineer-admin + achantas-data work.
- Do NOT restore achantas-data's old python-tests.yml; repo is docs-only now.

## Resumability (context-exhaustion handling)

If context fills up mid-queue (typically after issues 2-3 of 6):

1. Complete the in-flight issue's workflow through step G (verify + comment
   pass/fail).
2. Do NOT start the next issue.
3. Write a resume-point handoff at
   docs/handoffs/2026-04-21-ecosystem-ci-queue-resume-<N>.md with:
   - Which issues are complete (#N, ..., #M)
   - Which issue is next in queue
   - Any cross-issue context that emerged (e.g., a shared fix pattern)
4. Commit + push + notify user with the resume-path.

A future session resumes from that handoff's "Queue order" section, skipping
completed issues.

## Exit criteria

Session is done when ONE of:
- All 6 issues are status:plan-approved AND post-execution CI/validation
  reports comment-confirmed green → post final summary comment on #2424 +
  consider closing it.
- Context exhausts mid-queue → write resume handoff per above.
- User interrupts to redirect.

## Starting point (first action in fresh session)

1. Read docs/handoffs/2026-04-21-inbox-drive-triage-session-4-handoff.md
2. Read issue #2442 (the HIGH-priority first-in-queue)
3. Follow #2442's embedded session-entry prompt from step A above
```

---

## Design rationale

### Why priority order ≠ filing order

The 6 issues were filed in investigation order; the queue runs them in **CI-impact order**. #2442 (assethold) went red on 2025-09-28 and has **never** produced a green run on main — 7 months of zero CI coverage on a repo that should have it. That's a higher-impact repair than repos with recent short breaks, even if the fix itself is smaller.

### Why stop-at-every-gate is mandatory

Per memory `feedback_never_offer_to_self_label_plan_approved.md` (extended 2026-04-21 to cover session-handoff prompts): user-in-loop at `status:plan-approved` is load-bearing across session boundaries. A "work the queue autonomously" prompt that doesn't stop between issues would recreate the exact failure mode session-4 corrected for issues #2433 and #2437 mid-session.

### Why resumability is load-bearing

Each issue goes through Resource Intel → Plan draft → Cross-review (×1-N rounds) → User approval → Execute → Verify. #2017 took 9 cross-review rounds and accumulated 531 lines of plan. If any of these 6 issues triggers a similar cycle, one session won't finish all 6. Explicit permission to hand off mid-queue prevents the session from either (a) forcing through with context pressure, or (b) silently abandoning the queue tail.

### Why the prompt is self-contained

A new session picks this up with zero prior conversation context. It must be readable cold: queue order + per-issue rules + cross-cutting constraints + resume mechanics + exit criteria, all in one prompt. No pointers to "ask the user for the next step" or "use judgment" — those erode the discipline that keeps review cycles converging.

---

## Expected outputs during queue execution

As each issue progresses, the session produces:

- **Plan commits:** one per issue (`docs(plans): #<N> plan v1 — <title>`)
- **Review iteration commits:** zero-to-many per issue (depends on defect rate)
- **Execution commits:** one or more per issue after approval
- **Issue comments:** 2-4 per issue (plan-ready + execution-done + verification-pass/fail)
- **Label transitions:** `status:plan-review` (auto) + `status:plan-approved` (user) + potentially `status:done` (auto after verification)

Aggregate for the 6-issue queue, if clean: ~12-20 commits, ~15-25 issue comments, 6 label-flip events expected from user.

---

## Cross-reference

- **Session-4 handoff:** `docs/handoffs/2026-04-21-inbox-drive-triage-session-4-handoff.md`
- **Session-4 report:** `.planning/reports/20260421-session-4-report.md`
- **Meta issue:** https://github.com/vamseeachanta/workspace-hub/issues/2424
- **The 6 handoff issues:** #2433, #2437, #2441, #2442, #2443, #2444
