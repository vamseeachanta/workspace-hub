---
name: crossprovider gemini shell-script-pattern-for-scripts-security
description: Shell script pattern for scripts/security/
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [scripting-conventions, scripts-directory]
---

Workspace scripts in `scripts/security/` follow an established pattern: `set -euo pipefail`, SCRIPT_DIR extraction via `cd "$(dirname "${BASH_SOURCE[0]}")" && pwd`, REPO_ROOT reference, structured header comments, CLI arg parsing (e.g., `--repo`), and explicit exit 0/1 codes. This pattern is demonstrated by `secrets-scan.sh` and should be replicated for new utility scripts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
