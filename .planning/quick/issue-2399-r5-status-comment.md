Fresh adversarial re-review completed on the latest #2399 draft.

Result: still NOT approval-ready
- Codex: MAJOR
- Gemini: MAJOR

Convergent remaining blockers:
1. retrieval/inventory still appears incomplete for repo-ecosystem scope
   - Codex specifically calls out missing Codex/Hermes parity surfaces such as `.codex/CODEX.md` and #1583-related Hermes parity signals in the concrete inventory path
2. the eval battery is still not considered operational enough
   - both reviewers still see the YAML + runner-contract shape as too abstract / not fixture-backed enough
3. artifact packaging is still judged too fragmented
   - multiple markdown artifacts are being read as documentation sprawl instead of one cohesive reviewable gap-analysis package
4. discoverability anchoring is still incomplete
   - Codex adapter anchoring is still called out explicitly

Operational note:
- Gemini produced a substantive review in this rerun (not just capacity failure), so the current blocker set reflects live cross-provider evidence.

Conclusion:
- keep #2399 below `status:plan-review`
- do not ask the user to approve this plan yet
- next revision should focus narrowly on:
  a. explicit `.codex/CODEX.md` + Hermes parity/repo-ecosystem surfaces in retrieval + artifacts
  b. one cohesive main artifact for gap analysis / upgrade guidance instead of excessive report fragmentation
  c. fixture-backed executable battery semantics rather than YAML/schema prose alone

Latest raw review artifacts:
- `.planning/quick/review-2399-codex-r5.out`
- `.planning/quick/review-2399-gemini-r5.out`
