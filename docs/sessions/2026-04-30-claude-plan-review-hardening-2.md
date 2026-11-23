# claude-plan-review-hardening-2 — lane result

> **STARTED:** 2026-04-30T19:30Z (approx — UTC; system clock not directly polled, see Inspected commands)
> **Lane:** `claude-plan-review-hardening-2`
> **Workspace:** `/mnt/local-analysis/workspace-hub`
> **Original prescribed result path:** `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-145633/results/claude-plan-review-hardening-2.md`
> **Actual result path:** `docs/sessions/2026-04-30-claude-plan-review-hardening-2.md`
> **Hard gates honored:** no GitHub label/comment/closure mutations; no implementation; no outreach; no plan-approved markers created; no destructive git ops on workspace-hub.

## ENV-MISMATCH banner

The prescribed result file path sits outside the Claude Code workspace sandbox (`/mnt/local-analysis/workspace-hub`). Multiple `Bash` and `ls` attempts on `/mnt/local-analysis/agent-logs/...` were blocked with the message *"For security, Claude Code may only list files in the allowed working directories for this session"* and the parent process refused `mkdir`/listing under that path. Per `~/.claude/projects/.../memory/feedback_lane_result_path_outside_sandbox.md` (verified pattern, recurring failure mode for provider-autofeed lanes), this lane wrote durable output to `docs/sessions/` inside the sandbox instead. Operator action: either copy this file to the prescribed location after the session, or update the lane harness to issue paths under `docs/sessions/` (or a path that is granted to the Claude Code session).

## Inspected commands / sources

- `Bash: ls docs/plans/` — 326 entries; identified recent (2026-04-28→04-30) plans with no matching `.planning/plan-approved/<n>.md` marker.
- `Bash: ls .planning/plan-approved/` — 120 markers; latest are `2555.md`, `2560.md`, plus `aces-{2,3,4}.md`, `ecosystem-sync.md`.
- `Bash: ls scripts/review/results/ | grep -E "plan-(2557|2561|2562|2564|2552|2550)-"` — enumerated current review artifact set.
- `Read: docs/plans/nightly-immediate-batch2-20260430-plan-review-hardening.md` — sibling lane prompt (batch 2/5).
- `Read: docs/plans/2026-04-30-issue-2561-fowt-mooring-screening-worked-example.md` (147 lines).
- `Read: docs/plans/2026-04-30-issue-2562-gom-niche-vessel-contractor-evidence-lane.md` (151 lines).
- `Read: docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md` (349 lines).
- `Read: docs/plans/2026-04-30-issue-2564-mnt-ace-raw-reference-review.md` (78 lines, Resource-Intelligence addendum).
- `Read: docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` (239 lines).
- `Read: scripts/review/results/2026-04-30-plan-2552-{codex,gemini}-final.md`.
- `Read: scripts/review/results/2026-04-30-plan-2550-{codex,gemini}-final.md`.
- `Read: scripts/review/results/2026-04-30-plan-2564-{claude,codex,gemini}.md`.
- `Read: scripts/review/results/2026-04-30-plan-{2561,2562}-hermes.md`.
- Live label/state via `gh issue view <n> --json state,labels` for #2550, #2552, #2557, #2561, #2562, #2564 (all OPEN; labels recorded inline below).
- Memory cross-checked: `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_gemini_sandbox_overlay_blindness.md`, `feedback_codex_sustained_major_loop.md`, `feedback_attestation_enables_contradiction_detection.md`, `feedback_never_offer_to_self_label_plan_approved.md`, `feedback_lane_result_path_outside_sandbox.md`.

## Selection method

"Closest approval-prep" = (a) plan exists in `docs/plans/` on `2026-04-28` or later, (b) **no** matching `.planning/plan-approved/<issue>.md` marker, (c) at least one structured review artifact exists or is explicitly pending, (d) plan is materially complete (Acceptance Criteria + TDD/EC + Adversarial Review Summary). Out of ~14 plans matching (a)+(b), the 5 closest by remaining gate distance are listed below. #2557 is named as a sixth alternate (still farther because the companion report file regeneration is operator-gated).

## 5 candidates

### 1. #2552 — `external-contributor-runbook` (T1 doc plan)

