---
name: crossprovider hermes download-scripts-use-set-uo-pipefail-not-set-e
description: Download scripts use set -uo pipefail, not set -e
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scripting, reliability, download, best-practice]
---

The `set -e` pattern identified as dangerous for download-helpers.sh style scripts; `set -uo pipefail` is safer and resume-safe for resumable downloads. Don't propagate `set -e` to download libraries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
