---
name: crossprovider hermes filesystem-path-validation-gap-source-doc-key-sc
description: Filesystem path validation gap: source_doc_key schema accepts raw paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, schema-validation, privacy]
---

Schema accepts source_doc_key as bare string type, allowing `/home/user/client/secret.docx` or other sensitive paths. Fail-closed: enforce safe format like `source-doc-key:corpus:category:id` via regex pattern constraint, or reject paths starting with `/` and common sensitive prefixes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
