Revised-plan re-review update (2026-04-14/15):

- Codex re-review: MAJOR
- Gemini re-review: blocked by provider capacity exhaustion (429 MODEL_CAPACITY_EXHAUSTED), so no fresh Gemini verdict was produced on the revised text.

Current blocker summary from Codex
1. The plan still does not define a concrete evidence source and decision rule for proving whether `issue-planning-mode` was actually used.
2. The audited population / denominator is still not defined tightly enough in the plan itself.
3. `status:plan-approved` sequencing is still not explicitly verified.
4. The final decision output (“keep current approach or escalate enforcement”) is still not explicit enough in deliverables/acceptance criteria.
5. The implementation path is still slightly too loose (`or equivalent`).

Immediate next revision needed
- define authoritative and fallback evidence sources for `issue-planning-mode` detection
- define rollout start, threshold, inclusion/exclusion rules, and legacy/mixed handling directly in the plan
- add explicit `status:plan-approved` chronology checks and tests
- add final decision/recommendation output as a required report section
- replace `or equivalent` with a concrete implementation path
- add tests for malformed review artifacts and conflicting-evidence resolution

This plan still is not approval-ready.
