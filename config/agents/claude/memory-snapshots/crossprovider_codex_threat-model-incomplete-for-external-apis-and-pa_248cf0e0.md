---
name: crossprovider codex threat-model-incomplete-for-external-apis-and-pa
description: Threat model incomplete for external APIs and path handling
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, threat-model, external-api]
---

Threat models skip or minimize risks for path traversal (symlinks, mount substitution), external API leakage (provider rate limits, prompt injection, data leakage to third-party embeddings), and subprocess boundaries (secrets in stderr, auth token lifetime). For code touching paths or external services, expand threat model explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
