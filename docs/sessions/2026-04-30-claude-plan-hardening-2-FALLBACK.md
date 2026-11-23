# claude-plan-hardening-2 — fallback result

> **ENV-MISMATCH**: Lane prescribed result path
> `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-073439/results/claude-plan-hardening-2.md`
> is **outside** the session sandbox (`/mnt/local-analysis/workspace-hub`). `ls`/`Read`/`Write`
> all blocked. Per memory `feedback_lane_result_path_outside_sandbox.md` (2026-04-27),
> falling back to `docs/sessions/` and emitting this banner. Orchestrator should redirect
> future lanes or mount `agent-logs/` into the allowed dirs list.

## STARTED

- timestamp: 2026-04-30
- lane: claude-plan-hardening-2
- run dir: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-073439
- session sandbox: /mnt/local-analysis/workspace-hub
- task: identify plan-review artifacts with missing **adversarial / legal / TDD** evidence
  and produce a **bounded follow-up prompt pack**. **No approvals, no label mutations,
  no implementation.**
- mode: planning / review / evidence / handoff only

## Sources inspected

- `ls /mnt/local-analysis/agent-logs/provider-autofeed-20260430-073439/` → blocked (sandbox)
- `ls docs/plans/` → 326 plan files
- `ls .planning/plan-approved/` → 120 entries; latest issue marker = `2560.md`
- `ls scripts/review/results/ | grep ^(2026-04-29|2026-04-30)` → 60 review artifacts
- `ls docs/sessions/` → confirmed prior fallback artifacts at 0734 / 1003 / 1113 / 1143
- Targeted `grep` on each in-flight plan for `TDD|test.driven|legal|copyright|licens`
- Read of #2564 yaw-moment plan, #2560 evidence-fill plan, and Hermes review headers
  for #2554 / #2556 / #2561 / #2562
- Read of `docs/sessions/2026-04-30-claude-plan-review-hardening-2-FALLBACK.md` (prior
  lane @ 1143) for continuity with the established readiness frame

`git status` was attempted with a 10s timeout and exited 124 — the workspace lock is
contended (Hermes / auto-sync). No write operation requires `git status`; analysis
proceeded read-only via `ls`/`grep`/`Read`.

## Evidence matrix — in-flight plans, three axes

Three independent evidence axes are required by `docs/plans/README.md` and
`docs/standards/AI_REVIEW_ROUTING_POLICY.md`:

- **Adversarial**: ≥2 substantive cross-provider review verdicts (defect-hunting stance,
  not charitable acceptance), or an explicit T1 deferred-review user waiver.
- **Legal**: legal-sanity scan invocation tied to a TDD row OR a no-send/no-promotion
  gate; copyright / standards-quotation caution where standards are quoted verbatim.
- **TDD**: canonical "TDD Test List" with at least one row that would fail before the
  fix exists, in the failing-test-then-fix discipline.

