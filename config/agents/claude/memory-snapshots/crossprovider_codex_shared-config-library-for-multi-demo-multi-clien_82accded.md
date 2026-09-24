---
name: crossprovider codex shared-config-library-for-multi-demo-multi-clien
description: Shared config library for multi-demo/multi-client projects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, config-scaling, multi-demo-projects, source-of-truth]
---

Per-demo cloned constants don't scale across multiple analyses or clients. Move shared materials, codes, safety classes, catalog paths, and physical constants into centralized `config/*.yml` files. Each demo references config IDs and declares sweep axes in `inputs/demo_0N_*.yml`. Avoids drift and makes constants auditable cross-project.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
