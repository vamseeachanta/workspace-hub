---
name: crossprovider codex audit-lockfiles-via-pinned-exports-e-g-uv-export
description: Audit lockfiles via pinned exports (e.g., uv export --frozen), not installed environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependency-audit, lockfile-scanning, environment-divergence]
---

When auditing dependency lockfiles for CVEs, audit the declared pins using `uv export --frozen --no-dev` piped to pip-audit, not the installed environment. This catches lock/environment divergence and accurately reflects what is pinned, not what happened to get installed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
