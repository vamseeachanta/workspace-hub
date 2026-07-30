---
name: crossprovider codex absolute-path-guards-block-committed-client-data
description: Absolute-path guards block committed client-data leaks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [security, committed-secrets, ci-guards, digitalmodel]
---

digitalmodel repo has a known committed client-data leak (machine/field/client names hardcoded in scripts). Use `--added mode` checks in CI to block new absolute paths or client identifiers in commits. Review memory file `digitalmodel-committed-client-leak-*` before pushing PRs that mention infrastructure/clients.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
