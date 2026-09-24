---
name: crossprovider codex use-purpose-built-json-drivers-instead-of-ad-hoc
description: Use purpose-built JSON drivers instead of ad-hoc git parsing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-pattern, architectural-decision]
---

Ecosystem workflows provide JSON-output drivers (e.g., scripts/readiness/reconcile-ecosystem.sh) designed for filtering. Parsing ad-hoc git status/diff output is slower and noisier. Query the JSON driver and filter locally with jq when a workflow script exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
