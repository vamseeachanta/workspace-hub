# Claude plan-review hardening lane #2 — result

> **ENV-MISMATCH banner** — prescribed result path
> `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-125920/results/claude-plan-review-hardening-2.md`
> is outside the workspace-hub sandbox (Read/Write blocked by my permission gate;
> Glob enumeration only, per memory `feedback_lane_result_path_outside_sandbox`).
> Falling back to `docs/sessions/` per the documented procedure. The agent-logs
> path is enumerable but inert; an operator with broader access can copy this
> file there if needed.

- **STARTED:** 2026-04-30T13:11:36Z
- **Lane:** claude-plan-review-hardening-2
- **Run dir:** `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-125920`
- **Workspace HEAD:** `4aa70be58` (main; Hermes was actively rebasing during this run — `git rebase --autostash` PIDs 2190414/2190922 + `git merge FETCH_HEAD` PID 2193359 observed at start)
- **Hard gates honoured:** no destructive reset/clean of workspace-hub, no outreach, no self-approval, no `status:plan-approved` mutation, no implementation. Result is planning/evidence/handoff only.
- **Approval-marker check:** `.planning/plan-approved/` contains no entries for #2564, #2552, #2550 — none have local approval state, none have GitHub `status:plan-approved` label. Both gate halves are unmet.

## Inspected commands & sources

```
gh issue list --label "status:plan-review" --state open --limit 100 --json number,title,labels,updatedAt
gh issue view 2564 --json body,title,labels,comments
gh issue view 2552 --json body,title,labels,comments
gh issue view 2550 --json body,title,labels,comments
git -C /mnt/local-analysis/workspace-hub rev-parse HEAD
pgrep -af "git rebase|git stash push|git commit|git merge|git reset|hermes"
ls /mnt/local-analysis/workspace-hub/.planning/plan-approved/
ls /mnt/local-analysis/workspace-hub/scripts/review/results/ | grep -E "2026-04-(29|30)-plan-(2564|2552|2550)"
head -40 scripts/review/results/2026-04-30-plan-2564-{claude,codex,gemini}.md
head -30 scripts/review/results/2026-04-30-plan-{2552,2550}-{codex,gemini}-final.md
```

Live `status:plan-review` issues (snapshot at 2026-04-30T13:11Z):

| Issue | Title | Cat | T-class | Last update |
|---|---|---|---|---|
| [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) | feat(naval-arch): yaw moment sweep input for rudder cases | engineering-calculations | T2 (engineering-critical) | 2026-04-30T10:39Z |
| [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) | docs(security): external contributor and unsolicited paid-help response runbook | documentation | T1 | 2026-04-30T04:08Z |
| [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) | chore(security): codify public repo interaction-limit renewal in scheduled tasks | operations | T2 | 2026-04-30T04:08Z |

## Evidence-gap matrix

Three dimensions audited per the lane brief: **adversarial** (cross-provider review), **legal/safety** (calc-citation contract for engineering plans; policy/ToS review for security/ops plans), **TDD** (test list defined and demonstrably failing in Red before implementation).

Status legend: `OK` = evidence present and current; `GAP` = evidence missing or stale; `BLOCKED` = upstream blocker (provider unavailable, environment mismatch).

