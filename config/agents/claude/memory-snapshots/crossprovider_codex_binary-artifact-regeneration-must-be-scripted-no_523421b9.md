---
name: crossprovider codex binary-artifact-regeneration-must-be-scripted-no
description: Binary artifact regeneration must be scripted, not one-shot ad-hoc
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, reproducibility, artifact-generation]
---

Plans that render PDFs, binaries, or other generated artifacts via one-shot commands ('Chrome headless invocation, not a new script') cannot be regenerated deterministically. Commit a `scripts/gtm/render-capability-summary-pdf.sh` with shebang, `set -euo pipefail`, Chrome version assertion, and sidecar .meta emission (chrome_version, git_sha, timestamp, output_pdf_sha256). Otherwise future regeneration will not match.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
