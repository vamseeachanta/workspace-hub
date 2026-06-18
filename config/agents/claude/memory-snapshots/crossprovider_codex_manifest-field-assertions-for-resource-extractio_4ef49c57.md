---
name: crossprovider codex manifest-field-assertions-for-resource-extractio
description: Manifest field assertions for resource-extraction tests (electrical-canary pattern)
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [testing, extraction, manifest-validation, safety, electrical]
---

Assert exact manifest fields before extraction: source_root_label, publisher, source_kind, visibility, owning_issue, extraction_status, page_disposition, scope_class, license_policy. Check forbidden-output markers (/mnt/, /home/, source_pdf, source_path, .pdf, purchaser, watermark, order id, etc.) to detect source-path leakage. Locked parent rows remain metadata-only; support-reference rows stay reference-metadata-only, never generate standard pages/datasets.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
