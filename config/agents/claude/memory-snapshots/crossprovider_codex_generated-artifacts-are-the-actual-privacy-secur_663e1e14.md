---
name: crossprovider codex generated-artifacts-are-the-actual-privacy-secur
description: Generated artifacts are the actual privacy/security surface when checked-in
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [privacy-leaks, artifact-verification, generated-content]
---

Code-stage review must inspect checked-in generated JSON/JSONL/HTML outputs, not just the code producing them. Generated extensions like `.20250805-204115` and `.backup-20251023-081047` leaked through extension_mix despite code appearing safe. Artifact review is mandatory when outputs are tracked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
