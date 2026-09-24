---
name: crossprovider codex licensed-solver-open-publication-workflow-route-
description: Licensed-solver + open-publication workflow: route to licensed worker, return de-identified results
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, licensed-software, data-workflows, vercel-patterns]
---

For Windows-licensed tools (e.g., OrcaFlex) orchestrated from Linux: bundle deterministic inputs, route to a licensed worker for execution, bring back only de-identified inputs and results for verification and public publishing. This separates licensing liability from data availability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
