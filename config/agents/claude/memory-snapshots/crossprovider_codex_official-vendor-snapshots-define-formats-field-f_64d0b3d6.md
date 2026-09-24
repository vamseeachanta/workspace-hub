---
name: crossprovider codex official-vendor-snapshots-define-formats-field-f
description: Official vendor snapshots define formats; field-format assumptions are dangerous
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-loss, vendor-integration, testing]
---

Vendor data (e.g., RRC snapshots with 8-digit API numbers without Texas prefix) may not match normalizer assumptions about 'stable format'. Normalizers that only accept prefixed APIs silently drop official data. Probe with real vendor manuals and examples before claiming format is stable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
