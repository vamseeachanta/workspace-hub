---
name: crossprovider hermes legal-scan-tool-empty-output-can-mask-execution-
description: Legal scan tool empty output can mask execution failure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tooling-pitfall, legal-scanning, automation-testing]
---

Tools like `scripts/legal/legal-sanity-scan.sh --all --json` may return exit code 0 with zero bytes output, appearing successful while having scanned nothing. Validate output size > 0 before trusting results; empty JSON output is a failure signature masking missing file coverage or incomplete scans.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
