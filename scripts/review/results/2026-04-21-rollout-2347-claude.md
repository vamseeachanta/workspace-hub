# Review: #2347 — pilot scoping (adversarial)

## Verdict: **MAJOR**

The "pure contradiction detection" framing is materially wrong for at least two of the four in-scope trackers, the scope is not actually bounded to four issues, and the #2405 attestation mechanism is being over-claimed as the evidence layer. The pilot can succeed, but not under the current framing or the shape proposed in the umbrella comment.

## What I actually verified (checklist)

- [✓] Issue #2347 body and the 2026-04-21 framing comment exist as described (`gh issue view 2347`). Body matches the umbrella's summary.
- [✓] Source artifact `docs/reports/2026-04-15-gtm-cross-review-readiness.md` exists and does self-flag #2016/#1669/#117/#191 under "Still needs reconciliation before final approval signoff" (lines 84–90, 103–108). Self-flag claim is accurate.
- [✓] All four target issues are currently OPEN (`gh issue view 2016|1669|117|191 --json state`). None were silently closed during review packaging.
- [✓] Issue #2405 (cited as the evidence mechanism) is CLOSED and shipped — `scripts/review/attest-plan-claims.sh` exists and runs from plan files. So the attestation infra is real, not vaporware.
- [✓] Spot-check of #2016: the body (dated "Last updated: 2026-04-07") marks Demos 1/3/4/5, and sub-issues #1871/#1872/#1873/#1874/#1930/#1931/#1831/#1832/#1809/#1708/#1709 as "Open" / "OPEN" / "Not started". Per `gh`, ALL of those are in fact CLOSED. So the stale-body claim is strongly corroborated.
- [✗] Could NOT verify that the proposed per-tracker `claude -p` shape matches any existing pattern in `scripts/` — the umbrella asserts "existing ~25 CLI integration points" but doesn't name the one this pilot will template from. No precedent cited.
- [✗] Could NOT verify that `gh issue edit` is actually safe/rollback-able under the proposed shape. No dry-run or staging mechanism is proposed; `gh issue edit --body` overwrites atomically with no diff preview beyond what Claude surfaces locally.

## Findings

### 1. [MAJOR] "Pure contradiction detection" is false for #117 and #191

Quote from #2425: *"Pure contradiction detection; validates Claude-as-attestation-checker thesis (#2405)"*. Quote from the #2347 framing comment: *"pure contradiction detection: plan-claim text vs. shipped-artifact reality"*.

Inspecting #117 body (raw `gh api` output): the issue is a GTM **persona + 30-day plan spec** with acceptance criteria like *"Identify 10 target contacts"*, *"Post in relevant communities: SPE LinkedIn group, r/petroleum, O&G Slack channels"*, *"Reach out to 5 warm contacts individually"*. These are **outreach actions**, not shipped artifacts. Whether they're "done" requires semantic judgment against conversation history, email archives, LinkedIn activity — not file/commit lookups.

Per #2016 comment chain (2026-04-10), the *planning* artifacts (`docs/gtm/oil-man-persona.md`, `docs/gtm/gtm-plan-30day.md`) shipped, but the *execution* criteria (contacts identified, outreach sent) did not. An LLM reconciler reading only tracker bodies + file presence will falsely tick the acceptance checkboxes that require ground-truth-about-human-action. This is precisely the failure mode memory's `feedback_mock_vs_live_invocation_divergence.md` warns about, applied to text reconciliation.

**Impact:** the pilot as framed will over-credit #117 and #191, producing misleading tracker bodies that look reconciled but encode a false-positive view of outreach progress.

### 2. [MAJOR] Scope is not actually bounded to 4 issues

The framing comment claims *"Small, bounded scope (4 issues)"*. But #2016's body references at least 30+ sub-issues (#1904, #1932, #1798, #1799, #1831–#1874, #1930, #1931, #1792, #1707–#1709, #1971, #191, #117, #1669, #197, #1834–#1837, #1994, #1993, #108, #1670, #1671, #898). To "reconcile #2016 to shipped reality" requires checking state of every one of those. I spot-checked 21 — at least 10 are CLOSED while #2016's body lists them as "Open". Each of those requires a per-issue state lookup + commit/artifact check before a bullet can be flipped.

And the reverse: #1669/#117/#191 bodies reference *their own* dependency chains. Reconciling #117 means deciding whether its blocker #191 is "done", which means reconciling #191 first — and #191's "done" state depends on whether `docs/gtm/chatbot_fundamentals.md` *satisfies the acceptance criteria*, which is a semantic question (Finding 1).

**Impact:** "4-issue pilot" is actually "30+ sub-issue semantic audit". Cascading scope risk is concrete, not hypothetical.

### 3. [MAJOR] `#2405 attestation` is being over-applied

`scripts/review/attest-plan-claims.sh` extracts `#NNNN` references and file paths from a **plan file under `docs/plans/`** (strict allowlist regex `^docs/plans/[^/]+\.md$`). The target of attestation is a plan. The #2347 pilot has **no plan file yet** (issue body confirms: *"This is a SCOPING review, not a plan-content review"*).

