---
name: crossprovider codex report-design-self-contained-public-artifact-pro
description: Report design: self-contained public artifact + provenance sidecar
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-design, provenance, report-architecture]
---

Issue #810: HTML embeds all data inline for static publishing; JSON sidecar captures source URL, timestamp, row counts for downstream use. Split public (immutable HTML) from durable provenance (JSON).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
