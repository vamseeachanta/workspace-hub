# #2489 Continuous Planning Pipeline — Exit Handoff

Date: 2026-04-26
Repo: `vamseeachanta/workspace-hub`
Parent issue: https://github.com/vamseeachanta/workspace-hub/issues/2489
Current parent status: `status:plan-review`
Latest committed plan/review commit: `38cc66ec1 docs: refresh issue 2489 control-plane plan review`

## Current state

The canonical #2489 plan has been materially revised after cross-review with the ongoing Claude autonomous routine wave and adversarially re-reviewed.

Canonical plan:
- `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md`
- Current plan SHA256: `2071816fea65fb4d8fb5187eb8d9b7f6e5f465a6e714c4b9b3421c1210b2ea7b`

Review artifacts:
- `scripts/review/results/2026-04-26-plan-2489-claude.md` — governance/source-of-truth — `MINOR`
- `scripts/review/results/2026-04-26-plan-2489-codex.md` — scheduler/executor reliability — `MINOR`
- `scripts/review/results/2026-04-26-plan-2489-gemini.md` — next-day user-review/productivity — `MINOR`
- `scripts/review/results/2026-04-26-plan-2489-disagreement.md` — synthesis — no MAJOR blockers

GitHub update posted:
- https://github.com/vamseeachanta/workspace-hub/issues/2489#issuecomment-4322674327

## Gate state

#2489 is ready for explicit user approval, but **not implementation-ready**.

Implementation remains blocked until both are true:

1. user explicitly approves the revised plan, and
2. `.planning/plan-approved/2489.md` exists as a valid approval marker.

The parent issue label was restored to `status:plan-review` because a material plan revision invalidated the prior plan-approved label and no local approval marker exists.

## Follow-up issues created

These issues capture the MINOR/future-hardening work surfaced by final adversarial review. They are not blockers to approving #2489, but they should be planned in the same hard-stop workflow before implementation.

| Issue | Title | Purpose |
|---|---|---|
| #2502 | [feat(ai-orchestration): harden plan-review artifact metadata and stale-SHA handling](https://github.com/vamseeachanta/workspace-hub/issues/2502) | Make current-vs-stale provider review evidence machine-checkable and hard to misread. |
| #2503 | [feat(ai-orchestration): standardize canonical approval-request comments for plan-review issues](https://github.com/vamseeachanta/workspace-hub/issues/2503) | Define/backfill the Lane A approval-comment schema without creating approval authority. |
| #2504 | [feat(ai-orchestration): define dispatch-ledger trust contract and lease lifecycle writer](https://github.com/vamseeachanta/workspace-hub/issues/2504) | Specify trusted ledger/writer/lease behavior as a separate follow-up from #2489 v1 reporting. |
| #2505 | [feat(ai-orchestration): add golden-output contract for morning approval and QA packet](https://github.com/vamseeachanta/workspace-hub/issues/2505) | Keep the morning packet decision-dense, capped, and useful under sparse/degraded evidence. |
| #2506 | [feat(ai-orchestration): validate Lane E implementation handoff readiness](https://github.com/vamseeachanta/workspace-hub/issues/2506) | Separate open implementation PRs from genuinely review-ready Lane E handoffs. |

## Recommended next session sequence

1. If user approves #2489, create `.planning/plan-approved/2489.md`, move #2489 to `status:plan-approved`, then begin implementation.
2. If user wants more planning depth first, start with #2502 and #2503 because they improve source-of-truth quality for every later Lane A/B decision.
3. Treat #2504 as the bridge from read-only control-plane reporting into actual scheduler/lease authority; do not fold it into #2489 v1 unless explicitly approved.
4. Treat #2505 and #2506 as next-day productivity hardening for the morning review/QA loop.

## Exit verification notes

At handoff creation time:
- #2502–#2506 were verified open with labels: `enhancement`, `priority:medium`, `cat:ai-orchestration`, `cat:harness`, `domain:workflow`.
- #2489 labels were verified as: `enhancement`, `priority:high`, `cat:ai-orchestration`, `cat:harness`, `domain:workflow`, `status:plan-review`.
- No `.planning/plan-approved/2489.md` marker existed.

## Do not do on restart

- Do not implement #2489 before explicit user approval and marker creation.
- Do not treat #2502–#2506 as pre-approved; each needs the normal issue → plan → adversarial review → user approval flow.
- Do not let remote scheduler/Claude routine state outrank repo/GitHub evidence.
- Do not recreate duplicate follow-up issues unless these are closed or superseded.
