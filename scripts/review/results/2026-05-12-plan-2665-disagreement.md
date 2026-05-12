# Fresh adversarial review synthesis for #2665

## Review wave
- Date: 2026-05-12
- Scope: revised local plan `docs/plans/2026-05-12-issue-2665-provider-credit-approval-dashboard-dispatch-gates.md`
- Local/uncommitted status was explicitly not treated as a blocker.

## Verdicts
| Reviewer | Verdict | Blocking themes |
|---|---|---|
| Claude-style | MINOR | Acceptance command incomplete; #2519/dispatcher coexistence should be enforceable; strict issue inference must fail closed. |
| Codex-style | MAJOR | Approval authority too broad; missing per-issue approval lock; cross-host lease model not enforceable; non-leader dispatch gap; strict mode ambiguity. |
| Gemini-style | MAJOR | Existing `continuous-planning-pipeline.py` omitted; test paths/acceptance command incomplete; integration/reuse contract missing. |

## Accepted revisions required
1. Change approval authority to explicit **user approval**; local operator mechanics are only a transport for the user action, not delegated approval authority.
2. Add per-issue approval transaction lock and concurrent approval/resume race tests.
3. Centralize lease creation on ace-linux-1/Hermes leader; ace-linux-2 is worker-only unless explicitly promoted with a single-writer handoff that disables ace-linux-1 writes.
4. Require strict issue-specific approval checks to fail closed on missing/ambiguous issue mapping.
5. Integrate with `scripts/ai/continuous-planning-pipeline.py` for plan/review/marker/lane readiness instead of duplicating those classifiers.
6. Correct regression test paths and acceptance command to include all modified existing surfaces.

## Ready for user approval?
No before revision. After the above plan edits, a focused re-review should verify no MAJOR remains.
