Adversarial plan review is complete for #2128.

Verdicts
- Codex: MAJOR
- Gemini: MAJOR
- Ready for user approval: No

Shared blockers
1. Governance state is inconsistent relative to review/approval/execution state.
2. The implementation strategy is not yet safely chosen.
3. The current patching/insertion design is too brittle for a hook-modification issue.
4. Tests do not yet prove the real downstream behavior that matters.

Provider-specific emphasis
- Codex focused on governance drift, missing #1839 grounding, and insufficient end-to-end downstream validation.
- Gemini focused on the concrete technical flaw: insertion point/order is wrong, skip-if-present preserves the bug, and exit-search patching is unsafe.

Artifacts
- scripts/review/results/2026-04-14-plan-2128-codex.md
- scripts/review/results/2026-04-14-plan-2128-gemini.md

Conclusion
- #2128 is not approval-ready.
- It needs revision and re-review before any plan-approval step.
