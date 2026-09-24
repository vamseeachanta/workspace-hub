---
name: crossprovider codex path-scanning-validators-enforce-repo-local-secu
description: Path scanning validators enforce repo-local security boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scanning, security, validators]
---

Scanner CLIs (legal-sanity-scan.py, public-surface-scan.py) reject absolute paths outside the repository tree (e.g., `/tmp/...` or `/home/...`). Plans that reference temp files or out-of-repo paths for scanning must either snapshot to a repo-local path or revise the scan strategy. This is a hard security boundary in the validators, not a quirk.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
