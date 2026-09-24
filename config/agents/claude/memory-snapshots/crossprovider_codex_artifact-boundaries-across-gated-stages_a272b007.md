---
name: crossprovider codex artifact-boundaries-across-gated-stages
description: Artifact boundaries across gated stages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, decoupling, boundaries, licensing]
---

When splitting a pipeline across licensing or environment gates, communicate via files and serialized artifacts rather than shared live API objects. This allows license-free stages to run independently without transitive imports or dependency on the gated library.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
