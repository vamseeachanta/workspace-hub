---
name: crossprovider gemini standards-document-summarization-schema
description: Standards document summarization schema
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [standards-ingestion, metadata-schema, documentation]
---

Engineering standard ingestion follows a consistent metadata template: title, org, doc_number, summary (3-4 sentences), discipline (enum: structural|cathodic-protection|pipeline|marine|installation|energy-economics|materials|regulatory|drilling|other), keywords, target_repos, and key_clauses. Used across API and DNV standard processing tasks to normalize document intake for downstream repo assignment.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
