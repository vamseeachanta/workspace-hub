---
name: crossprovider gemini migration-tooling-must-include-dry-run-mode-for-
description: Migration tooling must include dry-run mode for verification
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-migration, verification, operational-safety]
---

Before destructive operations (line evictions, file reorganizations, data moves), provide `--dry-run` flag to preview changes safely. Allows verification that correct entries are moved/evicted before committing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
