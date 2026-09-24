---
name: crossprovider codex tdd-gate-is-non-negotiable-cannot-claim-complian
description: TDD gate is non-negotiable; cannot claim compliance when implementation precedes tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, tdd-gate, governance]
---

Hard gate: 'TDD mandatory — tests before implementation; no exceptions' per AGENTS.md. Plans saying 'author artifact, then validate' then claiming TDD compliance fail review. #2443 said author .markdownlint.jsonc then assert, but claimed AGENTS-compliant TDD—this is backwards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
