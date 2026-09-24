---
name: crossprovider codex guard-coverage-must-include-all-read-identifiers
description: Guard coverage must include all read identifiers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, data-safety, configuration]
---

Metadata-only and forbidden-content guards must filter across all read identifiers (primary key, canonical path, and metadata columns), not just explicit metadata slots. Primary-key and path configurations are attack surfaces if excluded from forbidden-token filtering.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
