---
name: crossprovider hermes dual-git-lock-hardening-for-read-only-probes
description: Dual Git lock hardening for read-only probes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-concurrency, read-only-safety, env-flags]
---

Use both `GIT_OPTIONAL_LOCKS=0` environment variable AND `git --no-optional-locks` flag together for robustness in concurrent read-only Git operations (status, rev-parse, rev-list). Single-method approach can still block under load. Validated pattern in workspace-hub tier-1 checker.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
