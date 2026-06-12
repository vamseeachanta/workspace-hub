---
name: crossprovider hermes gui-verification-cannot-be-inferred-from-registr
description: GUI verification cannot be inferred from registry facts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [windows-machines, verification, evidence-gates]
---

Windows machine readiness inferred from registry/SSH facts (hostname, branch, remote) misses physical state (license availability, scheduler status, dirty files, task manager). GUI-side evidence packet is blocking dependency: capture actual checkout paths, tool availability, license state before declaring operational readiness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
