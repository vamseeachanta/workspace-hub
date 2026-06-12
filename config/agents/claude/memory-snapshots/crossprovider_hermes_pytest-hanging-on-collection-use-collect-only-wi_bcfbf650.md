---
name: crossprovider hermes pytest-hanging-on-collection-use-collect-only-wi
description: pytest hanging on collection: use --collect-only with timeout to isolate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest, debugging, collection]
---

For repos where `pytest` hangs during collection (no output, process stuck), run `pytest --collect-only -x` with a timeout to identify which file/import causes the hang. Test files with heavy/network imports or conftest side effects are common culprits; --noconftest can isolate conftest-specific hangs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
