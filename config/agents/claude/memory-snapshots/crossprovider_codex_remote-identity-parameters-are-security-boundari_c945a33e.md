---
name: crossprovider codex remote-identity-parameters-are-security-boundari
description: Remote identity parameters are security boundaries requiring runtime validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, identity-validation, parameter-injection]
---

A parameter like `--machine` that specifies which host's config to manage can inject one host's schedule into another locally if not validated. Validation must occur at every entrypoint (wrapper and CLI), comparing requested identity to runtime hostname, not just accepting it passthrough.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
