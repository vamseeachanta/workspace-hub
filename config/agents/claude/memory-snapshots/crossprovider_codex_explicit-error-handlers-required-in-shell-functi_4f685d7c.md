---
name: crossprovider codex explicit-error-handlers-required-in-shell-functi
description: Explicit error handlers required in shell functions under set -euo pipefail
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-pipefail, set-e, error-handling, robustness]
---

Functions executing under `set -euo pipefail` must explicitly swallow errors in substitutions with `cmd 2>/dev/null || var=""` or similar. Omitting the handler risks silent failure when the function is called at top level: empty output doesn't trigger set -e, but unguarded `$()` substitution failure can blank downstream state. Critical for statusline/UI scripts where failure = invisibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
