---
name: crossprovider hermes codex-cli-version-conflicts-with-gpt-5-5-provide
description: Codex CLI version conflicts with gpt-5.5 provider
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex, provider-delegation, version-compatibility]
---

Codex pinned to v0.123.0 does not support gpt-5.5 delegation; downgrading doesn't fix the mismatch. When reconfiguring Codex to use gpt-5.5, upgrade the CLI to a newer version that supports the provider routing. This is a tooling constraint not obvious from error messages.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
