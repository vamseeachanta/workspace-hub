---
name: crossprovider codex explicit-resource-paths-must-fail-hard-not-soft
description: Explicit resource paths must fail hard, not soft
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration, error-handling, operational-safety]
---

Explicit config values referencing missing resources (REGISTRY_PATH=/missing, CONFIG=/typo) must error nonzero, not warn-skip. Silent success masks typos and creates operational blindness. Warn-skip applies only to implicit or optional discovery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
