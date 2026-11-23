Fresh adversarial re-review completed on the newest blocker-focused #2399 draft.

Result: still NOT approval-ready
- Codex: MAJOR
- Gemini: MAJOR

Latest converged blockers:
1. ecosystem-vs-workspace boundary is still not fully settled
   - Codex still sees risk that the plan is defining a repo-ecosystem contract from too workspace-hub-local an evidence base
2. contract specificity is still too generic in some dimensions
   - Gemini explicitly calls out missing forced coverage for:
     - context-budget / truncation-safe artifact design
     - machine-readable rules/skills vs prose-only guidance
3. verification is still too structural and not outcome-oriented enough
   - Codex wants scoring/normalization semantics for comparing releases, not just fixture existence
   - Codex also wants dedupe/idempotence checks around issue creation
4. Hermes-specific discoverability/entry surface is still under-modeled
   - Gemini asked for Hermes anchoring parity analogous to Codex anchoring

Practical recommendation:
- keep #2399 below `status:plan-review`
- do not ask the user to approve yet
- next rewrite should be one last narrow pass for:
  a. explicit required-dimension forcing in pseudocode/tests/ACs
  b. scoring/normalization semantics for the battery
  c. issue-creation idempotence/dedup checks
  d. Hermes-specific discoverability anchor treatment
  e. explicit note on how far repo-ecosystem sampling goes in this issue vs follow-up work

Latest raw review artifacts:
- `.planning/quick/review-2399-codex-r6.out`
- `.planning/quick/review-2399-gemini-r6.out`
