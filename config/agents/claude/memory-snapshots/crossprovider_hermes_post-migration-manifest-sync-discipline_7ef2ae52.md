---
name: crossprovider hermes post-migration-manifest-sync-discipline
description: Post-migration manifest sync discipline
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [operations, data-migration, manifest, verification]
---

After data moves (e.g., rsync org directories), always verify file counts match source, then update dependent manifest files (assets.json via build-manifest.py, README metadata). Automation (e.g., build-manifest.py rebuild) prevents human error and keeps documentation in sync with filesystem state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