| Issue | Plan | Adversarial | Legal | TDD |
|---|---|---|---|---|
| #2550 | `2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` | ✅ r4 Codex MAJOR + Gemini MAJOR (cross-provider quorum, substantive non-overlap) | ❌ **GAP** — no legal section, no legal-scan TDD row, no copyright framing | ✅ TDD Test List with split unit + bats integration |
| #2552 | `2026-04-29-issue-2552-external-contributor-runbook.md` | ✅ r4 Codex MAJOR + Gemini MAJOR (cross-provider quorum, substantive non-overlap) | ⚠️ **PARTIAL** — CLA/license posture cited in scenario 3; no legal-sanity-scan TDD row enforcing the gate | ✅ TDD Test List |
| #2554 | `2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` | ⚠️ **GAP** — Hermes delegate live MINOR is sole reviewer; cross-provider quorum absent and no recorded T1 waiver | ✅ Legal Sanity Gate + `no-individual-contact-details` acceptance criterion + legal scan TDD row | ⚠️ **GAP** — explicit "Test List (research-artifact equivalent of TDD)" deferral; not canonical failing-test-first |
| #2556 | `2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` | ⚠️ **GAP** — Hermes-only r4b MINOR; cross-provider quorum absent | ✅ `legal_sanity_scan` TDD row + no-send legal gate (7 plan-binding constraints) + `last_legal_scan_utc` rule | ✅ TDD Test List with `brochure_demo_path_full_filenames` + `brochure_proof_count_provenance` rows |
| #2560 | `2026-04-30-issue-2560-gtm-contractor-evidence-fill.md` | ⚠️ **GAP** — Hermes-only r1; cross-provider quorum absent (note: `.planning/plan-approved/2560.md` marker exists — verify whether prior approval covered an earlier revision) | ✅ legal-scan sidecar slot + `legal_scan` TDD row + scoped/staged grep leak check fallback | ✅ TDD Test List |
| #2561 | `2026-04-30-issue-2561-fowt-mooring-screening-worked-example.md` | ⚠️ **GAP** — Hermes-only r2 MINOR; cross-provider quorum absent | ✅ `legal_scan` TDD row + structured sidecar requirement + copyright/standards-quotation caution (added in r2 patch) | ✅ TDD Test List |
| #2562 | `2026-04-30-issue-2562-gom-niche-vessel-contractor-evidence-lane.md` | ⚠️ **GAP** — Hermes-only r2 MINOR; cross-provider quorum absent | ✅ legal-scan sidecar + `legal_scan` TDD row | ✅ TDD Test List |
| #2564 | `2026-04-30-issue-2564-yaw-moment-sweep-input.md` | ❌ **GAP** — all three CLIs UNAVAILABLE 2026-04-30 (Codex stdin-hang, Gemini capacity, Claude SessionEnd); only Hermes governance CONDITIONAL + 2026-04-29 MAJOR baseline | ❌ **GAP** — TDD-backed deliverable but no legal-scan TDD row; the plan cites PNA Vol. III, Bertram, ABS Vessel-Maneuverability Guide, IMO MSC/Circ.1053 — copyright/standards-quotation risk not surfaced | ✅ TDD Test List + "TDD-backed digitalmodel yaw-moment sweep capability" |

### Defect classes summarized

- **Class A — cross-provider quorum present, author revision pending:** #2550, #2552.
  These plans have authentic adversarial review (≥2 substantive non-overlapping MAJOR
  verdicts on r4). The blocker is author response, not review depth.
- **Class B — Hermes-only single-reviewer, cross-provider quorum absent:** #2554,
  #2556, #2560, #2561, #2562. Hermes is genuinely adversarial in stance (numbered
  findings, initial MAJOR verdicts, demands patches), but `AI_REVIEW_ROUTING_POLICY`
  requires ≥2 substantive cross-provider verdicts. Today's blocker is provider
  availability, not adversarial stance.
- **Class C — total provider blackout:** #2564. All three external CLIs unavailable
  on 2026-04-30; only the 2026-04-29 baseline (MAJOR) and Hermes governance
  (CONDITIONAL) carry weight. Approval-blocked until at least one external CLI
  recovers.
- **Class D — legal evidence missing in a plan that doesn't outwardly look "legal":**
  #2550 (interaction-limit policy is itself a legal-posture artifact — should at
  minimum cite a legal/CLA review hook), #2552 (CLA/license posture cited but not
  gated by a legal-scan TDD row), #2564 (verbatim standards quotation without a
  copyright/standards-quotation caution).
- **Class E — TDD-deferral plans:** #2554. Acceptable for research-artifact lanes,
  but the deferral should be explicit in `Acceptance Criteria` and tied to a
  follow-up issue that re-introduces canonical TDD if the artifact promotes from
  research surface to runtime surface.

## Bounded follow-up prompt pack

These are prompts the **user** (or a future plan-approved lane) can issue. None of
them mutate labels, none self-approve, none authorize implementation. Each is
phrased as a planning/review/handoff request to the plan author, gated on user
re-evaluation.

### P1 — Class B reviewers (provider tooling recovery preflight)

Before re-dispatching cross-provider fanout against any of #2554 / #2556 / #2560 /
#2561 / #2562, run the preflight:

```text
PROMPT — provider-availability preflight
Goal: confirm at least one of the three external CLIs is operational before
spending fanout slots.
Steps:
1. `codex --version` → confirm not 0.124.0 (memory: feedback_codex_cli_0_124...).
2. Issue a 90-byte canary plan to Codex via cross-review wrapper; expect non-stub.
3. `gemini --version` and verify GEMINI_CLI_TRUST_WORKSPACE=true is set; canary
   the same way; capacity-check on the pinned model (currently
   gemini-3.1-pro-preview is exhausted — repin or unpin).
4. Trigger a Claude review with SessionEnd hook; expect non-stub.
Action on failure: do NOT rerun fanout against the seven plans; surface the
provider regression to the orchestrator and append to #2479.
```

