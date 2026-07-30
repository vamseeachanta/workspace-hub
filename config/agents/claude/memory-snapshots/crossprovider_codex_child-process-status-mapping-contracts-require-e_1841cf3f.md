---
name: crossprovider codex child-process-status-mapping-contracts-require-e
description: Child process status mapping contracts require explicit non-SIGINT regression coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [testing, process-lifecycle, regression-coverage]
---

Signal handling in child process exit codes is easy to over-generalize: mapping only SIGINT to 130 while preserving all other negative child statuses unchanged requires regression tests that explicitly exercise non-SIGINT cases (e.g., SIGTERM returning −15, not 143). Tests covering only SIGINT and ordinary exits will miss violations of the 'all other statuses unchanged' contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
