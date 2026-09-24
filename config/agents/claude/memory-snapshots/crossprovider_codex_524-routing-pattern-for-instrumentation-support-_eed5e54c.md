---
name: crossprovider codex 524-routing-pattern-for-instrumentation-support-
description: #524 routing pattern for instrumentation/support work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [patterns, routing, test-assertion, safety-checks]
---

Use importable builder pattern with fail-closed drift checks before writing output; assert exact manifest row identities and constants (source_role, scope_class, license_policy, extraction_status, page_disposition); include forbidden-marker safety list (paths, source filenames, purchaser/order/email/watermark markers) and validate absence in generated artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
