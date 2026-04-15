# Adversarial Re-Review — Plan #2269 (Codex, wave 2)

Date: 2026-04-15
Issue: #2269
Plan: docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md
Reviewer: Codex CLI
Reviewer mode: adversarial
Overall verdict: MAJOR
Ready for user approval: No
Retrieval adequacy: adequate

Top blockers
- fork/version verification mechanism is still not pinned tightly enough
- bootstrap-path contract still needs a definitive supported-path policy
- final YAML schema remains incomplete around tutorial row structure and deterministic typing
- TDD still needs stronger pre-implementation determinism around mocks/fixtures and normalization behavior

Critical findings
- User approval should not proceed until the live/runtime truth for bootstrap path and version-detection command is pinned tightly enough to remove contradictory interpretations.

High findings
- The final YAML schema must define the exact `tutorials` structure and required per-tutorial fields.
- Required deliverables/tests still contain residual optional language or broad wording in places that should be exact.
- Requirement traceability is improved but some mapped tests remain broader than the linked requirement.

Medium findings
- Runtime truth is still under-specified relative to the number of internal docs cited.
- The risk section mixes actual risks with already-made decisions and should separate them more cleanly.

Low findings
- T2 may still be optimistic, but acceptable.

Required revisions before user approval
1. Pin the exact fork/version verification mechanism: command, parse rule, error behavior, and what is written to `verification_method`.
2. Resolve the bootstrap-path contract decisively: either one canonical path with the other treated as legacy troubleshooting, or an explicitly supported two-path baseline.
3. Define the final YAML schema completely, including `tutorials` structure and required per-tutorial fields.
4. Make TDD deterministic with explicit mocks/stubs/fixtures for bashrc probing, version detection, runner exit behavior, and YAML normalization.
5. Remove optional language from required deliverables and acceptance criteria.
6. Clarify the reproducibility contract for `examples/openfoam/cavity-v2312/README.md` beyond prose alone.
7. Keep the review summary explicit about what MAJOR issues remain after the latest patch wave.
