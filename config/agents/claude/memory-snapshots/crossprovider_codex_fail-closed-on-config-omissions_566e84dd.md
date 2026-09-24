---
name: crossprovider codex fail-closed-on-config-omissions
description: Fail-closed on config omissions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config, error-handling, safety]
---

Treating null or missing config values as defaults (e.g., `ssh_target: null` → local execution) creates silent false positives. Error explicitly on incomplete configuration instead, making config gaps immediately visible.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