- **Plan path:** `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md`
- **Live label state:** OPEN, `status:plan-review`, `documentation`, `cat:documentation`, `domain:security`, `priority:medium`. **No** local `.planning/plan-approved/2552.md`.
- **Latest review verdicts on this revision:** Codex 2026-04-30 final = **MAJOR**; Gemini 2026-04-30 final = **MAJOR**. (Earlier 2026-04-29 set: Codex/Gemini also MAJOR.)
- **Missing evidence:** (i) clean (MINOR-or-better) Codex artifact on the current revision; (ii) clean Gemini artifact on the current revision; (iii) explicit user waiver in the plan text if T1 deferred-review path is being invoked (Codex final review explicitly asks this question).
- **Current blockers:**
  - Codex MAJOR — *the plan's own front-matter and Adversarial Review Summary say "not approval-ready until fresh Codex/Gemini rerun is clean"; the artifacts cited are still MAJOR-on-prior-revisions, not clean reruns* (`scripts/review/results/2026-04-30-plan-2552-codex-final.md`).
  - Codex MINOR — stale 2026-04-29 embedded evidence block coexists with 2026-04-30 attested evidence; labels and issue bodies are not affirmatively verified.
  - Gemini MAJOR — `tests/security/test_runbook_external_contributor.py::test_plan_index_contains_2552_row` enforces presence of a point-in-time historical plan-index row in a permanent CI lint test; that test fails the moment the plan is archived/rotated.
  - Gemini MAJOR — Files-to-Change does not update `CONTRIBUTING.md`/`README.md` to publish the off-GitHub contact path the plan relies on for legitimate external contributors during interaction-limit lockdown; the prescribed ingestion vector is undiscoverable.
- **Legal/provenance status:** GTM/contributor-process plan; no engineering claims; `docs/standards/calc-output-citation.md` not triggered. Provenance gates that *do* apply: (a) cross-provider review evidence required before approval per `docs/standards/AI_REVIEW_ROUTING_POLICY.md` and `docs/plans/README.md` (Codex final cites both); (b) any off-GitHub contact path published in the repo must avoid disclosing private routes/PII (consistent with `docs/BUSINESS_BRAIN.md` legal-sanity gate). No `Citation` schema work needed.
- **Exact non-mutating follow-up prompt:**
  > Open the planning-only worktree at the latest `main` for #2552. Patch `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` to (1) drop `test_plan_index_contains_2552_row` and replace with a one-time evidence check executed during the plan's own implementation lane; (2) add a Files-to-Change row updating `CONTRIBUTING.md` (and/or `README.md`) to publish the off-GitHub ingestion vector that scenario 3 depends on; (3) replace the stale 2026-04-29 embedded-evidence block with the 2026-04-30 attested-evidence block (or clearly demote it as historical) and add explicit `gh issue view --json labels` verification commands. Then run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` from a non-sandboxed terminal (after `npm install -g @openai/codex@0.123.0` if Codex is still hanging) and write artifacts to `scripts/review/results/2026-05-01-plan-2552-{claude,codex,gemini}.md`. Do **not** flip labels, post comments, or create a `status:plan-approved` marker. Stop after the artifact set lands; user reviews.

### 2. #2564 — `yaw-moment-sweep-input` (engineering-critical T2)