| Issue | Adversarial | Legal/safety | TDD | Aggregate |
|---|---|---|---|---|
| #2564 | **BLOCKED** — 2026-04-30 fanout: Claude rc=124 SessionEnd hook, Codex rc=124 stdin hang (matches `feedback_codex_cli_0_124_upstream_regression`), Gemini rc=124 429 no-capacity for `gemini-3.1-pro-preview`. 2026-04-29 prior cycle had MAJOR history. **Zero fresh signal on current revision.** | **GAP** — calc-citation contract (`/mnt/local-analysis/workspace-hub/.claude/rules/calc-citation-contract.md`) requires Citation emission for every standards-derived constant. Plan defers Whicker & Fehlner from Citation schema but still anchors to PNA Vol III, USNA EN400, Bertram, ShipMo3D/McTaggart, ABS Vessel Maneuverability Guide, IMO MSC/Circ.1053, USCG NVIC 6-95/7-89. No per-constant audit shown. | **GAP** — TDD list itemized in plan (sign convention, package-data YAML access, speed-unit conversion, sweep cardinality, output schemas, chart artifacts) but no Red-state evidence; absolute (not symmetry-only) sign tests called out by author but not demonstrated. | NOT approval-ready |
| #2552 | **GAP** — 2026-04-30-final: Codex **MAJOR** (approval gate fails self-test; cross-provider evidence incomplete; stale 2026-04-29 evidence embedded), Gemini **MAJOR** (brittle `test_plan_index_contains_2552_row` mixes process verification with permanent CI; off-GitHub contact path not publicized in CONTRIBUTING.md / README.md so Scenario 3 ingestion vector is undiscoverable). Codex run was the third attempt (rerun → final), suggesting unstable signal. | **GAP** — paid-pilot scenario (Scenario 4) defers NDA template as out-of-scope, but plan introduces NDA/payment/PR-review-gate language without legal sign-off on intake gating phrasing, harassment-policy-safe `DECLINE_TEMPLATE` wording, or implicit-contract risk in `CONTRIBUTOR_INTEREST_TEMPLATE`. Discoverability gap (Gemini finding) is also a process/legal gap: lockdown blocks a path the plan mandates. | **GAP** — 4 structural lint tests defined but `test_plan_index_contains_2552_row` is brittle per Gemini (will fail when index rotates). No Red-state evidence; tests as written would pass tautologically once runbook file is created with the right headings. | NOT approval-ready |
| #2550 | **GAP** — 2026-04-30-final: Codex **MAJOR** (approval gate explicitly unmet; dry-run semantics internally contradictory between Pseudocode and AC; jq parser dependency unclear vs `requires: [bash, gh]`; report delivery target unresolved), Gemini **MAJOR** (open questions punted to user/executor; `mkdir -p logs/security/` missing; Hermes cron decommission step unactionable without machine-access clarification). | **MINOR GAP** — operation issues batched `gh api -X PUT` against 27 repos every ~150 days. No explicit attestation that this falls within standard `gh api` ToS / abuse-protection envelope. Low risk, but a one-line citation to GitHub's interaction-limits API documentation should be in the plan before approval. | **GAP** — 4 tests defined; `test_set_minus_e_propagates_jq_failure` mentions jq but `requires` list excludes jq (Codex MAJOR & Gemini MAJOR both flagged this). Patched away from Python mocks toward Bats per `feedback_mock_vs_live_invocation_divergence`, but Bats scaffold not yet written. No Red-state evidence. | NOT approval-ready |

## Why this is hardening, not approval

A `status:plan-review` plan can only move to `status:plan-approved` when both halves of the gate fire: GitHub label set by user **and** matching local marker `.planning/plan-approved/<issue>.md`. Neither half exists for any of these three issues. This audit identifies the evidence the user (and any future review agent) needs in order to make that approval decision defensibly. **It does not approve, recommend approval, or pre-authorize downstream agents** — explicit per `feedback_never_offer_to_self_label_plan_approved`.

## Bounded follow-up prompt pack

Each prompt is scoped to one issue × one evidence dimension, names input artifacts and output paths, and produces evidence-only deliverables. None invoke approval, none mutate labels, none touch `.planning/plan-approved/`.

### Prompt P1 — #2564 fresh adversarial fanout (provider availability gated)

