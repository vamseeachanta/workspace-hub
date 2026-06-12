---
name: crossprovider hermes machine-config-schema-requires-tier1-repo-root-w
description: Machine config schema requires tier1_repo_root when repos list is non-empty
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-validation, machine-config, required-fields, repo-root]
---

Schema validation should enforce that machines with a non-empty `repos` list must define `tier1_repo_root` (e.g., Linux primary `/mnt/local-analysis`, secondary `/mnt/dde`). Prevents incomplete machine configs where repo declarations lack placement authority.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
