---
name: crossprovider codex path-collision-detection-must-compare-against-al
description: Path collision detection must compare against all canonical outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-safety, cli-validation, test-coverage]
---

CLI validation that only rejects dangerous directories (e.g., /tmp) is insufficient; it must actively reject routing-ledger or human-disposition inputs that resolve to any canonical output path. Test must exercise the full input/output space, including data/document-index sources that are both valid inputs and potential outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
