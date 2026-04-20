Latest strategy-B review wave for #2408 completed.

Current result: still NOT approval-ready
- Codex: MAJOR
- Gemini: MAJOR

Converged blocker pattern now:
1. authority model is still ambiguous
   - the plan still mixes canonical-anchor language with direct provider-entrypoint updates
2. hidden-vs-root provider surfaces are still not consistently modeled
   - `.claude/CLAUDE.md` and `.gemini/GEMINI.md` are still not cleanly aligned with the test/artifact story
3. the issue is drifting from contract-definition into provider-entrypoint normalization
4. review-output / plan-index bookkeeping is still being read as unnecessary scope

Recommendation after this wave:
- do not request approval on #2408 yet
- choose one hard direction next:
  A. strict canonical-doc strategy: only `AGENTS.md` + `CONTROL_PLANE_CONTRACT.md` are changed, all provider files are audit-only and explicitly left untouched
  B. entry-surface normalization strategy: explicitly widen scope to normalize provider-facing entry surfaces as part of the issue

At this point, A is the cleaner recommendation for #2408.
Use a separate follow-up issue for provider-entrypoint normalization if still needed.

Latest raw artifacts:
- `.planning/quick/review-2408-codex-r4.out`
- `.planning/quick/review-2408-gemini-r4.out`
