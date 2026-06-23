---
name: crossprovider codex use-opaque-handles-instead-of-raw-source-labels-
description: Use opaque handles instead of raw source labels in sensitive GitHub artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [privacy, governance, data-safety, GitHub]
---

When outputting source-label data to GitHub artifacts (comments, reports, pages), use opaque identifiers or `source_root_label` + digest instead of exact labels containing directory/filename fragments. Precedent conflicts between privacy lanes suggest explicit choice of the stricter pattern in plans.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
