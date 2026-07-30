---
name: crossprovider codex caller-selected-registry-paths-enable-authority-
description: Caller-selected registry paths enable authority fabrication
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, api-design, authority-binding]
---

If public APIs accept a caller-supplied registry path or configuration file path, an attacker can craft a fake schema file granting arbitrary roots and permissions unless the implementation binds the parameter to a canonical trusted source. Validate and lock the authority source at the descriptor level.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
