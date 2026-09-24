---
name: crossprovider codex remediation-paths-must-mirror-discovery-audit-pa
description: Remediation paths must mirror discovery/audit paths exactly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [remediation, ssh, parity, execution-semantics]
---

If an audit uses SSH alias-then-tailscale fallback, remediation must use the same strategy. If audit measures `python --version` in cron shells, remediation must ensure plain `python` resolves to the new version in non-interactive shells (requires PATH/symlink validation, not just package installation).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
