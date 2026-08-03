---
name: crossprovider codex pytest-initialization-can-block-on-unrelated-thi
description: pytest initialization can block on unrelated third-party metadata in shared environments
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [pytest, environment-quirk, shared-venv]
---

Broken package metadata (e.g., vtk) can prevent pytest startup even when unused. Disable autoload or specific broken plugins (`pytest -p no:cacheprovider`) to restore speed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
