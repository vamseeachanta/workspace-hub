Second adversarial review wave for #2408 completed / partially completed.

Current status: still NOT approval-ready
- Codex: MAJOR
- Gemini: incomplete at time of check (startup/agent-loading warnings persisted; no clean substantive completion captured within the wait window)

Converged current blocker from Codex:
- discoverability consistency across existing provider-facing entrypoints is still not fully resolved; updating only `AGENTS.md` + `CONTROL_PLANE_CONTRACT.md` is likely insufficient if root/provider entry surfaces continue to point elsewhere

Operational note:
- Gemini run did not yield a clean substantive verdict in the allotted wait window; treat the Gemini lane as incomplete rather than approved.

Recommendation:
- do not request approval yet
- next revision should decide one of two explicit strategies:
  1. strict canonical-anchor strategy with a documented audit-only treatment for provider entrypoints, or
  2. include provider-entrypoint convergence in scope and update the affected files directly

Latest raw artifacts:
- `.planning/quick/review-2408-codex-r3.out`
- `.planning/quick/review-2408-gemini-r3.out`
