---
name: crossprovider codex environment-based-work-filtering-identifies-lice
description: Environment-based work filtering identifies license and external dependency blocks
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [work-queue, environment, dependencies, filtering]
---

WRK-149/WRK-157 execution queue depends on OrcaFlex/OrcaWave availability, but queue state doesn't track blocking dependencies. Metadata (license_required, external_tools, environment_flags) per WRK + pre-execution environment scan separates executable-now work from blocked items without manual filtering.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
