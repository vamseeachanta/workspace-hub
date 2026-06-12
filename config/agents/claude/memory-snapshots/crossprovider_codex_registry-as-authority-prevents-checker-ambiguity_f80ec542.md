---
name: crossprovider codex registry-as-authority-prevents-checker-ambiguity
description: Registry as authority prevents checker ambiguity
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, registry, single-source-of-truth]
---

Readiness and validation tools should read from a single registry authority (e.g., `config/workstations/registry.yaml`) rather than creating parallel discovery mechanisms. This prevents checkers from silently diverging from the source of truth. #2766 emphasized `telegram_hermes_readiness.py --registry` pattern and forbade new top-level state keys.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
