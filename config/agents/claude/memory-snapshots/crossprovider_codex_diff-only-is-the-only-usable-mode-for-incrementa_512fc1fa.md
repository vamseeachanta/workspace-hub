---
name: crossprovider codex diff-only-is-the-only-usable-mode-for-incrementa
description: --diff-only is the only usable mode for incremental legal scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [legal-gate, performance, issue-259, issue-260]
---

Running a full legal scan on repos with extensive tracked private paths (/mnt/ace/...) floods with pre-existing violations. Issues #259/#260: full scan had to be killed after 30s on 400+ pre-tracked paths. Reserve full scans to CI/setup; use --diff-only for incremental checks and reviews.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
