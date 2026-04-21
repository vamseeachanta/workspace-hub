## Summary

`config/agents/hermes/SOUL.md` currently contains only a generic Nous Research system prompt and has **zero references** to `AGENTS.md`, planning workflow, gate enforcement, plan approval, or TDD. If Hermes is used for implementation work, it has no gate awareness — any Hermes-driven commit would bypass workflow discipline.

## Context

Identified during #2018 plan development (`docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` §Provider Bootstrap Surface Inventory). The #2018 plan lists this as an implementation requirement:

> The Hermes gap must be closed by either (a) adding gate/workflow references to `config/agents/hermes/SOUL.md`, or (b) documenting that Hermes is not authorized for implementation tasks and therefore does not require gate enforcement.

Under the middle-path governance close of #2018, this gap is being extracted as its own tracked issue so #2018 can close on bypass-matrix infrastructure coverage while the Hermes onboarding question is answered independently.

## Verification of the gap (2026-04-21)

```
$ grep -iE "AGENTS\.md|plan|approval|TDD" config/agents/hermes/SOUL.md
(no matches)
```

Compared with other provider adapters:
- `CLAUDE.md` — references `AGENTS.md` and the mandatory planning workflow.
- `GEMINI.md` — references `AGENTS.md` for canonical contract.
- `.codex/CODEX.md` — explicit Required Gates section.
- `config/agents/hermes/SOUL.md` — none of the above.

## Decision required

Either:

**(a) Retain Hermes as implementation-capable provider:**
- Add `AGENTS.md` gate references OR the literal gate-order keywords (plan / approval / TDD) to `config/agents/hermes/SOUL.md`.
- Add a test under `tests/enforcement/` (`test_agent_bootstrap_surfaces_receive_constraints`) asserting presence of the required references.

**(b) Restrict Hermes to non-implementation use:**
- Add an explicit "non-implementation provider — not authorized to commit code or modify gated files" marker to SOUL.md.
- Add the same test, asserting presence of the non-implementation marker instead.
- Update AGENTS.md to reflect the restriction.

## Acceptance criteria

- [ ] Decision is made and documented (comment or plan file).
- [ ] `config/agents/hermes/SOUL.md` reflects the decision.
- [ ] Test `test_agent_bootstrap_surfaces_receive_constraints` added under `tests/enforcement/` verifying either gate references OR the non-implementation marker for Hermes.
- [ ] Other provider adapters (`CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`) spot-checked as still consistent.
- [ ] AGENTS.md updated if decision is (b).

## References

- Parent plan: `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` §Provider Bootstrap Surface Inventory
- Sibling child: #2289 (bypass rollback/recovery — covers enforcement recovery after a bypass)
- Parent issue: #2018 (agent bypass resistance — detection/prevention; this issue is about a gap in detection via agent onboarding)

## Complexity

T1 — single-file content change in `config/agents/hermes/SOUL.md`, plus one test under `tests/enforcement/`.

## Priority

Medium — no active harm today (Hermes not currently running implementation), but present gap is documented.
