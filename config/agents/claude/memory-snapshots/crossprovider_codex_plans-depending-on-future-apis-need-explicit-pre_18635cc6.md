---
name: crossprovider codex plans-depending-on-future-apis-need-explicit-pre
description: Plans depending on future APIs need explicit precondition contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, cross-issue-dependency, api-contract]
---

Multiple plans assumed unimplemented APIs (#602, #603) would land with specific signatures (e.g., `build_modular_spec(spec_path: str | Path) -> dict`) without making those exact contracts preconditions or requiring compatibility checks. This creates fragile cross-issue dependencies where implementation changes silently invalidate the plan. Bind future API shapes to their issue acceptance criteria or make verification a gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
