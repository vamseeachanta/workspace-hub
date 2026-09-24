---
name: crossprovider codex non-ssh-evidence-interfaces-require-explicit-des
description: Non-SSH evidence interfaces require explicit design in cross-machine automation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [distributed-systems, evidence-collection, windows-integration]
---

Windows machines and special-access hosts can't be probed via SSH. Plans for parity/readiness automation must explicitly map each machine to an evidence source: direct SSH, bridge artifacts, readiness config static data, or 'blocked-no-interface'. Leaving this implicit causes silent failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
