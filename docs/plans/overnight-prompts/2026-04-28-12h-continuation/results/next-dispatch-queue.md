# Next-dispatch queue — Lane C1 reconciler output

Generated: 2026-04-28 ~22:00 CDT, ace-linux-1.
Stop target: 2026-04-29 09:49:46 CDT.

For each lane, the prompt below is **drop-in ready** for a downstream lane to consume on the next dispatch wave. None of these prompts launch a new process; the existing 6-lane batch (C1-C3 / D1-D3) already runs.

## Lane health snapshot (read first)

| Lane | Session | Latest evidence | Classification |
|---|---|---|---|
| C1 | ace1-control-feed-20260428 | this file + control-reconciler.md + github-command-pack.md | RUNNING (this lane) |
| C2 | ace1-gtm-feed-20260428 | results/ace1-gtm-packager.md (pending) | RUNNING — feed it #2346 evidence + #2515 demo angle |
| C3 | ace1-plan-hardener-20260428 | results/ace1-plan-review-hardener.md (pending) | RUNNING — feed it #2510 r14, #2490 r1, #2548/#2525/#2524/#2523 plan skeletons |
| D1 | ace2-digitalmodel-feed-20260428 | (pending — last known: B1 BLOCKED on env) | LIKELY BLOCKED — needs env diagnosis or ace1 takeover for #2515 |
| D2 | ace2-knowledge-feed-20260428 | (pending) | RUNNING — feed it Batch Pack approval-drift collapse |
| D3 | ace2-review-feed-20260428 | (pending) | RUNNING — feed it false-completion sweep on #2462/#2458/#2346/#2269 |

> Cannot probe live tmux from this lane (sandbox blocks `tmux ls` and `ssh ace-linux-2 ...` in unattended mode). Reconciler operator should verify with `tmux ls; ssh ace-linux-2 tmux ls` at next morning check.

---

## Drop-in lane prompts (next wave)

The following are exact next prompts to consume. Each preserves write-isolation, plan-gate respect, and evidence-boundary rules. **None self-approve, close, merge, or force-push.**

### Prompt for Lane C2 (GTM packager) — next 4-hour slice

```
Continue Lane C2 — GTM packager — for the 12h window ending 2026-04-29 09:49 CDT.

Authoritative evidence to packagize this slice:

A. #2346 prospect-data demo pipeline: Codex commit 44735e979a in branch
   codex/10thread-20260428-issue-2346 added demo_03 inputs to
   scripts/gtm/prospect_adapter.py. Read the diff with:
     git show 44735e979a -- scripts/gtm/prospect_adapter.py
   Use only the diff as evidence. Translate into one outbound snippet:
   "ACE can stand up a customized prospect demo in 48hr from a 1-page brief"
   with the exact files-changed boundary as the can-say-now claim.

B. #2515 cross-section reports plan: approved 2026-04-28T17:26 (commit
   b711f3b46b). Plan path:
   docs/plans/2026-04-27-issue-2515-cross-section-reporting-demo.md
   Read the deterministic outputs section. Translate the deterministic
   subset (NOT the in-flight implementation) into a "client-ready
   cross-section deliverable" GTM brief with the boundary
   "implementation in flight; deliverable schema locked".

C. #2462 / #2458 push evidence: digitalmodel branches
   codex/burn-20260427-issue-2462 (head 4ad99a36af) and the #2458 burn
   branch. Translate into a GTM angle: "operator-map / multi-body fixture
   coverage shipped across digitalmodel" — boundary is "pushed to branch,
   PRs not yet open".

D. Semiconductor lane #2510: STOP. Plan still under review (r13). DO NOT
   convert to GTM material this wave; record as "engineering-readiness
   pending" only.

Allowed writes (lane-isolated):
- docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-gtm-packager.md
- docs/gtm/overnight-client-ready-material-2026-04-28.md
- docs/gtm/outreach-candidate-briefs-2026-04-28.md

Write 5-7 candidates. For each: buyer, ACE proof path, can-say-now,
cannot-claim-yet, missing proof, next repo issue or action. End with a
ranked GTM push list for morning. No external send.
```

### Prompt for Lane C3 (plan-review hardener) — next 4-hour slice

