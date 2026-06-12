---
name: crossprovider codex client-private-routing-must-check-config-client-
description: Client-private routing must check config/client-wikis.yml registry, not directory structure
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [client-routing, firewall, llm-wiki]
---

Classification of client-private vs generic content must verify the actual `config/client-wikis.yml` registry. Absence from registry = fail-closed to private-issue routing, not generic-ingest assumption. Directory names and folder structure alone are not authoritative.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