- **Plan path:** `docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md` (canonical) + `docs/plans/2026-04-30-issue-2564-mnt-ace-raw-reference-review.md` (RI addendum).
- **Live label state:** OPEN, `status:plan-review`, `enhancement`, `cat:engineering-calculations`, `domain:hydrodynamics`, `domain:naval-architecture`, `priority:medium`. **No** local `.planning/plan-approved/2564.md`.
- **Latest review verdicts on the 2026-04-30 revision:** Claude UNAVAILABLE (rc=124, `SessionEnd hook ... Hook cancelled`), Codex UNAVAILABLE (rc=124, `Reading additional input from stdin...` → matches #2479 stdin-hang regression), Gemini UNAVAILABLE (rc=124, 429 *"No capacity available for model gemini-3.1-pro-preview"*). Authoritative substantive set is therefore the 2026-04-29 trio (Claude MAJOR, Codex MAJOR, Gemini MAJOR; addressed in this revision but not re-verified).
- **Missing evidence:** at least **two** substantive no-MAJOR provider reviews against the 2026-04-30 plan revision. Per the plan's own Acceptance Criteria: *"a single-provider 'available providers' result is not sufficient for this engineering-critical plan."*
- **Current blockers:**
  - All three 2026-04-30 review attempts are UNAVAILABLE — purely tooling failures, not signal. Any approval pass against current artifacts is unjustified per `docs/BUSINESS_BRAIN.md` lines 89–97 (*"repeated APPROVE/MINOR adversarial-review outcomes across Claude/Codex/Gemini"*).
  - Codex blocked by upstream `codex-cli@0.124.0` stdin-hang (#2479); per memory `feedback_codex_cli_0_124_upstream_regression.md`, even the `0.123.0` downgrade hangs from inside Claude Code's Bash tool — operator must run from a plain terminal.
  - Gemini quota 429 — no immediate workaround besides retry-with-backoff or schedule outside the saturated window; per memory `feedback_gemini_sandbox_overlay_blindness.md`, must additionally verify any "file missing" finding against `git ls-files` if/when Gemini does respond.
  - Sign-convention precondition probe is a real implementation-time gate (the plan acknowledges this), but does **not** block plan approval — flag it for the executing lane, not the review lane.
- **Legal/provenance status:** Engineering calc plan that explicitly does *not* trigger `docs/standards/calc-output-citation.md` (no standards-derived numeric constant introduced; reuses `digitalmodel.naval_architecture.maneuverability.rudder_normal_force` via Whicker & Fehlner research literature, not a standards page). Plan correctly emits non-schema provenance (`force_source_module`, `scope_limitations`) instead of fabricating a strict `Citation`. Cross-repo write boundary: governance commits land in `workspace-hub`, implementation in nested `digitalmodel/` repo — both pushes are gated on `status:plan-approved` and explicit user approval. Conforms to `.claude/rules/calc-citation-contract.md` "Do NOT apply when..." clause.
- **Exact non-mutating follow-up prompt:**
  > From a plain terminal (not Claude Code Bash, not Hermes), run `npm install -g @openai/codex@0.123.0` and then `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md` against the latest `main`. Write fresh artifacts to `scripts/review/results/2026-05-01-plan-2564-{claude,codex,gemini}.md`. If Gemini still returns 429, retry once after 6 hours; do **not** treat the prior 2026-04-29 MAJOR set as the current verdict and do **not** synthesize a "majority MINOR" verdict from a single substantive provider — engineering-critical plans require ≥2 substantive no-MAJOR. Do not promote labels, post comments, or write `.planning/plan-approved/2564.md`. After the artifact set lands, append a `Disagreement` analysis at `scripts/review/results/2026-05-01-plan-2564-disagreement.md` if any provider returns MAJOR.

### 3. #2550 — `interaction-limit-renewal-scheduled-task` (T1 ops/security)

- **Plan path:** `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md`
- **Live label state:** OPEN, `status:plan-review`, `enhancement`, `cat:operations`, `domain:automation`, `domain:security`, `priority:medium`. **No** local `.planning/plan-approved/2550.md`.
- **Latest review verdicts on the 2026-04-30 final revision:** Codex final = **MAJOR**; Gemini final = **MAJOR**. (`-rerun` artifacts also exist but `-final` are the freshest substantive reviews.)
- **Missing evidence:** plan revision that resolves the dry-run semantics + jq dependency + report-delivery + log-dir-creation contradictions; then a clean cross-provider rerun.
- **Current blockers:**
  - Codex MAJOR — Pseudocode says dry-run *always* runs verification loop and exits 1 on non-`collaborators_only`, but Acceptance Criteria says `--dry-run` exits 0 and prints status without PUT. Internal contradiction blocks implementation behavior.
  - Codex MAJOR — Plan declares its own approval gate unmet (`Overall result: NOT APPROVAL-READY after 2026-04-30 Codex MAJOR`).
  - Codex MINOR — Bats test `test_set_minus_e_propagates_jq_failure` expects jq behavior, but scheduled-task `requires:` lists `[bash, gh]` only.
  - Codex MINOR — Report-delivery still listed as Open Question (post issue comment? write local report?) — must be deterministic before approval.
  - Gemini MAJOR — Same Open-Questions punt (issue comment, `__init__.py`/`conftest.py`); `jq` requires-list mismatch; missing `mkdir -p logs/security/`; Hermes-cron decommission is not actionable without explicit CLI command or "manual human step" annotation.
- **Legal/provenance status:** Ops plan modifying interaction-limit lockdown via `gh api` PUT; no standards-derived constants → `calc-citation-contract.md` not triggered. Boundary concern: the script issues a real PUT against `gh api` repo settings, which is a write to shared GitHub state — implementation lane must respect "carefully consider reversibility and blast radius" guidance and confirm before each PUT, *not* run in autonomous mode. No PII; no outreach.
- **Exact non-mutating follow-up prompt:**
  > In a planning-only worktree, patch `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` to: (1) define dry-run as report-only (exits 0, no PUT, no compliance-check exit codes) and add a separate `--check`/`--verify-only` flag for the compliance-checking variant; (2) decide one default for report delivery (recommend: write dated local report to `docs/reports/security/`, optionally post issue comment behind a flag) and remove from Open Questions; (3) add `jq` to `requires:` list (or pivot to `gh --jq` and update the Bats test wording to match); (4) add an explicit `mkdir -p logs/security/` step in both script and scheduled-task setup; (5) make the Hermes-cron decommission step explicit (CLI command if remote-accessible; otherwise mark as "manual human step on Hermes host"); (6) close the `__init__.py`/`conftest.py` Open Question (recommend: not needed, justify in plan). Then rerun the fanout script and write artifacts to `scripts/review/results/2026-05-01-plan-2550-{claude,codex,gemini}.md`. Do not promote labels, mutate cron schedules, or call any `gh api ... -X PUT` — this lane is planning/review only.

### 4. #2561 — `fowt-mooring-screening-worked-example` (T2 GTM proof)

- **Plan path:** `docs/plans/2026-04-30-issue-2561-fowt-mooring-screening-worked-example.md`
- **Live label state:** OPEN, `priority:medium`, `cat:business`, `domain:gtm`, `type:follow-up`. **No** `status:plan-review`. **No** local `.planning/plan-approved/2561.md`.
- **Latest review verdicts:** Hermes/local **MAJOR → MINOR after r2 patch** (`scripts/review/results/2026-04-30-plan-2561-hermes.md`); Codex PENDING (never run); Gemini PENDING (never run).
- **Missing evidence:** any external (non-Hermes) provider artifact on the current revision; the plan itself notes *"Codex/Gemini review still required before `status:plan-review`"*.
- **Current blockers:**
  - No cross-provider review yet — single-author MINOR is insufficient for promotion to `status:plan-review`.
  - Primary artifact (`docs/reports/gtm/2026-04-30-fowt-mooring-screening-worked-example.md`) and legal-scan sidecar (`docs/reports/gtm/legal-scans/2026-04-30-fowt-worked-example-scan.json`) are MISSING — by design (this is the planning slice), but reviewers will want to see the legal-scan harness wired up before approval.
  - Reference-geometry freeze (OC4-DeepCwind) is locked in r2 but the *minimum public geometry package* (water depth, floater variant, mooring arrangement, copied vs inferred parameters, `checked_at`) is still aspirational; reviewers will probe whether the plan specifies the source URL/document version.
- **Legal/provenance status:** GTM artifact, public-repo-safe; explicit no-outreach / no-PII / no-private-route gates in Acceptance Criteria. Engineering boundary is sharp: screening-only, not certification-grade, not bankability evidence, not site-specific design, not IEC 61400-3 DLC, not aero-servo-elastic. Source-quotation discipline is gated by `scripts/legal/legal-sanity-scan.sh --diff-only` with structured sidecar — addresses copyright/standards-overuse risk. `calc-citation-contract.md` does not apply (no standards-derived numeric constants are introduced; the artifact references a public reference geometry, not adopts a standards constant). No `Citation` schema needed.
- **Exact non-mutating follow-up prompt:**
  > Verify that `docs/plans/2026-04-30-issue-2561-fowt-mooring-screening-worked-example.md` names an exact OC4-DeepCwind source (canonical NREL/IEA-15 PDF or web URL) along with revision/year and `checked_at` placeholder fields, then run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-30-issue-2561-fowt-mooring-screening-worked-example.md` from a non-sandboxed terminal. Write artifacts to `scripts/review/results/2026-05-01-plan-2561-{claude,codex,gemini}.md`. Do not promote `status:plan-review` until at least two substantive no-MAJOR provider artifacts land; do not create the primary artifact `docs/reports/gtm/2026-04-30-fowt-mooring-screening-worked-example.md` (that is the implementation lane's job, post-approval). Do not flip labels or post issue comments.

### 5. #2562 — `gom-niche-vessel-contractor-evidence-lane` (T2 GTM data)

- **Plan path:** `docs/plans/2026-04-30-issue-2562-gom-niche-vessel-contractor-evidence-lane.md`
- **Live label state:** OPEN, `priority:high`, `cat:business`, `domain:gtm`, `type:follow-up`. **No** `status:plan-review`. **No** local `.planning/plan-approved/2562.md`.
- **Latest review verdicts:** Hermes/local **MAJOR → MINOR after r2 patch** (`scripts/review/results/2026-04-30-plan-2562-hermes.md`); Codex PENDING; Gemini PENDING.
- **Missing evidence:** any external (non-Hermes) provider artifact on the current revision; plan explicitly states *"Codex/Gemini review still required before `status:plan-review`"*.
- **Current blockers:**
  - No cross-provider review yet — same as #2561.
  - Boundary with #2560 (broad High-priority deep-link/pain-point fill) was patched in r2 but reviewers will probe whether the deduplication rule (*"Duplicate URLs must reference the #2560 source rather than diverge"*) is operationally enforceable without a tooling step.
  - Demo 3 / Demo 5 / no-demo-gap rubric is a one-paragraph rule — reviewers will likely ask for a worked-classification example for each of Helix/Otto Candies/Hornbeck/ECO before approval.
- **Legal/provenance status:** Strict no-individual-contacts / no-direct-emails / no-phone-numbers / no-private-routes gates, with grep-based no-PII test (`@`, phone-like patterns, `linkedin.com/in`, person-name fields, `private_route`). Legal-sanity-scan + path/proprietary leak grep gates present. Public-repo-safe. `calc-citation-contract.md` does not apply (no standards content). Outreach explicitly blocked at the plan level (echoes `feedback_recruiter_engagement.md` and `BUSINESS_BRAIN.md` legal-sanity gate stance — this is consistent with project memory).
- **Exact non-mutating follow-up prompt:**
  > Patch `docs/plans/2026-04-30-issue-2562-gom-niche-vessel-contractor-evidence-lane.md` to add a worked-classification example for each of Helix, Otto Candies, Hornbeck, and Edison Chouest Offshore showing the demo-mapping rubric in action against each company's public fleet/service page. Then run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-30-issue-2562-gom-niche-vessel-contractor-evidence-lane.md` from a non-sandboxed terminal and write artifacts to `scripts/review/results/2026-05-01-plan-2562-{claude,codex,gemini}.md`. Do not promote labels, do not begin populating the canonical artifact `docs/reports/gtm/2026-04-30-gom-niche-vessel-contractor-evidence-lane.md`, do not modify the #2554 matrix scaffold. This lane is planning/review only.

## Sixth alternate (recorded but not selected)

- **#2557 — `weekly-productivity-flow-hacks`**: Plan exists with 8 distinct review findings (F1–F8) addressed at the plan-level by the 2026-04-29 nextwave-followup-patch, but the **companion report file** `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md` regeneration is operator-gated and the only structured review is single-author Claude MAJOR pre-patch. Codex/Gemini both UNAVAILABLE (Bash permission gate + #2479). Plan explicitly states *"Not ready for `status:plan-review` and not approved."* Strictly farther from approval than the 5 above. If the 2026-04-30 06:00 CT cron regeneration of provider-utilization-weekly happened before approval-prep, the plan numbers are already a snapshot pin and need a second refresh — adding latency. Recommend deferring until after #2550/#2552/#2564 land clean reviews.

## Cross-cutting blocker patterns (lane-level signal)

1. **Codex tooling regression #2479** is the dominant single point of failure across #2550/#2552/#2564 — every candidate would benefit from the operator-side `npm install -g @openai/codex@0.123.0` workaround being run from a plain terminal *before* fanouts are dispatched.
2. **Gemini 429 quota** struck #2564 on 2026-04-30; for engineering-critical plans where Gemini is one of two required substantive providers, schedule fanouts off-peak or accept Claude+Codex as the substantive pair.
3. **Single-author plans (#2557/#2561/#2562)** — local Hermes review is structurally insufficient evidence for label promotion. The fanout dispatch is the unblocking step; no plan-level patches are needed first for #2561/#2562 (#2557 has plan-level F7/F8 still deferred).
4. **No plan currently warrants a `status:plan-approved` marker.** Per `.planning/plan-approved/` ground-truth and the live label state, no candidate has the prerequisite *two substantive no-MAJOR* signal on the current revision. This lane did not approve any plan.

## Hard-gate compliance attestation

- No GitHub mutations issued (`gh issue view --json ...` is read-only; no `gh issue edit`, `gh pr ...`, `gh issue comment`, or label changes).
- No `.planning/plan-approved/<n>.md` markers created.
- No implementation, no test runs, no CLI subprocess that would write to repos other than this single durable result file under `docs/sessions/`.
- No outreach, no email/calendar, no Slack, no external sending. No private-route data added. No PII surfaced.
- `git status` not destructively manipulated; no `reset --hard`, `clean`, `checkout --`.
- Workspace assumed dirty per lane contract; this lane wrote exactly one new tracked file (`docs/sessions/2026-04-30-claude-plan-review-hardening-2.md`). Operator decides whether to commit it; no commit issued by this lane.

---

*End of lane report — claude-plan-review-hardening-2.*
