---
name: crossprovider codex windows-dispatch-wrapper-has-persistence-linux-d
description: Windows dispatch wrapper has persistence; Linux does not
metadata:
  type: reference
  source: codex
  bridged: 2026-08-01
  tags: [dispatch, cross-platform, infrastructure-parity]
---

dispatch-run.ps1 (Windows Scheduled Task) survives session close; Linux equivalent is missing entirely. This asymmetry makes Linux dispatch unobservable and non-adoption of the wrapper becomes silent-by-default. Requires explicit cross-platform feature parity or enforcement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