### P2 — Class A author-revision prompt (#2550)

```text
PROMPT — #2550 r5 author revision
Goal: address Codex r4-final and Gemini r4-final MAJOR findings; emit Class D
legal-evidence row.
Author tasks:
1. Split dry-run semantics: `--dry-run` = report-only; new `--check` = compliance
   verify with non-zero exit.
2. Reconcile `jq` vs `gh --jq`; update `requires:` and Bats test wording.
3. Add `mkdir -p logs/security/` to script bootstrap.
4. State Hermes cron decommission as either manual operator step OR exact
   `crontab -r` / unit-disable command.
5. Decide deterministic report-delivery default (recommend: dated local report;
   GitHub-comment behind `--post-comment` flag).
6. Close all "open questions" inline.
7. **NEW (Class D legal evidence):** Add a legal-posture row to TDD Test List
   tying interaction-limit renewal to a legal/CLA review hook OR explicitly
   declare the renewal posture as an internal-policy artifact with no public-
   distribution leg.
8. Rerun cross-provider fanout once P1 preflight passes; archive fresh artifacts.

Constraint: Do NOT add or move `status:plan-approved`. Plan stays
`status:plan-review` after revision; user re-evaluates.
```

### P3 — Class A author-revision prompt (#2552)

```text
PROMPT — #2552 r5 author revision
Goal: address Codex r4-final and Gemini r4-final MAJOR findings; emit Class D
legal-evidence row.
Author tasks:
1. Drop `test_plan_index_contains_2552_row` from permanent test suite (move to
   one-time execution check).
2. Add `CONTRIBUTING.md` (or `README.md`) update task to Files-to-Change so the
   off-GitHub contact path is publicly discoverable.
3. Decide GitHub-comment vs log-only and remove from open questions.
4. Declare `jq` vs `gh --jq`.
5. Replace stale 2026-04-29 embedded evidence block with the 2026-04-30 attested
   set; explicitly verify labels and issue bodies.
6. **NEW (Class D legal evidence):** Add `legal_cla_posture_check` TDD row
   binding the runbook's CLA/license posture mention (line 112) to a verifiable
   gate (e.g., grep for `CLA` or `license` in the runbook before promotion;
   confirm the project's CLA stance is documented in CONTRIBUTING.md).
7. Rerun cross-provider fanout once P1 preflight passes.

Constraint: same — no label mutation, user re-evaluates.
```

### P4 — Class B reviewer-quorum prompt (#2554)

```text
PROMPT — #2554 cross-provider quorum OR T1 waiver
Goal: convert Hermes-delegate-only MINOR into a quorum-backed verdict.
Two paths (user picks one):
(a) After P1 preflight passes, dispatch Codex + Gemini cross-review against
    the patched #2554 plan; archive both artifacts.
(b) Surface to user a T1 documentation deferred-review path waiver: explicit
    user note in the plan that #2554 is approved on documentation-surface
    grounds without cross-provider evidence; record waiver SHA + waiver
    rationale in the plan body.

ALSO (Class E TDD-deferral): tighten the "research-artifact equivalent of TDD"
language so the deferral is bound to: "no canonical failing-test-first row
required while artifact lives at `docs/reports/gtm/...`; if/when the artifact
promotes to runtime surface, follow-up issue must re-introduce canonical TDD."

Constraint: NEVER self-approve in chat; lane stays `status:plan-review` until
user reads waiver and approves.
```

### P5 — Class B reviewer-quorum prompt (#2556 / #2561 / #2562)

```text
PROMPT — re-dispatch fanout once P1 preflight passes
Plans: #2556 (r4b), #2561 (r2), #2562 (r2).
For each, dispatch Codex + Gemini cross-review against the local Hermes-patched
plan revision. If Codex / Gemini return MAJOR, surface findings for author
patch; if MINOR / clean, archive as r5 review artifacts and recompute approval
readiness.

DO NOT batch-rerun before preflight. DO NOT self-approve. The Hermes MINOR
verdict is **substantively** clean but **procedurally** insufficient under
`AI_REVIEW_ROUTING_POLICY` quorum rules — wait for cross-provider evidence.
```

### P6 — Class B confirmation prompt (#2560)

