Adversarial plan review is complete for #2024.

Verdicts
- Codex: MAJOR
- Gemini: MAJOR
- Ready for user approval: No

Shared blockers
1. The plan still leaves core design decisions unresolved: thread-vs-message unit of work, exact state schema, deletion semantics, attachment handling, and rollback/failure ordering.
2. The plan does not fully implement the issue’s required CLI/action contract.
3. Migration safety is underspecified, especially the required phased coexistence/validation path before replacing gmail-archive-extract.py.
4. Retrieval and TDD are incomplete for a risky stateful data-pipeline rewrite.

Provider-specific emphasis
- Codex focused on unsafe ambiguity in lifecycle/deletion/legal-scan/write ordering, missing downstream write contract, and inadequate falsifiable acceptance criteria.
- Gemini focused on the missing CLI architecture, ignored 5-phase migration strategy, missing Gmail label contract, and unresolved thread-state design.

Artifacts
- scripts/review/results/2026-04-14-plan-2024-codex.md
- scripts/review/results/2026-04-14-plan-2024-gemini.md

Conclusion
- #2024 is not approval-ready.
- The earlier MAJOR review stands and is reinforced by both external provider reviews.