```
Lane: plan-2564-fresh-fanout
Inputs:
  - Plan: docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md (commit 75a465894)
  - Prior 2026-04-29 fanout: scripts/review/results/2026-04-29-plan-2564-{claude,codex,gemini,disagreement}.md
  - Prior 2026-04-30 fanout (UNAVAILABLE): scripts/review/results/2026-04-30-plan-2564-{claude,codex,gemini}.md
  - Hermes governance note: scripts/review/results/2026-04-30-plan-2564-hermes-governance.md
Preconditions:
  - Codex CLI must NOT be 0.124.0 (regression per feedback_codex_cli_0_124_upstream_regression). Verify codex --version reports 0.123.0 or earlier; abort with EVIDENCE-OF-CLI-VERSION if 0.124.0.
  - Gemini provider must report capacity for the configured model; abort with EVIDENCE-OF-NO-CAPACITY if 429.
  - Claude SessionEnd hook must not be set to a version that aborts subagents (rc=124). Verify with a smoke `claude exec` returning under 30s.
Task:
  Run the standard cross-provider review fanout against the current plan revision (head of docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md as of dispatch). Use scripts/review/cross-review.sh or the equivalent skill. Produce three artifacts under scripts/review/results/<DATE>-plan-2564-{claude,codex,gemini}.md plus a -disagreement.md row.
Adversarial stance: every reviewer must hunt defects; no charitable reading; verdicts {APPROVE | MINOR | MAJOR}. Codex MUST cite at least one fallback-read path (js_repl or GitHub connector) per feedback_codex_sandbox_fallback_paths.
Out of scope: do NOT mutate labels, do NOT add approval markers, do NOT comment on the issue.
Deliverable: 4 artifact files written; STDOUT confirms each provider's verdict and a 1-line summary.
```

### Prompt P2 — #2564 calc-citation contract audit

```
Lane: plan-2564-citation-contract-audit
Inputs:
  - Rule: .claude/rules/calc-citation-contract.md
  - Pilot: digitalmodel/src/digitalmodel/citations/schema.py + digitalmodel/src/digitalmodel/orcaflex/mooring_design.py
  - Plan: docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md
  - Plan addendum: docs/plans/2026-04-30-issue-2564-mnt-ace-raw-reference-review.md
  - LLM-wiki anchors: knowledge/wikis/naval-architecture/wiki/concepts/{yaw-moment-rudder-sweep,rudder-force-modeling,maneuvering-coordinate-conventions,maneuvering-validation-metrics,environmental-yaw-moment-coefficients}.md
Task:
  Enumerate every numeric or formulaic constant the plan would introduce when implemented. For each, classify as (a) standards-derived (Citation REQUIRED), (b) code-derived/conventional (no Citation), (c) literature/research-only (no Citation per #2481 D2). Produce a per-constant table with classification + rationale + target wiki page (under wiki/standards/, not wiki/sources/, per project_wiki_standards_path_decision memory and rule §7).
  Specifically resolve: is `rudder_normal_force(...)` driven by a constant from PNA Vol III, USNA EN400, Bertram, ABS Vessel Maneuverability Guide, IMO MSC/Circ.1053, USCG NVIC 6-95/7-89, or only by code-internal expressions? If any standards anchor exists, the plan MUST emit Citation in the implementation phase. Confirm or refute the plan's current "literature provenance, not Citation" stance per rule §7.
Output: docs/plans/2026-04-30-issue-2564-citation-audit.md with the table + recommendation. Optional appendix: any wiki-page frontmatter gaps (#2471 forward-adoption candidates).
Out of scope: do not write Citation code; do not edit the plan; do not approve.
```

### Prompt P3 — #2564 TDD Red-state scaffold

