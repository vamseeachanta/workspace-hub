---
name: crossprovider codex privacy-plans-need-filesystem-access-monkeypatch
description: Privacy plans need filesystem-access monkeypatch tests
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [privacy, governance, testing, verification, correctness]
---

Plans proposing raw-source read prohibitions must include tests that monkeypatch filesystem operations (`Path.open`, `builtins.open`, `subprocess.run`, and resolver libraries) to enforce the prohibition. Absence of these tests means safety claims are untested and the plan's correctness-critical assertions remain unverified.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
