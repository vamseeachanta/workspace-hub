---
name: crossprovider codex legacy-report-preservation-leakage-exemption-sco
description: Legacy report preservation ≠ leakage exemption; scope strict scans to new artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [privacy, proof-safety, scope-isolation]
---

Historical metadata reports can legitimately contain 16-char signatures, label tokens, or `delete_manifest` fields. Preserving them for audit does not exempt them from privacy review—it shifts the scanning boundary. New/modified proof artifacts require stricter scanning; legacy reports are kept as-is but isolated from public outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
