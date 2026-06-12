---
name: crossprovider hermes download-helpers-shell-pattern-set-uo-pipefail-n
description: Download-helpers shell pattern — set -uo pipefail, not set -e
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-patterns, error-handling, download-scripts, best-practice]
---

Scripts sourcing download-helpers.sh must use `set -uo pipefail` (without `-e`) because the `download()` function returns 1 on failure. With `set -e`, any failed download aborts the entire script unless guarded by `|| true`. This is the established pattern across 6 download scripts (subsea, structural, pipeline, geotechnical, cathodic-protection, naval-architecture).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