The framing comment in #2347 asserts the pilot will use *"tracker body + attested shipped-evidence block as input"*. But `attest-plan-claims.sh` doesn't attest tracker bodies — it attests plan files. And tracker-body acceptance checkboxes like "Reach out to 5 warm contacts" are not the grep-able `#NNNN` + file-path assertions the script was built to verify. Repurposing #2405's attestation for this pilot requires either (a) writing the plan as a plan-file under `docs/plans/` and running attestation there, OR (b) building a new attestation path for tracker bodies. Neither is acknowledged in #2347 or #2425.

**Quote to falsify:** umbrella #2425 Table says #2347 *"validates Claude-as-attestation-checker thesis (#2405)"*. It cannot validate what it does not actually exercise.

### 4. [MINOR] `gh issue edit` is not idempotent/rollback-safe as proposed

The framing comment shape is: *"User (not agent) approves each rewritten body before `gh issue edit`"*. `gh issue edit --body` overwrites the body atomically. There is no proposal for:

- dry-run diff preview (beyond what Claude renders in terminal — which the user must eyeball)
- pre-edit body capture (so a bad edit can be restored via `gh issue edit --body-file pre-edit.md`)
- post-edit verification (re-read body, compare to expected)

Given memory entry `feedback_gh_issue_close_silent_comment_drop.md` — `gh` has known silent-failure modes on issue operations — this pilot should pre-commit a rollback artifact for each of the 4 targets. Nothing in the current framing does.

### 5. [MINOR] Workflow mismatch with `issue-planning-mode`

Project CLAUDE.md: *"Steps: Issue → Resource Intel → Plan → Adversarial Review → `status:plan-review` → USER APPROVES → `status:plan-approved` → Implement"*. The umbrella table says #2347 is at *"plan-review, 0 plan yet"*. There is no plan file, no plan-review cycle yet, and yet the umbrella already ranks it #1 with full ⭐⭐⭐⭐⭐ fit. The approval gate is load-bearing (`feedback_never_offer_to_self_label_plan_approved.md`), and ranking a pilot before its plan exists risks the "route around user-in-loop" anti-pattern flagged in memory.

### 6. [MINOR] Historical-context risk not acknowledged

#2016 comments span 2026-04-07 → 2026-04-15 with 20+ progress updates. A reconciliation that reads only the current body and the current state of sub-issues will lose the *why* of each checkbox — e.g., the 2026-04-15 comment about production deployment (*"methodology pages ... 404 on production"*) resolved later that same day (`de49d21`). A naive redline that strips "stale" content without reading the full comment thread can erase the legitimate rationale for a still-open item. No comment-thread-ingestion is proposed in the framing.

### 7. [MINOR] #117 body is in legacy `WRK-XXX / Stage 17` schema

`gh api repos/.../issues/117` shows the body is formatted around `<details>` blocks (Implementation Summary / Final Plan / TDD Results / Stage Progress). Memory entry `feedback_no_reserved_wrk_ids.md` says the project abandoned local task IDs. An LLM reconciler that *preserves* the `WRK-470 / Stage 17: Reclaim (n)` scaffolding is propagating a deprecated schema; one that *strips* it may lose acceptance-criteria tracking that hasn't been migrated elsewhere. Either direction is a non-trivial policy call the pilot must make explicit.

## Required changes before pilot kickoff

1. **Split the four trackers by kind.** #2016 and #1669 are candidate for mechanical reconciliation (file-/commit-/issue-state lookups). #117 and #191 need a different path — either drop them from pilot scope, or require human review of every outreach-style checkbox (no auto-tick).
2. **Plan file must exist before ranking.** Move #2347 from "⭐⭐⭐⭐⭐ pilot #1" to "candidate pending plan" until a `docs/plans/2026-04-21-issue-2347-...md` is written and attested.
3. **Adopt a rollback artifact per target.** For each issue, capture `gh issue view N --json body > pre-edit/N.json` and commit it *before* `gh issue edit`, so a silent bad edit is recoverable via `--body-file`.
4. **Clarify attestation scope.** Either (a) write a plan file and run `attest-plan-claims.sh` against it as the attested-evidence block, OR (b) acknowledge that this pilot does NOT use the #2405 mechanism and drop that claim from the umbrella.
5. **Cascading-scope budget.** Enumerate the full set of sub-issues that need a state check (≥30 for #2016 alone), and declare up-front whether the pilot recurses or stops at depth-1. Without this, #2347 will silently absorb days of work.
6. **Ingest the comment thread, not just the body.** The reconciler prompt must include `gh issue view N --json comments` output, not just `--json body`, for every target. Otherwise legitimate context gets stripped.

## What I did NOT check (honesty declaration)

- Did not read #1669's current body in detail — relied on #2016's references to it.
- Did not check #191's body at all — only its state (OPEN) and title.
- Did not attempt a dry-run of the proposed `claude -p` shape against any tracker.
- Did not verify that `scripts/` contains or lacks a template for per-issue `claude -p` invocations — umbrella's "~25 CLI integration points" claim is assumed plausible but not audited.
- Did not check git history on `attest-plan-claims.sh` beyond reading the current file — may have mode flags or extension points I missed.
- Did not evaluate whether Codex or Gemini would be a better pilot-runner for this task than Claude — scope was Claude-CLI-specific.
- Did not check whether a prior pilot of similar shape has run in this repo.
