---
name: crossprovider codex established-shell-script-structure-pattern
description: Established shell script structure pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [script-pattern, code-convention, ops]
---

Infrastructure scripts in this repo follow the pattern from `scripts/security/secrets-scan.sh`: `set -euo pipefail`, SCRIPT_DIR calculation, REPO_ROOT reference, CLI arg parsing (e.g., --repo), structured header comments, and exit 0/1 status. New security/ops scripts should replicate this convention.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
