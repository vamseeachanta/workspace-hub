---
name: crossprovider codex validation-rules-must-be-structurally-independen
description: Validation rules must be structurally independent
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [testing, validation, qa]
---

Checking two quantities derived from the same parameter (e.g., both GM and C44 derived from mass/volume) as separate validation rules creates false confidence; failure in one should invalidate both. Validation inputs should come from independent sources or be explicitly acknowledged as coupled.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
