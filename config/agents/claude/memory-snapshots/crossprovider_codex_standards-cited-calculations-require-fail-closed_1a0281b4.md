---
name: crossprovider codex standards-cited-calculations-require-fail-closed
description: Standards-cited calculations require fail-closed gates and sidecars
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [engineering-calculations, standards, provenance]
---

When a calculation uses licensed/external standards (OCIMF MEG3/MEG4, AISC, etc.), the implementation must: (1) name the licensed source explicitly, (2) emit a citation sidecar tied to provenance, (3) state the limitation (reference/generic, not ship-specific), (4) fail closed if source unavailable. Silent fallback to placeholder coefficients is unacceptable. #2760 required explicit OCIMF workbook path + citation contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