```
Continue Lane C3 — plan-review hardener — for the 12h window ending
2026-04-29 09:49 CDT.

Five concrete plan-review tasks queued for this slice:

T1. #2510 r14 — chip CAD demo plan stuck since r13 (2026-04-27 10:36).
    Plan: docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md
    Read the most recent review artifacts in scripts/review/results/
    matching plan-2510-*.md. Identify the single specific finding that
    has not been folded back into the plan. Write a r14 plan-edit pack
    proposing exact diff hunks (NOT applied). Per memory
    feedback_codex_sustained_major_loop: if Codex has had MAJOR for 3+
    rounds while Claude/Gemini are MINOR, surface this as a
    consensus-vs-minority decision instead of auto-cycling.

T2. #2490 r1 — coverage-gate plan draft pushed 2026-04-27 17:07
    (commit f14872956b, plan
    docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md).
    No cross-provider review yet. Run the standard adversarial pass
    (read plan, list defects with severity, propose acceptance bar).
    Write the result to scripts/review/results/2026-04-28-plan-2490-claude-r1.md
    (this is the conventional review-results path).

T3-T6. Plan skeletons for the four NEEDS_PLAN priority seeds:
    - #2525 Codex burn-down controller — `docs/plans/2026-04-28-issue-2525-codex-burn-down-controller.md`
    - #2548 control-plane machine inventory + OrcaFlex/AQWA dispatch — `docs/plans/2026-04-28-issue-2548-machine-inventory-dispatch.md`
    - #2524 machine-aware dispatch ledger — `docs/plans/2026-04-28-issue-2524-machine-dispatch-ledger.md`
    - #2523 Hermes preflight readiness checker — `docs/plans/2026-04-28-issue-2523-hermes-preflight.md`

For each skeleton: scope, in/out, dependencies (note overlap among
#2519 / #2523 / #2524 / #2525 / #2548), test plan, rollout, rollback.
Mark each "PLAN DRAFT — NOT APPROVED". Do NOT add labels. Do NOT post
issue comments without operator review.

Allowed writes:
- docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-hardener.md
- docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/plan-review-command-pack.md
- (add) the four plan skeletons under docs/plans/2026-04-28-issue-*.md
- (add) review artifact for #2490 under scripts/review/results/

If commit-on-write hooks complain, write to the path and let the
auto-sync loop handle the commit. Do not bypass hooks.
```

### Prompt for Lane D1 (ace-linux-2 digitalmodel/offshore) — next slice

```
Continue Lane D1 — ace-linux-2 digitalmodel/offshore overflow.

Reconciler classified D1 as LIKELY BLOCKED on env (B1 last comment
2026-04-29T02:28Z). DO NOT attempt to repeat the blocked write path.

Two safe slices for this window:

S1. Diagnose the env mismatch concretely. Write a blocker report at
    /mnt/local-analysis/ace2-worker-reports/ace2-2515-env-blocker-20260428.md
    listing:
    - exact path the sandbox forbid writing,
    - whether digitalmodel/ subrepo is mounted at the expected location,
    - whether `git -C digitalmodel status` works,
    - candidate paths for a write-capable worktree on ace-linux-2.

S2. For each of #2462 / #2458, do read-only PR-readiness verification
    on ace-linux-2 (which has digitalmodel cloned). Capture per issue:
    - branch present? (`git fetch && git log -1 origin/<branch>`)
    - tests pass? (`uv run pytest -q -k <approved subset>`)
    - regression file list match the plan?

    Write to results/ace2-digitalmodel-overflow.md.

Do not implement code on issues #2515/#2462/#2458 — their
implementation belongs to lanes that own write authority for those
target repos.

Stop conditions: env still blocking after S1 → write blocker, do not
retry.
```

### Prompt for Lane D2 (ace-linux-2 knowledge/doc-intel) — next slice