```text
PROMPT — verify #2560 approval marker is revision-bound
Marker `.planning/plan-approved/2560.md` exists. Per memory
`project_issue_2460_approval_binding.md`, approval markers must be
revision-bound (SHA + review artifact paths + storage surface).

Action: read `.planning/plan-approved/2560.md`; confirm it carries SHA and
review artifact paths matching the current `docs/plans/2026-04-30-issue-2560-...`
content. If marker is stale or refers to an earlier revision, surface to user
for waiver-or-revoke decision. Do NOT remove the marker yourself.

If marker is stale: do P5-style cross-provider fanout against current revision
once P1 preflight passes.
```

### P7 — Class C blackout prompt (#2564)

```text
PROMPT — #2564 hold-and-document
While all three CLIs are UNAVAILABLE today, do NOT rerun fanout (would burn
provider quota for identical UNAVAILABLE stubs).

Author tasks (do now, no provider needed):
1. **NEW (Class D legal evidence):** Add a `copyright_standards_quotation_scan`
   TDD row that grep-checks the plan body and any generated yaw-moment
   documentation for verbatim quotations from PNA Vol. III, Bertram, ABS, IMO,
   USNA EN400; require either (a) paraphrase + cite, or (b) fair-use
   short-quotation with explicit attribution. Tie to `scripts/legal/legal-sanity-scan.sh`.
2. State that the 2026-04-29 baseline (Codex MAJOR + Gemini MAJOR) remains
   authoritative until at least one external CLI recovers; the Hermes governance
   CONDITIONAL is informational, not quorum.
3. Add to plan body: "Approval-blocked: triple-provider blackout 2026-04-30;
   re-engage cross-review after #2479 + Gemini-capacity + Claude-SessionEnd
   regressions clear."

Track on #2479: (a) Claude SessionEnd hook regression repro; (b) Gemini
gemini-3.1-pro-preview capacity-pinning hazard.
```

## Lane invariants confirmed

- No `status:plan-approved` label mutated.
- No `.planning/plan-approved/<issue>.md` marker written, removed, or modified.
- No outreach, no external sending, no implementation work attempted.
- No commits made.
- Sandbox boundary respected: result emitted to `docs/sessions/` with
  ENV-MISMATCH banner; orchestrator should re-mount `agent-logs/` or update lane
  prescription.
- Approval-binding rule (memory `project_issue_2460_approval_binding.md`) honored:
  every prompt above stays in `status:plan-review` posture; final approval
  requires user action with revision-bound markers.
- Workspace dirty-state honored: no `git reset`, `git clean`, `git checkout --`,
  `git stash drop`, or `git rebase` operations attempted. `git status` was
  observed to time out (Hermes / auto-sync lock contention) — analysis proceeded
  read-only.

## Handoff to orchestrator

1. **Single durable artifact today** is this fallback file. If a future lane is
   granted broader sandbox access, copy contents to the prescribed `agent-logs/`
   path verbatim.
2. **Recommend promoting** memory `feedback_lane_result_path_outside_sandbox.md`
   (2026-04-27) to a hookify rule that catches lane prompts prescribing paths
   outside the workspace allowlist before a session even starts. Three
   consecutive lanes (1003 / 1113 / 1143 / 0734-this) have hit the same trap.
3. **Provider-blackout signal**: triple-CLI failure on 2026-04-30 (Codex
   stdin-hang, Gemini capacity, Claude SessionEnd hook) is a routing-policy
   stress that the "≥1 provider available" assumption did not anticipate.
   Recommend either (a) appending to #2479, or (b) filing a sibling issue for
   Gemini model-pinning hazard (currently pinned to `gemini-3.1-pro-preview`
   which returned 429 No-capacity today).
4. **Class D legal-evidence gap** is the lane's most under-attended axis: three
   plans (#2550, #2552, #2564) are silent or thin on legal scan / copyright /
   CLA gating despite touching legal-relevant surfaces. Recommend the user
   issue P2 / P3 / P7 prompts to authors before re-dispatching any
   cross-provider fanout.
5. **Class A vs Class B distinction** is the lane's most useful synthesis: do
   NOT lump "more reviewer effort needed" together — Class A needs author
   revision, Class B needs provider availability, and the prompts to issue
   are different. The previous fallback artifact (1143) treated all five
   non-#2550/#2552 plans as approval-prep candidates without distinguishing
   the quorum-vs-revision blocker; this lane corrects that.
