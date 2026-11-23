Recommended decomposition for #2399 is now created as narrower child issues.

Created child issues:
1. #2408 — workspace-hub-only model-release readiness contract and upgrade playbook
2. #2409 — fixture-backed golden-task corpus for model-release comparisons
3. #2410 — smoke-battery schema and runner contract (no runner implementation)
4. #2411 — tier-1 provider entrypoint and parity surface inventory
5. #2412 — deterministic follow-up issue creation and dedup policy

Recommendation:
- treat #2399 as the parent umbrella / steering issue
- move detailed plan approval and execution sequencing into the child issues above
- stop trying to force all five scopes through one approval gate

Suggested next approval order:
A. #2408
B. #2409
C. #2411
D. #2410
E. #2412

Rationale:
- #2408 gives the narrowest contract surface
- #2409 and #2411 produce the evidence base the ecosystem-level work was missing
- #2410 and #2412 isolate the two most review-sensitive subsystems (runner semantics and issue creation policy)
