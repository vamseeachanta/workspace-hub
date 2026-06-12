---
name: crossprovider hermes pytest-asyncio-incompatibility-with-hypothesis-d
description: pytest-asyncio incompatibility with hypothesis: disable globally
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest, asyncio, hypothesis]
---

Tests mixing `@given` (hypothesis) and `@pytest.mark.asyncio` have improper marker interaction. Rather than fixing individual test markers, disable the pytest-asyncio plugin globally via `pytest.ini` with `addopts = -p no:asyncio`. This resolves marker conflicts without test code changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
