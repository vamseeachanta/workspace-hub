---
name: crossprovider gemini three-phase-ecosystem-change-pattern
description: Three-phase ecosystem change pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [governance, ecosystem, change-management, schema-enforcement]
---

For centralizing scattered state (specs, work items) across repos: Phase 1 adds hygiene gates (validation scripts, CI warnings), Phase 2 runs pilot migrations on subset with dry-run manifests + checksums, Phase 3 switches CI to blocking mode. Avoids big-bang migration disasters; gates catch issues early, pilots build confidence, enforcement is gradual.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
