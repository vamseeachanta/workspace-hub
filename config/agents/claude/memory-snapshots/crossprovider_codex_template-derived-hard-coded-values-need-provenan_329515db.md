---
name: crossprovider codex template-derived-hard-coded-values-need-provenan
description: Template-derived hard-coded values need provenance metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [conversion-logic, metadata, provenance]
---

When conversion logic inherits hard-coded values from existing templates (bend curvature signs, mesh segment sizes), these should be explicitly marked in output metadata as 'template-derived' or 'provisional' with tests verifying the metadata marking, not just the numeric output. Without this, future maintainers cannot distinguish engineering-sourced from template-borrowed values.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