```
Lane: plan-2564-tdd-red-state
Inputs:
  - Plan: docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md (TDD Test List section)
  - Existing maneuverability module: digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py
Task:
  Write the test file digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py with failing tests covering:
    1. Absolute sign convention (+M_z for starboard rudder under positive forward speed; -M_z mirror for port; NOT just port==-starboard symmetry)
    2. Package-data YAML access via importlib.resources (locates digitalmodel/src/digitalmodel/naval_architecture/data/typical-ship-yaw-sweep.yaml)
    3. Speed-unit conversion (knots ↔ m/s round-trip exactness within 1e-9)
    4. Sweep cardinality (Cartesian product of speeds × angles == len(speeds) * len(angles))
    5. Output schema (CSV header lock, JSON top-level keys lock, provenance metadata required keys)
    6. Chart artifact contract (filename pattern, count == 4 per the plan: yaw_moment_vs_angle_by_speed, yaw_moment_vs_speed_by_angle, transverse_force_vs_angle_by_speed, yaw_moment_speed_angle_heatmap)
  Run uv run pytest digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py -v and capture stdout/stderr to evidence/2564-tdd-red-state.txt. Every test MUST fail or error (Red). Save evidence file.
Out of scope: do NOT write production code in maneuverability.py; do NOT create the YAML; only the test file + evidence capture.
```

### Prompt P4 — #2552 adversarial remediation pass

```
Lane: plan-2552-remediation
Inputs:
  - Plan: docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md (commit 2734c103)
  - Codex final: scripts/review/results/2026-04-30-plan-2552-codex-final.md (MAJOR)
  - Gemini final: scripts/review/results/2026-04-30-plan-2552-gemini-final.md (MAJOR)
Task:
  Edit the plan to address every MAJOR finding:
    - Codex M1 (approval gate self-fail): demote stale 2026-04-29 evidence; cite either the fresh rerun artifacts (after P5/P6 below land) or an explicit user waiver. Do NOT add the waiver yourself; mark as `WAIVER-PENDING-USER`.
    - Codex M2 (cross-provider evidence incomplete): add explicit "approval-ready iff" gate text that lists the artifact paths and verdicts required.
    - Codex MINOR1 (unverified context claims): add command/output evidence for #2546 closeout, #2401 status, and the 2734c103 SHA.
    - Codex MINOR2 (stale embedded timestamps): replace 2026-04-29 timestamps with 2026-04-30 attested ones or move to a `## Historical context` block.
    - Gemini M1 (brittle `test_plan_index_contains_2552_row`): drop this test; replace with a one-time process check (a comment in the runbook noting "verify plan-index entry on landing").
    - Gemini M2 (off-GitHub contact path undiscoverable): add `Files to Change` row for CONTRIBUTING.md (or README.md) update naming the contact path while interaction-limits are active. Cross-link from docs/security/external-contributor-runbook.md.
  After patches, write a remediation summary at docs/plans/2026-04-30-issue-2552-remediation.md mapping each finding → patch → diff hunk reference.
Out of scope: do NOT change `status:plan-review` label; do NOT add `.planning/plan-approved/2552.md`; do NOT request approval.
```

### Prompt P5 — #2552 legal/policy review of paid-pilot intake

```
Lane: plan-2552-legal-review
Inputs:
  - Plan: docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md (post-P4 if P4 has landed)
  - Memory pointer: feedback_recruiter_engagement.md (consulting-level + credible source standard)
  - Trust governance: docs/governance/TRUST-ARCHITECTURE.md
Task:
  Adversarially review the runbook's four scenarios against three legal/policy axes:
    A. Implicit-contract risk: does any DECLINE_TEMPLATE or CONTRIBUTOR_INTEREST_TEMPLATE wording create offer / counter-offer / consideration that could imply a contract? Suggest minimum safe wording.
    B. Harassment-policy compliance: does the hide-not-reply default or the DECLINE_TEMPLATE expose the project owner to harassment-policy breach claims by hidden commenters? Cross-check GitHub Community Guidelines for "report" vs "hide".
    C. NDA + paid-pilot scope: even though the NDA template is deferred, the plan introduces NDA/payment/PR-review-gate language. Flag any clause that creates expectation of confidentiality or work-product ownership without an NDA. Recommend a "no-NDA-no-engagement" gate phrasing.
  Produce docs/plans/2026-04-30-issue-2552-legal-review.md with one section per axis, each with verdict {OK | FLAG | BLOCK} and rationale. BLOCK means the plan must be revised before approval.
