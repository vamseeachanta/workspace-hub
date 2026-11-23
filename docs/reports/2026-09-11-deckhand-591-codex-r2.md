# Codex targeted adversarial review — Deckhand 591 revision 2

Verdict: **APPROVE — advisory plan review only.** No unresolved blocking plan defect established. Owner approval, implementation/code review, native qualification and deployment remain separate.

Reviewed [revision-2 plan](../plans/2026-09-11-deckhand-591-cleanup.html), SHA256 `565bf4e87b8113040ae1dfa6312c5e4e4646fd784ddd1e14482d68b7ce94a477`, against the pinned-source findings in [revision-1 review](2026-09-11-deckhand-591-codex-review.md).

## Finding disposition

- **C1 closed:** lifecycle item 6 now proposes an explicit additive `summary.cleanup` location in `_summary_payload`, a version-1 field/state contract, validation before release and serialization, actual agent-authored `summary.guard_state`, and round-trip tests through result writing/reading. It no longer assumes the pinned serializer preserves arbitrary runner fields. This is a proposed repair, not an implemented contract claim.
- **C2 closed:** unexpected descendants followed by confirmed absence will fail the workload but permit safe release; uncertainty will fail and retain quarantine. The outcomes are now distinct.
- **C3 closed:** crash qualification will retain independent process handles without retaining an observer Job Object handle across the supervisor crash. Normal/timeout tests will separately check job accounting. This avoids defeating kill-on-last-handle-close in the test itself.

## Additional contradiction checks

- Qualification is limited to trusted uv/Python descendants using ordinary CreateProcess inheritance. Brokered WMI/service launches and arbitrary executable hooks are excluded; the plan does not claim an arbitrary-code sandbox.
- Windows containment will precede resume; uncertain partial construction will retain ownership. A created-but-suspended process must not be reported `not_started`, whose contract now requires that no process was created. Such a branch will require confirmed cleanup or conservative quarantine.
- Non-Windows default execution will fail before spawn. Injected runners retain their call signature but intentionally require new proof; these breaking behaviors are explicitly included in the requested owner approval.
- Watchdog helper behavior remains unchanged and separately owned by [Deckhand 592](https://github.com/vamseeachanta/deckhand/issues/592). The risk section requires that owner to be reconciled before deployment claims about one managed lane.
- Guard retention/recovery is scoped to cooperating writers and a protected directory, with no stale-PID/age auto-unlock or power-loss durability claim. Failure to prove ownership or cleanup remains conservative unavailability.
- Bounded cleanup, file-backed diagnostics and release after observation are specified; native API behavior, durable guard handling and actual serializer acceptance still require the proposed tests and code review.

## Checks and write scope

Read the complete current plan, checked its SHA256 and compared the revised lifecycle, artifact map, native-test oracle and scope boundaries against the previously inspected pinned runtime/agent/queue/watchdog source. No native tests, solver processes or deployment actions were run. Only this review file was written; no commits or external comments were made. This verdict does not imply another provider's agreement.
