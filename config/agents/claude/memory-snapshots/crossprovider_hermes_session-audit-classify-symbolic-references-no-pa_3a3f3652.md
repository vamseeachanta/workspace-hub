---
name: crossprovider hermes session-audit-classify-symbolic-references-no-pa
description: Session audit: classify symbolic references (no path separators) separately from missing files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, multi-provider, classification]
---

In multi-provider audits, tool/file references without path separators (e.g., 'skill_name', 'session_history') are likely symbolic reads, not missing files. Classifying them as missing_file generates false positives. Infer from context: if no '/' or '.', mark as 'symbolic_reference' or provider-specific category (e.g., Hermes 'session_search' references). Reduces audit noise.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
