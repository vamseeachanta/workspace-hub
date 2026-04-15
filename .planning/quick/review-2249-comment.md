Adversarial plan review is complete for #2249.

Verdicts
- Codex: MAJOR
- Gemini: MAJOR
- Ready for user approval: No

Shared blockers
1. The plan is still not approval-ready and currently misstates prior review status.
2. Retrieval is insufficient for a cat:data-pipeline issue because key machine-readable execution surfaces and schema details were not grounded before defining behavior.
3. The scoring/packing rubric is not fully trustworthy yet, especially around unverified fields and missing/null metadata handling.
4. The #2247 handoff contract is overstated/ambiguous relative to the current implementation.

Provider-specific emphasis
- Codex focused on governance drift, incorrect representation of prior MAJOR reviews, missing retrieval from classifier/writeback implementation surfaces, and invalid assumptions about #2247 consumer semantics.
- Gemini focused on schema-level flaws: unverified readability field, hardcoded live-count tests, null-handling gaps, and underspecified manifest contract.

Artifacts
- scripts/review/results/2026-04-14-plan-2249-codex.md
- scripts/review/results/2026-04-14-plan-2249-gemini.md

Conclusion
- #2249 is not approval-ready.
- It needs revision plus re-review before any plan-approval step.
