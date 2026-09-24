---
name: crossprovider codex cron-installer-implementations-diverge-on-enviro
description: Cron installer implementations diverge on environment handling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron-architecture, installer-divergence, workspace-hub]
---

The workspace-hub cron subsystem has three independent implementations (setup-cron.sh, cron_apply.py, cron_transaction.py) that handle environment variables, command rendering, machine token resolution, and variable expansion inconsistently. Legacy emits two-space separators; transactional uses one. Machine resolution pins to canonical registry keys while legacy uses hostname/alias tokens. These divergences break byte-parity tests and allow uncataloged variables to pass validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
