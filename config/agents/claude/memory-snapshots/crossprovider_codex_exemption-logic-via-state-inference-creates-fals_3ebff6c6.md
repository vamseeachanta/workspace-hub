---
name: crossprovider codex exemption-logic-via-state-inference-creates-fals
description: Exemption logic via state inference creates false passes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, exemptions, state-inference, toctou]
---

Using inferred state (e.g., 'logs/ dir present means legacy') to detect exemption conditions allows new work with failed enforcement to slip through unchanged. Exemption gates should use explicit metadata (creation date, schema version, archived marker) not presence/absence of artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
