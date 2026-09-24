---
name: crossprovider codex reproducing-corpus-wide-validation-with-environm
description: Reproducing corpus-wide validation with environment paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment-variables, corpus-validation, diagnostic-path]
---

Corpus-dependent validators require explicit `FDAS_CORPUS` and `UV_CACHE_DIR` environment variables; failures without these are non-diagnostic. Rerun with full environment after confirming the paths before deciding verdict.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
