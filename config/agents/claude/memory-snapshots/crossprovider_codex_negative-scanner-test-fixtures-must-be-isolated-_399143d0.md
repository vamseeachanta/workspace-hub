---
name: crossprovider codex negative-scanner-test-fixtures-must-be-isolated-
description: Negative scanner test fixtures must be isolated from public scan paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, security-scanning, public-scan]
---

Test files containing scan-hostile patterns (traversal commands, digest values, private identifiers) will fail public scanning if the test file itself is included. Isolate negative-scanner test modules outside public scan scope or use explicit allowlists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
