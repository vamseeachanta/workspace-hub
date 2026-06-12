---
name: crossprovider hermes mnt-ace-data-is-a-backwards-compatibility-alias-
description: /mnt/ace-data is a backwards-compatibility alias—reference canonical /mnt/ace
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [mount-paths, data-residency, migration-patterns]
---

/mnt/ace-data is a symlink to /mnt/ace for backwards compatibility only. New code must reference /mnt/ace as the canonical path; cleanup of the alias requires a separate GitHub issue + verification of all consumer migrations. Never treat /mnt/ace-data as a distinct storage root.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
