---
name: crossprovider codex registry-dependent-privacy-scans-fail-silently-w
description: Registry-dependent privacy scans fail silently when unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [privacy, registries, single-source-of-truth]
---

Privacy verification that sources known-values (e.g., mkt-a hostnames) from a private registry cannot operate if the registry is offline, stale, or inaccessible. The scan is only as strong as the registry's availability and freshness. Plan must address what happens when the private source is unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
