---
name: crossprovider codex cli-contract-completeness-missing-flags-mean-mis
description: CLI contract completeness: missing flags mean missing scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli, contracts, scope, testing]
---

When CLI interface is approved/specified, all required repeatable flags must be implemented. Missing flags like `--issue`, `--pr-range`, or `--artifact` mean those selection paths don't work, violating the approved scope. Test against actual approved command examples, not just happy paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
