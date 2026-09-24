---
name: crossprovider codex private-data-validation-requires-targeted-checks
description: Private-data validation requires targeted checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, validation, scanning, private-data]
---

Full-file legal scans are noisy on baseline or insufficient when diff-only. For private-data validation, use targeted pattern checks tied to the data flow: check for both generic `/mnt/ace` paths AND secret forms (`password=`, `Bearer`, `/home/...`) specific to your data structure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
