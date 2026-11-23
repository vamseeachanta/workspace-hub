# Plan-Review Triage — 2026-05-13

Read-only triage of 8 open workspace-hub issues nominally labelled `status:plan-review`. No issues were modified and no comments were posted.

## Classification Summary

| Count | Classification |
|---|---|
| 3 | APPROVE-READY |
| 2 | CLOSE (mislabeled / executed; need label correction, not approval) |
| 1 | STALE |
| 1 | NEEDS-REVISION |
| 1 | NEEDS-REVISION (sustained-MAJOR; consider park/escalate) |

## Per-Issue Triage (recommended order of attention)

### Tier 1 — Quick wins (approve or close)

#### 1. #2683 — Claude SessionEnd hook crashes plan-review-fanout — **CLOSE (already executed)**
- **Rationale:** Label is actually `status:plan-approved` (not `plan-review`), and `scripts/review/plan-review-fanout.sh:159` already contains the `claude --bare -p ...` patch. The single-line change appears to have landed; only ceremony (close issue, post implementation note) remains.
- **User action:** Verify on disk, then close the issue. If the verification artifact (TDD + comment) was skipped, ask for a quick implementation summary comment before close.
- **Plan file:** `docs/plans/2026-05-12-issue-2683-claude-bare-flag-for-fanout.md` (exists).

#### 2. #2653 — WRK-694 per-session log files in session-logger.sh — **CLOSE (stage progress shows complete)**
- **Rationale:** Issue body Stage Progress shows steps 1-17 already marked **done** (including User Review - Implementation). Only stages 18 (Reclaim) and 19 (Close) are pending. Label `status:plan-review` is stale — the work has actually run through implementation review per the issue's own stage tracker.
- **User action:** Verify behavior of `.claude/hooks/session-logger.sh` matches acceptance criteria, then close. No fresh plan review is needed.
- **Plan file:** `docs/plans/2026-05-06-issue-2653-per-session-log-files.md` (exists).

#### 3. #2683's twin pattern — n/a (only #2683 falls in this category)

### Tier 2 — APPROVE-READY (plan is clean, scope is bounded, awaiting thumbs-up)

#### 4. #2626 — Narrow #2552 external-contributor runbook tests — **APPROVE-READY**
- **Rationale:** T1 plan with 4 clearly enumerated defect fixes, TDD contract (positive-presence + fixed-string negative), ingestion-vector ADR. Single contained scope, no upstream blocker.
- **User action:** Approve (move label to `status:plan-approved`).
- **Plan file:** `docs/plans/2026-05-03-issue-2626-narrow-2552-runbook-fixes.md` (exists).

#### 5. #2528 — Retire 6 deprecated email skills + update gmail-triage — **APPROVE-READY** (with 2 open questions surfaced)
- **Rationale:** T1 plan, all 6 `_archived/` twins verified on disk, 13 file actions enumerated, 6 TDD grep tests defined. Plan explicitly surfaces two open questions (gmail-data-extraction DELETE vs KEEP; gmail-operations KEEP vs DELETE) needing user resolution before approval.
- **User action:** Answer the two open questions in the plan, then approve. Recommend DELETE for `gmail-data-extraction` (per plan author) and KEEP for `gmail-operations`.
- **Plan file:** `docs/plans/2026-05-06-issue-2528-retire-deprecated-email-skills.md` (exists).

#### 6. #2551 — Audit branch/ruleset protections across public repos — **APPROVE-READY**
- **Rationale:** T2 plan with 10-column evidence table contract, 6 GitHub API sources mapped, 5 TDD tests defined, 4 risks flagged (404→none mapping, time-bound interaction limits, MCP-scope, personal-vs-org). Deliverables auditable and bounded.
- **User action:** Approve.
- **Plan file:** `docs/plans/2026-05-06-issue-2551-security-audit-public-repos-branch-protection.md` (exists).

### Tier 3 — NEEDS-REVISION (scope/dependency issues)

