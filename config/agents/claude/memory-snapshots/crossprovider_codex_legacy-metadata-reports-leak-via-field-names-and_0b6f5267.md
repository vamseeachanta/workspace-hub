---
name: crossprovider codex legacy-metadata-reports-leak-via-field-names-and
description: Legacy metadata reports leak via field names and structures; active scanning required when extending
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-gates, legacy-code, code-extension]
---

Session 5 noted that extending a metadata-only archive tool for privacy gates required active regex/content scanning, not trust in prior leak detection. The old report still had `delete_manifest` field (false-valued) and `archive_label` tokens that could appear in new output. When inheriting code, audit field names and structure intentionally, not just presence-of-secrets patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
