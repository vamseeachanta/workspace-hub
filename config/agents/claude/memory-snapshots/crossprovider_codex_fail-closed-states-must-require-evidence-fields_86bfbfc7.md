---
name: crossprovider codex fail-closed-states-must-require-evidence-fields
description: Fail-closed states must require evidence fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, fail-closed-design, manifest]
---

Manifest rows with 'blocked', 'gated', 'manual', 'deferred' status must carry evidence fields (e.g., `blocker_or_manual_notes`) that are required and non-empty. Validation must enforce this; normal rows can omit evidence, but fail-closed states cannot skip explanation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
