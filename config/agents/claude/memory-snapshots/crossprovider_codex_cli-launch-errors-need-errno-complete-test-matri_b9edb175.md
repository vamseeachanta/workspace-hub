---
name: crossprovider codex cli-launch-errors-need-errno-complete-test-matri
description: CLI launch errors need errno-complete test matrices
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, cli, error-codes]
---

Error handling for pre-child failures must prove: ENOENT→127, all other launch errors→126, SIGINT→130, with explicit redaction for every family. Single generic catch-all hides errno-specific behavior; TDD matrices surface it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
