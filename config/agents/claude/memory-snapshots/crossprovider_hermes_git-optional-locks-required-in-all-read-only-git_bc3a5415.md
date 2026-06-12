---
name: crossprovider hermes git-optional-locks-required-in-all-read-only-git
description: GIT_OPTIONAL_LOCKS required in all read-only git probe paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-safety, read-only-scope, optional-locks]
---

Any script calling `git status`, `git rev-parse`, `git rev-list` read-only must set `GIT_OPTIONAL_LOCKS=0`; not just one place but consistently across all read-only scope paths. Protects against index-refresh mutations during probes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