Out of scope: do not draft an NDA template; do not approve; do not file new issues.
```

### Prompt P6 — #2552 TDD Red-state scaffold (post-P4 patch)

```
Lane: plan-2552-tdd-red-state
Preconditions: P4 landed (brittle plan-index test removed).
Inputs:
  - Plan: docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
Task:
  Write tests/security/test_runbook_external_contributor.py with the THREE remaining structural lint tests (file exists; covers four scenario headings; contains DECLINE_TEMPLATE + CONTRIBUTOR_INTEREST_TEMPLATE + HIDE_CHECKLIST strings) plus a fourth test verifying `external-contributor-runbook` is referenced in docs/governance/TRUST-ARCHITECTURE.md.
  Run uv run pytest tests/security/test_runbook_external_contributor.py -v and capture to evidence/2552-tdd-red-state.txt. All four tests MUST be Red (file does not yet exist).
Out of scope: do NOT create docs/security/external-contributor-runbook.md; do NOT edit docs/governance/TRUST-ARCHITECTURE.md.
```

### Prompt P7 — #2550 adversarial remediation pass

```
Lane: plan-2550-remediation
Inputs:
  - Plan: docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md (commit 2734c103, post-batch2 patches)
  - Codex final: scripts/review/results/2026-04-30-plan-2550-codex-final.md (MAJOR)
  - Gemini final: scripts/review/results/2026-04-30-plan-2550-gemini-final.md (MAJOR)
Task:
  Edit plan to address every MAJOR finding:
    - Codex M1: same as P4 M1 (approval gate self-fail); add WAIVER-PENDING-USER if user requests waiver, otherwise wait for P9-driven fresh fanout.
    - Codex M2 (dry-run contradictory): split into `--dry-run` (report-only, exit 0 always) and `--check` (verify-only, exit 1 on non-compliance). Update Pseudocode AND Acceptance Criteria together.
    - Codex MINOR1 (jq dependency): pick one — either add jq to `requires` list and use standalone jq, or commit to `gh api --jq` and remove jq references from tests. Update both schedule-tasks.yaml AC and the test list to match.
    - Codex MINOR2 (report delivery): pick one — default to dated local report under `logs/security/` and gate GitHub-issue-comment behind `--post-comment` flag.
    - Gemini M1 (open questions): close every open question in `Risks and Open Questions` with a definitive decision before approval-readiness.
    - Gemini M2 (mkdir): add `mkdir -p logs/security/` in script init OR in schedule-tasks.yaml setup hook.
    - Gemini M3 (Hermes cron): specify the exact decommission command (e.g., `crontab -l | grep -v 'd9b2d1c2270d' | crontab -`) AND state the machine ace-linux-1 explicitly. If access not guaranteed, mark as a manual operator step.
  Write remediation summary at docs/plans/2026-04-30-issue-2550-remediation.md.
Out of scope: do not change `status:plan-review`; do not approve; do not add `.planning/plan-approved/2550.md`.
```

### Prompt P8 — #2550 GitHub API ToS / abuse-protection one-line attestation

```
Lane: plan-2550-tos-attestation
Inputs:
  - Plan: docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md (post-P7)
  - GitHub docs: https://docs.github.com/en/rest/interactions (web fetch)
  - Local memory: project_issue_2460_approval_binding (revision-bound approvals)
