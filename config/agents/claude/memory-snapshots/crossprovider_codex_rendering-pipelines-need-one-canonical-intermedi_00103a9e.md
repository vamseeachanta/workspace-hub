---
name: crossprovider codex rendering-pipelines-need-one-canonical-intermedi
description: Rendering pipelines need one canonical intermediate representation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, html-generation, rendering]
---

When building HTML/Markdown generation pipelines, avoid separate renderers for each format—they diverge in structure and semantics over time. Instead, render once to a canonical intermediate model (AST, dataclass, or JSON), then project both output formats from that shared representation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
