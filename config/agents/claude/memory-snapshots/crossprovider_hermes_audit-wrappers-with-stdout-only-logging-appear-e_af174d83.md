---
name: crossprovider hermes audit-wrappers-with-stdout-only-logging-appear-e
description: Audit wrappers with stdout-only logging appear empty on success
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [logging, wrapper-design]
---

Provider-session audit empty because wrapper captures only Python stdout; no output ≠ healthy. Wrappers should log explicit summary counts or status codes, never rely on silence as signal.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
