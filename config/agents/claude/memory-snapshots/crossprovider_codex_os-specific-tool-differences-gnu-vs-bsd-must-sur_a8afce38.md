---
name: crossprovider codex os-specific-tool-differences-gnu-vs-bsd-must-sur
description: OS-specific tool differences (GNU vs BSD) must surface in readiness planning, not defer to implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [portability, os-compatibility, readiness-testing]
---

sed -i, hostname -s, stat -c behave differently on macOS (BSD) vs Linux — these surface in readiness scripts (nightly-readiness.sh) and can't be patched later. Plans must identify which scripts use OS-sensitive commands and either restrict scope or commit to cross-platform fixes upfront.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
