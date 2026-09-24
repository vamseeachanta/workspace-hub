---
name: crossprovider codex multi-backend-extension-without-upfront-identifi
description: Multi-backend extension without upfront identification causes silent failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [backend-design, multi-component, silent-failure-hazard]
---

When adding metadata, tracking, or features to a result carrier or output structure, identify and extend ALL backends/implementations that emit similar results (e.g., both OrcaWave and AQWA runners, not just one). Partial extension causes silent failures where one backend drops the metadata or feature without raising an error.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