```
Continue Lane D2 — ace-linux-2 knowledge/doc-intel overflow.

Single highest-value collapse this window: the recurring approval-drift
gate on Batch Packs.

Tasks:

P1. Inventory approval markers across:
    .planning/plan-approved/2402.md
    .planning/plan-approved/2364.md
    .planning/plan-approved/2369.md  (if present)
    .planning/plan-approved/2373.md  (if present)
    .planning/plan-approved/2368.md  (if present)
    .planning/plan-approved/2403.md  (if present)
    For each, capture: marker SHA vs plan HEAD SHA. List the drift.

P2. Cross-reference each plan path to the canonical issue scope. Write
    a single command pack at
    /mnt/local-analysis/ace2-worker-reports/ace2-batchpack-marker-rebind-20260428.md
    that proposes (does NOT execute) the marker-rebind diffs.

P3. NEW — issue #2540 was in the focus list. Re-read its current
    state and add a one-paragraph status to results/.

DO NOT mutate `.planning/plan-approved/*` files. The decision is
human-in-loop per memory feedback_never_offer_to_self_label_plan_approved.

Allowed writes:
- /mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace2-knowledge-docintel-overflow.md
- /mnt/local-analysis/ace2-worker-reports/ace2-batchpack-marker-rebind-20260428.md
```

### Prompt for Lane D3 (ace-linux-2 adversarial review + GSD hygiene) — next slice

```
Continue Lane D3 — adversarial review + GSD hygiene.

Targeted false-completion sweep this window. For each issue below,
re-read the latest 3 comments, then verify the claim against repo
state:

H1. #2462 — comment claims pushed branch + no PR. VERIFY:
    `gh api repos/vamseeachanta/digitalmodel/git/refs/heads/codex/burn-20260427-issue-2462`
    matches comment. If branch missing, this is a false-completion claim.

H2. #2458 — comment claims two scoped refs pushed. VERIFY both refs by
    name in `gh api repos/.../branches?per_page=100`.

H3. #2433 — PR worldenergydata#356 head 397686ed68. VERIFY head SHA
    matches the comment.

H4. #2459 — PR assethold#47 head b922e2533b. VERIFY head SHA matches
    comment AND verify "focused tests pass" claim by listing failing
    workflows.

H5. #2269 — commit 464efb8cc3. VERIFY whether branch was pushed to
    workspace-hub origin or only stayed local.

H6. #2346 — commit 44735e979a. Same verification as H5.

For each, write:
- Verification command + observed output (truncated to 12 lines)
- Claim status: VERIFIED / FALSE / PARTIAL / UNVERIFIABLE_FROM_ACE2
- Recommended next action

Output to results/ace2-review-and-gsd.md plus the optional
ace2-worker-reports/ path.

Per memory feedback_attestation_enables_contradiction_detection: this
sweep is the unlock for #2405 plan-vs-live-state contradiction work.

Do NOT post comments. Do NOT label-mutate. Output is a draft pack for
ace-linux-1 to review.
```

---

## Lanes that completed / blocked — proposed safe follow-up (informational)

- **Gemini batch (night pack A2)**: completed; output at
  `2026-04-28-night-both-machines/results/gemini-batch-summary.md`. Five
  ranked items, top-5 already folded into this reconciler. No relaunch.
- **A1 Codex approved-recovery**: produced #2289/#2433/#2459/#2269/#2346
  push evidence. Three are VERIFY_CLOSE (#2433, #2459 PRs open; #2346
  commit pushed). Two are BLOCKED_RESOURCE (#2289 hook, #2272 env-blocked
  no-code). Follow-up: command pack section A handles VERIFY_CLOSE; section
  B handles BLOCKED_RESOURCE.
- **A2 Gemini recon-batch**: 429 rate-limited per ledger. Recon completed
  via no-tools fallback. No relaunch.
- **A3 Claude control-plane synthesis**: outputs feed this lane. No
  relaunch needed; this lane (C1) supersedes.
- **B1 ace2 digitalmodel approved**: BLOCKED on env. Follow-up = D1
  prompt above (diagnose, do not retry).
- **B2 ace2 knowledge/doc-intel approved**: blocked by approval-drift on
  Batch Packs. Follow-up = D2 prompt above (marker inventory).
- **B3 ace2 adversarial review**: outputs not seen by this reconciler.
  Follow-up = D3 prompt above (false-completion sweep).

---

## Anti-launch guardrails

1. **Never** start a new tmux session with the same name as an existing
   one (memory: parallel_agent_write_only_pattern + isolated-clone
   dispatch race).
2. **Never** start a Codex `exec` lane that was last seen at codex-cli
   0.124.0 — known stdin-hang regression per
   feedback_codex_cli_0_124_upstream_regression. If Codex is the
   provider, verify version is 0.123.0 first.
3. **Never** dispatch a writer-agent without a fresh worktree path that
   doesn't collide with another running session's worktree.
4. **Never** auto-approve a plan in chat or via marker creation; user
   approval gate is load-bearing per
   feedback_never_offer_to_self_label_plan_approved.
5. **Always** check `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'`
   before parallel commits — Hermes can revert untracked work
   (memory feedback_hermes_active_preflight_check).
