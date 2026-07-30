---
name: crossprovider codex validators-must-delegate-gate-checking-to-upstre
description: Validators must delegate gate-checking to upstream trust boundaries, not re-implement
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [validation, security, delegation]
---

Validators claiming 'public-approved' or 'sampling-authorized' output should not re-implement those gates; they should call upstream gatekeeping systems (e.g., firewalls, trust registries). Self-attested evidence fails security review and creates false confidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
