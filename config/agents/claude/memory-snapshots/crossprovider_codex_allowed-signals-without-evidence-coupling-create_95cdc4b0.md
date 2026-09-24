---
name: crossprovider codex allowed-signals-without-evidence-coupling-create
description: Allowed signals without evidence coupling create fail-open paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, fail-closed, gates, authorization]
---

Classifier functions returning allowed=True without tracing to validated evidence create silent authorization. Every allow path must be explicitly coupled to an evidence reference; bare allow signals are a class of security defect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
