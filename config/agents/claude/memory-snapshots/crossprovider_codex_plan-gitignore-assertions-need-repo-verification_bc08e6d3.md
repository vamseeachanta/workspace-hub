---
name: crossprovider codex plan-gitignore-assertions-need-repo-verification
description: Plan gitignore assertions need repo verification, not assumption
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, gitignore, durability-contract]
---

Plans asserting paths are tracked must verify actual .gitignore state at attestation time. #2471 claimed `knowledge/wikis/*/wiki/**` was positively tracked, but live .gitignore excluded `/knowledge/wikis/*` except for engineering-only; proposed marine-engineering paths would remain ignored. Verify via `ls` and .gitignore inspection during plan resource-intelligence phase.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