Task:
  Add a `## API compliance attestation` section to the plan citing:
    - GitHub interaction-limits API endpoint contract: https://docs.github.com/en/rest/interactions/repos
    - Rate-limit envelope: 27 PUT calls every ~150 days = ~0.18 calls/day average; well under the 5000-req/hr authenticated REST limit.
    - Abuse-detection envelope: bursting 27 calls in <60s sequentially is below the secondary rate-limit guidance (https://docs.github.com/en/rest/overview/resources-in-the-rest-api#secondary-rate-limits); add a `sleep 0.5` between repos for safety.
    - Private-repo skip: 405 response handling per existing plan note.
  Edit the plan to include this 4-bullet attestation. No code changes.
Out of scope: do not approve; do not run the script live; do not change `status:plan-review`.
```

### Prompt P9 — #2550 TDD Red-state scaffold (post-P7 patch, Bats)

```
Lane: plan-2550-tdd-red-state
Preconditions: P7 landed (jq decision made; dry-run/check semantics split).
Inputs:
  - Plan: docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
  - Existing security script pattern: scripts/security/secrets-scan.sh
  - Test framework: bats-core (per feedback_mock_vs_live_invocation_divergence; Python mocks rejected)
Task:
  Write tests/security/test_renew_interaction_limits.bats with FOUR Red-state tests:
    1. `--dry-run` calls `gh api GET` only, no PUT (verify by stubbing gh via PATH override and recording calls).
    2. All-compliant universe → exit 0 (stub gh to return `{"limit":"collaborators_only"}` for all 10 repos).
    3. One non-compliant repo → exit 1, "FAIL" present in stdout.
    4. Output enumerates all 10 public repo names (stub `gh repo list` to return a fixed fixture).
  Add `bats` to `requires` in schedule-tasks.yaml AC. Run `bats tests/security/test_renew_interaction_limits.bats` and capture to evidence/2550-tdd-red-state.txt. All four tests MUST be Red (script does not exist).
Out of scope: do NOT create scripts/security/renew-interaction-limits.sh; do NOT modify schedule-tasks.yaml beyond the test-driven `requires` line; do NOT approve.
```

## Cross-cutting hardening notes

- **Hermes activity caveat:** during this run, PIDs 2190414/2190922 were `git rebase --autostash` and PID 2193359 was `git merge FETCH_HEAD`. Per `feedback_hermes_active_preflight_check`, parallel commits to `main` can be reverted within minutes. Any agent dispatched on P1-P9 that needs to *commit* should preflight `pgrep -af 'git (rebase|stash push|commit|merge|reset)'` and use a worktree+feature-branch. P2/P5/P8 are pure plan-edit prompts, but they still write into the workspace — operators should batch their commits into a single isolated worktree (per `feedback_multi_agent_commit_serialization`) rather than dispatch nine concurrent serializing-on-`.git/index` lanes.
- **Provider availability is the binding constraint for #2564.** No amount of prompt engineering moves the needle until Codex CLI ≤0.123.0 is restored (issue #2479 per memory) AND Gemini capacity returns AND the SessionEnd hook timeout is investigated. P1 should run *after* operator confirms all three providers are healthy, not eagerly.
- **No prompt in this pack approves anything.** Every prompt explicitly disables label mutation, marker creation, and approval requests. The user-in-loop gate per `feedback_never_offer_to_self_label_plan_approved` remains intact across all nine handoffs.
- **Codex sustained-MAJOR pattern watch:** if P4 (#2552) or P7 (#2550) lead to a third-or-later round of Codex MAJOR while Claude/Gemini land MINOR, surface the consensus-vs-minority decision per `feedback_codex_sustained_major_loop` instead of auto-cycling.

## End-of-run state

- No git operations performed by this lane (no add, commit, push, branch, label, marker).
- Single artifact written: this file, untracked, in `docs/sessions/`.
- Approval state unchanged: #2564, #2552, #2550 remain `status:plan-review` with no local approval markers.
- Result file ENV-MISMATCH: prescribed `agent-logs/...` path is Read/Write blocked at this permission level; this fallback path is durable per `feedback_lane_result_path_outside_sandbox`.

## Completion timestamp

- **COMPLETED:** 2026-04-30T13:26:42Z
- **Elapsed:** ~15 minutes
- **Status:** evidence/handoff complete; no implementation, no approvals, no label changes.