#### 7. #2632 — Rebind 3 llm-wiki plan-approved issues stuck on missing approval markers — **NEEDS-REVISION (STALE)**
- **Rationale:** Plan dated 2026-05-04; covers approval-binding rot for 3 llm-wiki issues. Per MEMORY entry `project_llm_wiki_spunout` (2026-05-05), the llm-wiki repo has been spun out to a dedicated public repo. Approval-binding contract from issue #2460 (`project_issue_2460_approval_binding`) requires SHA + review artifact paths + storage surface — recheck whether the 3 affected issues still live in workspace-hub or have migrated. Plan may need a target-repo rebase before approval.
- **User action:** Confirm whether the 3 child issues are still tracked in workspace-hub, or whether the sweep should run against the spun-out llm-wiki repo. Plan needs explicit issue-list and target-repo before approval.

#### 8. #2643 — Plan metadata-only /mnt/ace-data source coverage triage — **STALE**
- **Rationale:** Plan dated 2026-05-04; T2 metadata-only inventory of 14 raw-like roots under `/mnt/ace`. Per MEMORY `project_elements_drive_identity` and `2026-04-27-elements-drive-ingest-handoff.md`, the `/mnt/ace` ingest landscape has shifted (Elements drive ingest, new WD 4TB at `/mnt/elements`). Frozen inventory artifact at `data/document-index/ace-data-raw-like-inventory-2026-05-04.yaml` may already be drifting. Also part of the llm-wiki cluster (spinoff 2026-05-05) — needs scope re-confirmation against the new repo boundary.
- **User action:** Re-baseline the inventory against current `/mnt/ace` + `/mnt/elements` state; clarify which repo (workspace-hub vs llm-wiki) is the routing target post-spinoff. Then re-surface for review.

#### 9. #2510 — Build Python layout/CAD automation demo — **NEEDS-REVISION (sustained-MAJOR — escalate decision)**
- **Rationale:** **14 adversarial review rounds (r1 through r14)** with persistent MAJOR verdicts. r14 (2026-05-02) surfaced 3 non-overlapping P1 defects (PDK activation missing, forbidden-phrase test hole, duplicate r13 summary rows) that prior 13 rounds missed. This is the textbook anti-pattern from MEMORY `feedback_codex_sustained_major_loop` (#2045, #2289). User attempted `approved via gh label route` but was retracted. Plan also lists 35+ review-artifact files in `scripts/review/results/` — review tooling is now bigger than the planned deliverable.
- **User action:** Decision point per `feedback_codex_sustained_major_loop` — either (a) accept r14's 3 P1 patches inline and approve as-is without r15, (b) explicitly park the issue (CAD demo is portfolio-grade, not blocking), or (c) shrink scope to a minimal PDK-activated GDS round-trip and re-spec. Continuing to r15+ is the wrong move.

## Patterns Observed

1. **llm-wiki spinoff aftershock:** Two of the eight issues (#2632, #2643) are llm-wiki coverage/governance plans drafted *before* the 2026-05-05 spin-out to the dedicated public repo. Both need target-repo re-confirmation, not just freshness.
2. **Stale `status:plan-review` labels are masking executed work:** #2683 (label drift to `plan-approved` + patch landed) and #2653 (stage tracker shows 17/19 done) are *not* actually awaiting plan approval. The label query over-counts open plan-review work by 25%.
3. **Sustained-MAJOR governance miss on #2510:** 14 review rounds without invoking the documented park/escalate rule. Repo's own MEMORY warns against this exact loop; tooling did not surface the threshold.
4. **All plan files exist on disk** — no phantom-plan rot. The Write/commit pipeline is healthy; the gap is in label hygiene and post-execution close-out.

## Recommended Order

1. **#2683** — verify line 159 patch landed → close (1 min)
2. **#2653** — verify session-logger.sh behavior → close (5 min)
3. **#2626** — approve as-is (T1, narrow)
4. **#2528** — answer 2 open questions → approve (T1, mechanical)
5. **#2551** — approve as-is (T2, well-scoped audit)
6. **#2632** + **#2643** — batched re-baseline against llm-wiki spinoff; both need clarification before approval
7. **#2510** — sustained-MAJOR decision call: accept r14 inline, park, or re-spec

## File

This report: `/mnt/local-analysis/workspace-hub/docs/sessions/2026-05-13-plan-review-triage.md`
