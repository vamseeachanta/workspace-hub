---
name: crossprovider codex crontab-transactions-require-explicit-marker-spe
description: Crontab transactions require explicit marker spec and stable identity matching
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [crontab-safety, marker-parsing, external-ownership]
---

Marker-block parsing must define behavior for no markers, malformed markers, env lines (MAILTO/SHELL/PATH), and duplicates. Preserved-external lines must use stable fingerprints (path patterns, command-hash) that handle variation (wrappers, env prefixes, log redirects). Require tests for each anomaly and variant case.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
