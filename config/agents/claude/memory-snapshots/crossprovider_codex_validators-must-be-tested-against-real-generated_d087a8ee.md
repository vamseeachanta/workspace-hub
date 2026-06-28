---
name: crossprovider codex validators-must-be-tested-against-real-generated
description: Validators must be tested against real generated artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-25
  tags: [validation, testing, privacy, adversarial]
---

Passing tests do not prove a validator catches real leaks. Session #790 diff review found that generated JSON contained source-identity bucket names and the public-surface scanner did not reject them, despite earlier passing test runs. Validators must be executed against actual artifact output before shipping privacy-gated code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
