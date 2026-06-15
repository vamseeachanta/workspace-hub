---
name: crossprovider codex generated-reports-must-sanitize-sensitive-labels
description: Generated reports must sanitize sensitive labels and preserve provenance safely
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [generated-reports, sanitization, provenance]
---

Output JSON/HTML must alias private labels (e.g. `private-llm-wiki` → `private-metadata-only`) before emission; never leak labels that reveal corpus categorization. Row provenance must include a `safe_source_root_label` field (safe alias, not mount path). Retrieval evidence should carry `status_code`, `retrieved_date`, `content_digest` for auditability and anti-spoofing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
